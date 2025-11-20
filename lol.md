## 1. Product Overview

**Description**
Swagit is a video-focused application/platform under the Granicus GOV product family, closely related to GovMeetings and Granicus Video.
It is primarily a video management, video playback, and agenda/meeting engagement platform used by government clients.

**Training documents**

- Swagit KT session recordings (SharePoint – Swagit KT series).
- Swagit – Sysindex (Production Support) – Confluence.
- **Key Dependencies:** 
    - **Swagit API**
        - Dev: https://api.dev.swagit.com → k8s-swagit-aasmdswa-c4f03ed0a8-1203319188.us-east-1.elb.amazonaws.com
        - QA: https://api.qa.swagit.com → k8s-swagit-aasmqswa-841b648ba1-759849006.us-east-1.elb.amazonaws.com
        - Int: https://api.int.swagit.com → k8s-swagit-aasmiswa-b89533781f1512826265.us-east-1.elb.amazonaws.com
        - Prod: https://api.swagit.com (target ELB/EKS **TBD**)

        - **Admin v3**
        - Dev: https://admin.dev.swagit.com (and `*.dev`) → k8s-swagit-aasmdswa-d5f86205f6-1848117766.us-east-1.elb.amazonaws.com
        - QA: https://admin.qa.swagit.com (and `*.qa`) → k8s-swagit-aasmqswa-f464fa6e64-595398558.us-east-1.elb.amazonaws.com
        - Int: https://admin.int.swagit.com (and `*.int`) → k8s-swagit-aasmiswa-b8867a3273-368039205.us-east-1.elb.amazonaws.com
        - Prod new: `admin.new.swagit` → ELB/EKS **TBD**
    
