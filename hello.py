#!/usr/bin/env python3
"""
WAF & DNS Inventory Report

Outputs:
  - waf_protected_endpoints.csv
  - domains_without_waf.csv

What it does:
  1. Lists all WAFv2 WebACLs (REGIONAL in all regions + CLOUDFRONT scope).
  2. For each WebACL, finds attached resources:
       - APPLICATION_LOAD_BALANCER
       - CLOUDFRONT distributions
  3. For each resource, finds its frontend DNS name.
  4. Lists all Route 53 hosted zones & records (A / AAAA / CNAME / ALIAS).
  5. Maps WAF-protected resources to domains.
  6. Finds domains pointing to ALB / CF that are NOT behind any WAF.
"""

import boto3
import botocore
import csv
import re
from typing import Dict, List, Tuple, Any

# -------- Helpers --------

def get_account_id() -> str:
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def get_all_regions() -> List[str]:
    ec2 = boto3.client("ec2")
    resp = ec2.describe_regions(AllRegions=False)
    return [r["RegionName"] for r in resp["Regions"]]


def paginate(method, result_key: str, **kwargs):
    """
    Generic paginator for AWS APIs that use NextToken/NextMarker/etc.
    """
    token_keys = ["NextToken", "NextMarker", "Marker"]
    while True:
        resp = method(**kwargs)
        # yield items
        data = resp
        for part in result_key.split("."):
            data = data.get(part, [])
        for item in data:
            yield item

        # find token
        next_token = None
        for tk in token_keys:
            if tk in resp:
                next_token = resp[tk]
                break

        if not next_token:
            break

        # determine which parameter to use
        if "NextToken" in resp:
            kwargs["NextToken"] = resp["NextToken"]
        elif "NextMarker" in resp:
            kwargs["NextMarker"] = resp["NextMarker"]
        elif "Marker" in resp:
            kwargs["Marker"] = resp["Marker"]


# -------- Step 1: WAF WebACLs --------

def list_waf_web_acls() -> List[Dict[str, Any]]:
    """
    Returns a list of dicts:
      {
        'account_id',
        'scope',           # REGIONAL or CLOUDFRONT
        'region',          # region name or 'us-east-1' for CLOUDFRONT
        'name',
        'id',
        'arn'
      }
    """
    account_id = get_account_id()
    regions = get_all_regions()
    web_acls = []

    # REGIONAL scope
    for region in regions:
        waf = boto3.client("wafv2", region_name=region)
        try:
            for acl in paginate(
                waf.list_web_acls,
                result_key="WebACLs",
                Scope="REGIONAL",
                Limit=100
            ):
                web_acls.append({
                    "account_id": account_id,
                    "scope": "REGIONAL",
                    "region": region,
                    "name": acl["Name"],
                    "id": acl["Id"],
                    "arn": acl["ARN"],
                })
        except botocore.exceptions.ClientError as e:
            # Some regions may not support WAFv2; skip them
            code = e.response.get("Error", {}).get("Code")
            if code not in ("WAFUnavailableEntityException", "AccessDeniedException"):
                print(f"[WARN] Error listing REGIONAL WAFs in {region}: {e}")

    # CLOUDFRONT scope (always us-east-1)
    cf_region = "us-east-1"
    waf_cf = boto3.client("wafv2", region_name=cf_region)
    try:
        for acl in paginate(
            waf_cf.list_web_acls,
            result_key="WebACLs",
            Scope="CLOUDFRONT",
            Limit=100
        ):
            web_acls.append({
                "account_id": account_id,
                "scope": "CLOUDFRONT",
                "region": cf_region,
                "name": acl["Name"],
                "id": acl["Id"],
                "arn": acl["ARN"],
            })
    except botocore.exceptions.ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code not in ("WAFUnavailableEntityException", "AccessDeniedException"):
            print(f"[WARN] Error listing CLOUDFRONT WAFs: {e}")

    return web_acls


# -------- Step 2: WAF -> Resources (ALB, CloudFront) --------

