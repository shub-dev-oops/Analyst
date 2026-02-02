TICKET 1  Verify Kubernetes Metrics Pipeline
Type: Investigation
Points: 3
Owner: Nikhil Garg
Timeline: 1 sprint (complete before SRE-16016-B)
Related: SA-126434 (blocking)

Problem
SRE-16016 has been unresolved for 8 months. SA-126434 (data ingestion fix) is marked "DONE" but dashboards still show no data. We don't know if the fix actually deployed or if metrics are flowing today.

Objective
Establish the ground truth: Are Kubernetes metrics currently flowing into Elasticsearch for aasmp-eks1 and amomp-eks1?

Acceptance Criteria
 Confirmed: kube-state-metrics pod exists and is healthy in both clusters

 Confirmed: Elastic Agent or Metricbeat pods are running on all nodes in both clusters

 Confirmed: Last 24 hours of data exists in metrics-kubernetes.* indices

 Document findings: Confluence update with current component inventory




----



Restore & Verify Data Streams and Pipeline
Type: Feature/Fix
Points: 5
Owner: Nikhil Garg with DevOps
Timeline: Depends on Ticket 1



Problem
Metrics pipeline is broken or partially broken. Even if SA-126434 marked "done," the fix may not have deployed to production, or metrics stopped flowing after the initial fix.

Objective
Ensure kube-state-metrics + Elastic Agents are deployed and healthy in both clusters, with consistent 48-hour metric flow.

Acceptance Criteria
 Nikhil & Piyush sync completed with DevOps (DevOps confirms SA-126434 fix status)

 kube-state-metrics deployed to both clusters (or verified running)

 Elastic Agent DaemonSet deployed/updated with current config

 RBAC & TLS auth verified for kubelet access

 Data flows for 48 consecutive hours with no gaps

 Both clusters tagged: kubernetes.cluster.name = aasmp-eks1 / amomp-eks1




TICKET 3: Ship 3 production-ready dashboards, Confluence guide, and train Team Forge on usage.

Dashboard 1: Cluster Overview

Total nodes (count, ready status)

Total pods (running, pending, failed)

Cluster CPU utilization (trend)

Cluster memory utilization (trend)

Pod distribution across namespaces

Dashboard 2: Node Health

Node list (sortable by CPU, memory, disk)

Per-node CPU/memory gauges (color-coded thresholds)

Pod distribution per node

Node condition alerts (MemoryPressure, DiskPressure, etc.)

Dashboard 3: Pod Lifecycle & kube-system (covers SRE-16875)

Pod status breakdown by namespace (filter: kube-system)

Recent pod failures + restarts

coredns pod health (replicas, restarts)

kube-proxy pod health (per node)

Recent Kubernetes events (failures, warnings)

Confluence Documentation
Page: govMeetings EKS Monitoring - Dashboards & Runbook