- **Architecture & Data Flow:** 
    [Swagit Infrastructure – Confluence](https://confluence.granicus.com/spaces/PE/pages/551295514/Swagit+Infrastructure)
- **Business Impact:** *What happens if this product fails?*

### 1.z Core Components

- **API (govmeetings-swagit-api)**
  - Rails 7 application.
  - Fleet orchestration for on-prem Swagit systems (similar to GADS).
  - Scheduling interface used by Managed Services to set events for ~95% of customers.
  - Handles ~15k RPM of consistent traffic from on-prem systems checking in and pulling upcoming event lists.

- **Admin V3 (govmeetings-swagit-web)**
  - Web UI used by internal teams and customers for configuration and scheduling.

- **Worker (govmeetings-swagit-worker)**
  - Background processing for integrations, captioning, social publishing, and VOD-related tasks.


### 1.2 Live & VOD Video Components

- **Live Streaming**
  - Customer encoders publish to Wowza **Origin** servers.
  - Wowza **Edge** servers poll all origins and serve streams.
  - **CDN:** Fastly is used for live streaming delivery.
  - Consolidated with **MeMa archive tier** using MediaCache pointers to Swagit S3 buckets.

- **Recorded Video (VOD)**
  - Recorded videos stored in Swagit S3 buckets.
  - **CDN:** CloudFront is used for VOD delivery.


**Database**

- Swagit database is an RDS SQL instance in the **govMeetings Prod** AWS account.
- Connection credentials: LastPass → folder **“Shared-TSE GovMeetings”** → note **“Connections”**.

**Hosted location**

- Web components (`govmeetings-swagit-web`, `govmeetings-swagit-api`, `govmeetings-swagit-worker`) run in **AWS EKS**.
- **Live video:**
  - Dev & QA: hosted in **AWS**.
  - INT & Prod: hosted in the **Ashburn datacenter**.

---

## 2. Reliability Metrics

### 2.1 SLO Thresholds for APM Golden Signals

| SLA class | SLO Availability Goal | Period | Error Budget | Downtime per month | SLO Latency (99p) | SLO Latency (95p) |
| --- | --- | --- | --- | --- | --- | --- |
| Tier-1 | 99.99% | 30 days | 0.01% | 4.32 min | 99% of requests to take ≤ 250 ms | 95% of requests to take ≤ 200 ms |
| Tier-2 | 95% | 30 days | 5% | 36 hours | 99% of requests to take ≤ 250 ms | 95% of requests to take ≤ 200 ms |
- **Scheduled Downtimes (SDTs):** Planned SDTs are not consumed from error budget (communication must be sent to customers).
- **SLO Saturation Goal:** CPU / Memory / Disk / Network thresholds up to which apps perform with optimal user experience.*Latency increases are often leading indicators of saturation.*
- **SLO Traffic Goal (RPMs):** 
    - Sysindex / Swagit API: **~15k RPM**  baseline from on-prem encoders / systems polling for upcoming events.
    - Web / Worker: aligned to API traffic patterns and event schedules (bursty around meeting start/end).??? 

---

### 2.2 SLO Availability

> Source: Cloud Ops → SRE_Reporting workflows (Microsoft Teams)
> 

**Weekly Trend Chart:** ***[Insert chart / screenshot here]***

**Availability SLO Table**

| Application | SLO Target | Threshold | Error Budget Consumed | Error Budget Remaining | SLI Value | Status |
| --- | --- | --- | --- | --- | --- | --- |
| *govMeetings-swagit-api_production* | 99.90 | N/A | *value* | *value* | *value* | HEALTHY |
| *govMeetings-swagit-worker_production* | 90.00 | N/A | *value* | *value* | *value* | HEALTHY |
| *govMeetings-swagit-web_production* | 99.00 | N/A | *value* | *value* | *value* | HEALTHY |

---

### 2.3 SLO Latency

> Source: Cloud Ops → SRE_Reporting workflows (Microsoft Teams)
> 

**Weekly Trend Chart:** ***[Insert chart / screenshot here]***

**Latency SLO Table (99p / 95p)**

| Application | SLO Target | Threshold (ms) | Error Budget Consumed | Error Budget Remaining | SLI Value | Status |
| --- | --- | --- | --- | --- | --- | --- |
| *govMeetings-swagit-api_production* | 99.99 | 250 | *value* | *value* | *value* | HEALTHY / VIOLATED |
| *govMeetings-swagit-worker_production* | 99.99 | 380000 | *value* | *value* | *value* | HEALTHY / VIOLATED |
| *govMeetings-swagit-web_production* | 99.99 | 650 | *value* | *value* | *value* | HEALTHY / VIOLATED |

---

### 2.4 Action Plan on SLO Deviations

*Describe root causes and corrective actions whenever SLOs are at risk or violated.*

- **Root cause(s):** *e.g., high latency on web tier due to DB contention*
- **Immediate corrective actions:** *e.g., scale out pods, DB index fix, rollback, feature flag, etc.*
- **Long-term prevention:** *e.g., capacity planning, query optimisation, cache, new alerts, load tests*
- **Owners / ETA:** *names + target dates*

---

## 4. Incident Summary

> Include incidents affecting Swagit & Granicus Video.
> 

| Period | Count | MTTA (mins) | MTTD (mins) | MTTR (hrs) |
| --- | --- | --- | --- | --- |
| Last 7 days | *#* | *mins* | *mins* | *hrs* |
| Last 30 days | *#* | *mins* | *mins* | *hrs* |
| Quarterly | *#* | *mins* | *mins* | *hrs* |

**Links**

- [Quick Suite – Incident Analysis](https://www.notion.so/Swagit-SME-Dashboard-2b14fa80b5de804da9f0d54026622790?pvs=21)
- [Incident Postmortems](https://www.notion.so/Swagit-SME-Dashboard-2b14fa80b5de804da9f0d54026622790?pvs=21)

### Action Plan on Incidents

- **Data quality:** *Correct cause field updates, accurate MTTA/MTTR/MTTD, clear timeline in tickets.*
- **High incident count:** *List top categories and actions to reduce them.*
- **High MTTA / MTTD / MTTR:** *Actions to improve detection, triage, on-call runbooks, automation.*
- **Customer reported tickets:** *Actions taken towards reducing customer-facing reports.*

---

## 5. Problem Tickets & RCA

| Ticket ID | Description | RUN Link | RCA Status | Corrective Action | Owner |
| --- | --- | --- | --- | --- | --- |
| *ID* | *Desc* | *Link* | *Open/In Progress/Done* | *Action* | *Owner* |

---

## 6. Monitoring & Alerting

- **Dashboards:** *Elastic (link to dashboards)*
- **Alert Health:** *False positives %, known gaps, noisy alerts.*
- **Recent Improvements:**
    - *Item 1 – e.g., Added CPU saturation alert for Swagit worker.*
    - *Item 2 – e.g., Tuned web latency threshold from 800 ms → 650 ms.*

---

## 7. Release Readiness

- **SME CR Review Status:** *Approved / Pending / Blocked + notes*
- **Go/No-Go Checklist:** *[Link]*
- **Upcoming Releases:**
    - *Date – Release name – SME sign-off status (Go/No-Go)*
    - *Date – Release name – SME sign-off status*

---

## 8. Action Items

| Item | Owner | Due Date | Status |
| --- | --- | --- | --- |
| *Task* | *Name* | *YYYY-MM-DD* | Open / In Progress / Done |

---

## 9. Improvement Initiatives

*List ongoing projects to reduce outages, improve observability, and increase automation.*

- *Initiative 1 – e.g., Swagit Fargate migration & PV improvements*
- *Initiative 2 – e.g., Error budget burn dashboard for Granicus Video*
- *Initiative 3 – e.g., Synthetic checks for critical endpoints*

---

## 10. Incident Reduction Goal

| Quarter | Target (Incidents) | Actual (Incidents) | Trend |  |
| --- | --- | --- | --- | --- |
| Q1 | *value* | *value* | ⬆ / ⬇ |  |
| Q2 | *value* | *value* | ⬆ / ⬇ |  |
| Q3 | *value* | *value* | ⬆ / ⬇ |  |
| Q4 | *value* | *value* | ⬆ / ⬇ |  |