def list_resources_for_web_acl(acl: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    For a given WebACL, return list of resources:
      {
        'account_id', 'scope', 'region',
        'web_acl_name', 'web_acl_arn',
        'resource_type', 'resource_arn', 'resource_dns'
      }
    Currently handles:
      - APPLICATION_LOAD_BALANCER
      - CLOUDFRONT
    """
    account_id = acl["account_id"]
    scope = acl["scope"]
    region = acl["region"]

    waf = boto3.client("wafv2", region_name=region)
    resources = []

    def add_alb_resources():
        try:
            alb_arns = waf.list_resources_for_web_acl(
                WebACLArn=acl["arn"],
                ResourceType="APPLICATION_LOAD_BALANCER",
            ).get("ResourceArns", [])
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code not in ("WAFNonexistentItemException", "WAFUnavailableEntityException"):
                print(f"[WARN] list_resources_for_web_acl ALB failed in {region}: {e}")
            alb_arns = []

        if not alb_arns:
            return

        elbv2 = boto3.client("elbv2", region_name=region)
        for alb_arn in alb_arns:
            try:
                resp = elbv2.describe_load_balancers(LoadBalancerArns=[alb_arn])
                lb = resp["LoadBalancers"][0]
                dns_name = lb["DNSName"]
            except Exception as e:
                print(f"[WARN] describe_load_balancers failed for {alb_arn}: {e}")
                dns_name = ""

            resources.append({
                "account_id": account_id,
                "scope": scope,
                "region": region,
                "web_acl_name": acl["name"],
                "web_acl_arn": acl["arn"],
                "resource_type": "ALB",
                "resource_arn": alb_arn,
                "resource_dns": dns_name,
            })

    def add_cloudfront_resources():
        # Only relevant for CLOUDFRONT scope
        if scope != "CLOUDFRONT":
            return
        try:
            cf_arns = waf.list_resources_for_web_acl(
                WebACLArn=acl["arn"],
                ResourceType="CLOUDFRONT"
            ).get("ResourceArns", [])
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code not in ("WAFNonexistentItemException", "WAFUnavailableEntityException"):
                print(f"[WARN] list_resources_for_web_acl CLOUDFRONT failed: {e}")
            cf_arns = []

        if not cf_arns:
            return

        cf = boto3.client("cloudfront")
        for dist_arn in cf_arns:
            dist_id = dist_arn.split("/")[-1]
            try:
                resp = cf.get_distribution(Id=dist_id)
                dns_name = resp["Distribution"]["DomainName"]
            except Exception as e:
                print(f"[WARN] get_distribution failed for {dist_arn}: {e}")
                dns_name = ""

            resources.append({
                "account_id": account_id,
                "scope": scope,
                "region": region,
                "web_acl_name": acl["name"],
                "web_acl_arn": acl["arn"],
                "resource_type": "CLOUDFRONT",
                "resource_arn": dist_arn,
                "resource_dns": dns_name,
            })

    add_alb_resources()
    add_cloudfront_resources()
    return resources


def collect_all_waf_resources(web_acls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_res = []
    for acl in web_acls:
        res = list_resources_for_web_acl(acl)
        all_res.extend(res)
    return all_res


# -------- Step 3: Route 53 hosted zones & records --------

def list_all_hosted_zones(route53) -> List[Dict[str, Any]]:
    zones = []
    marker = None
    while True:
        args = {}
        if marker:
            args["Marker"] = marker
        resp = route53.list_hosted_zones(**args)
        zones.extend(resp["HostedZones"])
        if not resp.get("IsTruncated"):
            break
        marker = resp["NextMarker"]
    return zones


def list_all_record_sets(route53, hosted_zone_id: str) -> List[Dict[str, Any]]:
    records = []
    start_name = None
    start_type = None
    start_id = None

    while True:
        args = {"HostedZoneId": hosted_zone_id}
        if start_name:
            args["StartRecordName"] = start_name
            args["StartRecordType"] = start_type
            if start_id:
                args["StartRecordIdentifier"] = start_id

        resp = route53.list_resource_record_sets(**args)
        records.extend(resp["ResourceRecordSets"])

        if not resp.get("IsTruncated"):
            break

        start_name = resp["NextRecordName"]
        start_type = resp["NextRecordType"]
        start_id = resp.get("NextRecordIdentifier")

    return records


def extract_record_targets(rrset: Dict[str, Any]) -> List[str]:
    """
    Returns a list of target hostnames from an RRSet:
      - ResourceRecords[].Value
      - AliasTarget.DNSName
    """
    targets = []
    if "AliasTarget" in rrset:
        dns = rrset["AliasTarget"].get("DNSName", "")
        if dns:
            targets.append(dns.rstrip("."))
    elif "ResourceRecords" in rrset:
        for rec in rrset["ResourceRecords"]:
            val = rec.get("Value", "")
            if val:
                targets.append(val.rstrip("."))
    return targets


def infer_backend_type(target: str) -> str:
    t = target.lower()
    if "elb.amazonaws.com" in t:
        return "ELB"
    if t.endswith("cloudfront.net"):
        return "CLOUDFRONT"
    if "execute-api" in t and ".amazonaws.com" in t:
        return "API_GW"
    return "OTHER"


# -------- Step 4: Join WAF resources with Route 53 --------

def build_reports(
    waf_resources: List[Dict[str, Any]],
    route53_records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns:
      (waf_protected_rows, domains_without_waf_rows)
    """

    # Normalize resource DNS names set for quick membership tests
    waf_dns_to_res = {}
    for res in waf_resources:
        dns = res.get("resource_dns", "").rstrip(".").lower()
        if not dns:
            continue
        waf_dns_to_res.setdefault(dns, []).append(res)

    # --- Build WAF-protected endpoints table ---
    waf_protected_rows = []
    for rec in route53_records:
        target = rec["record_target"].lower()
        backend_type = infer_backend_type(target)
        # Try exact or suffix match for WAF resources
        matched_res = None
        for dns, res_list in waf_dns_to_res.items():
            if dns and (target == dns or target.endswith(dns)):
                matched_res = res_list
                break

        if matched_res:
            for res in matched_res:
                waf_protected_rows.append({
                    "account_id": res["account_id"],
                    "region_or_scope": f"{res['scope']}:{res['region']}",
                    "web_acl_name": res["web_acl_name"],
                    "web_acl_arn": res["web_acl_arn"],
                    "resource_type": res["resource_type"],
                    "resource_arn": res["resource_arn"],
                    "resource_dns": res["resource_dns"],
                    "zone_name": rec["zone_name"],
                    "zone_id": rec["zone_id"],
                    "record_name": rec["record_name"],
                    "record_type": rec["record_type"],
                    "record_target": rec["record_target"],
                    "backend_type": backend_type,
                })

    # --- Build domains WITHOUT WAF table ---
    # First, find all ALB/CF-like records
    domains_without_waf = []
    for rec in route53_records:
        backend_type = infer_backend_type(rec["record_target"])
        if backend_type not in ("ELB", "CLOUDFRONT", "API_GW"):
            continue

        target = rec["record_target"].lower()
        has_waf = False
        for dns in waf_dns_to_res.keys():
            if dns and (target == dns or target.endswith(dns)):
                has_waf = True
                break

        if not has_waf:
            domains_without_waf.append({
                "account_id": rec["account_id"],
                "zone_name": rec["zone_name"],
                "zone_id": rec["zone_id"],
                "record_name": rec["record_name"],
                "record_type": rec["record_type"],
                "record_target": rec["record_target"],
                "backend_type": backend_type,
            })

    return waf_protected_rows, domains_without_waf


# -------- Main --------

def main():
    account_id = get_account_id()
    print(f"[INFO] Using AWS account: {account_id}")

    print("[INFO] Listing WAF WebACLs...")
    web_acls = list_waf_web_acls()
    print(f"[INFO] Found {len(web_acls)} WebACLs")

    print("[INFO] Listing resources attached to WebACLs...")
    waf_resources = collect_all_waf_resources(web_acls)
    print(f"[INFO] Found {len(waf_resources)} WAF-attached resources")

    print("[INFO] Enumerating Route53 hosted zones and records...")
    route53 = boto3.client("route53")
    zones = list_all_hosted_zones(route53)
    print(f"[INFO] Found {len(zones)} hosted zones")

    route53_records = []
    for z in zones:
        zone_id = z["Id"]
        # HostedZoneId is like "/hostedzone/XYZ", keep full string
        zone_name = z["Name"].rstrip(".")
        print(f"[INFO]   Zone {zone_name} ({zone_id})")

        rrsets = list_all_record_sets(route53, zone_id)
        for rr in rrsets:
            rtype = rr["Type"]
            if rtype not in ("A", "AAAA", "CNAME", "NS", "MX", "TXT", "SRV", "CAA", "ALIAS"):
                continue

            targets = extract_record_targets(rr)
            if not targets:
                continue

            for t in targets:
                route53_records.append({
                    "account_id": account_id,
                    "zone_id": zone_id,
                    "zone_name": zone_name,
                    "record_name": rr["Name"].rstrip("."),
                    "record_type": rtype,
                    "record_target": t.rstrip("."),
                })

    print(f"[INFO] Total Route53 records with targets: {len(route53_records)}")

    print("[INFO] Building reports...")
    waf_protected_rows, domains_without_waf = build_reports(
        waf_resources, route53_records
    )

    print(f"[INFO] WAF-protected endpoints: {len(waf_protected_rows)}")
    print(f"[INFO] Domains without WAF: {len(domains_without_waf)}")

    # Write CSVs
    with open("waf_protected_endpoints.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "account_id",
                "region_or_scope",
                "web_acl_name",
                "web_acl_arn",
                "resource_type",
                "resource_arn",
                "resource_dns",
                "zone_name",
                "zone_id",
                "record_name",
                "record_type",
                "record_target",
                "backend_type",
            ],
        )
        writer.writeheader()
        writer.writerows(waf_protected_rows)

    with open("domains_without_waf.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "account_id",
                "zone_name",
                "zone_id",
                "record_name",
                "record_type",
                "record_target",
                "backend_type",
            ],
        )
        writer.writeheader()
        writer.writerows(domains_without_waf)

    print("[INFO] Written waf_protected_endpoints.csv and domains_without_waf.csv")


if __name__ == "__main__":
    main()
