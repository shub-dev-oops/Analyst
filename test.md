# 📊 SRE SME Dashboard - Swagit & Granicus Video

*Weekly Health & Reliability Report*

## 1. Product Overview

**Description:**Swagit is a video-focused application/platform closely related to GovMeetings and Granicus Video. Primarily handles video management, playback, and agenda engagement.

**Key Documentation:**

- [Swagit - Sysindex (Production Support)](https://www.google.com/search?q=%23)
- [Architecture & Infrastructure Page](https://www.google.com/search?q=%23)
- [Environment URLs & Dependencies](https://www.google.com/search?q=%23)

## 2. Reliability Metrics

### 2.1 Target SLO Thresholds for APM Golden Signals

| SLA Class | SLO Availability Goal | Period | Error Budget | Approx. Downtime / Month | SLO Latency (99p) | SLO Latency (95p) |
| --- | --- | --- | --- | --- | --- | --- |
| **Tier-1** | 99.99% | 30 days | 0.01% | ~4.32 minutes | 99% of requests ≤ 250 ms | 95% of requests ≤ 200 ms |
| **Tier-2** | 95% | 30 days | 5% | ~36 hours | 99% of requests ≤ 250 ms | 95% of requests ≤ 200 ms |
- **Scheduled Downtimes (SDTs):** Planned SDTs do not consume error budget; communication must be sent to customers.
- **Saturation SLOs:** CPU/Memory/Disk/Network up to thresholds where UX remains acceptable; latency increases often signal saturation.
- **Traffic SLOs (RPM):**
    - Swagit API baseline: ~15k RPM from on-prem encoders/systems.
    - Swagit Web/Worker: aligned with API and event schedule (bursty around meeting start/end).

### 2.2 Current Baseline

| Granicus Product | Customers US/CA | SLA Class | APMs | Servers | SLO Availability Goal | SLO Latency@99p Goal | SLO Latency@95p Goal | SLO Traffic Goal | SLO Saturation Goal | DR site |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Media Manager PHP** | 1850/31 | Tier-1 | govmeetings-mediamanager-php | gasmp-mmphp1-7 | 99.859% | 1084ms | 285ms | 4,145.46 (rpm) |  | (US) azmop (CA) |
| **MDC** |  | Tier-1 | govmeetings-mediamanager-net | gasmp-mmnet1-2 | 95.192% | 3201ms | 104ms | 2,523.29 |  |  |
| **MediaVault Archive Video** |  |  | mediamanager-net | amomp-mmnet1-2 |  |  |  |  |  |  |
| **Live Video** |  | Tier-1 | govmeetings-mediavault-web | gasmp-medapp1-6 | 99.289% | 2424ms | 1210ms | 686.09 |  |  |
|  |  |  |  | azmop-medapp1-2 |  |  |  |  |  |  |
| **Granicus Video** |  | Tier-1 |  | gasmp-wowstr | n/a | n/a | n/a |  |  |  |
|  |  |  |  | gasmp-wowarch |  |  |  |  |  |  |
| **Swagit** |  | Tier-2 | govmeetings-swagit-api |  |  |  |  |  |  |  |
|  |  | Tier-2 | govmeetings-swagit-web |  |  |  |  |  |  |  |
|  |  | Tier-2 | govmeetings-swagit-worker |  |  |  |  |  |  |  |

## 3. Reliability Scoreboard (Weekly Status)

| **Overall Health** | **Trend (Week-over-Week)** | **Critical Actions Required** |
| --- | --- | --- |
| 🟠 **AT RISK** | 📉 **Latency Degradation** | **Latency on Web & Worker** is consistently violating targets. **Action Plan needed.** |

### 3.1 Current Status vs Targets (Week of Nov 24)

| Service | Metric | Target | Current Value | Status |
| --- | --- | --- | --- | --- |
| **Swagit API** | Availability | 99.99% | **99.96%** | ✅ Healthy |
|  | Latency (99p) | 250ms | **100%** | ✅ Healthy |
| **Swagit Worker** | Availability | 90.00% | **92.85%** | ✅ Healthy |
|  | Latency (99p) | 380s | **99.73%** | ❌ **Violated** |
| **Swagit Web** | Availability | 99.00% | **99.76%** | ✅ Healthy |
|  | Latency (99p) | 650ms | **6.20%** | ❌ **Violated** |

### 3.2 Action Plan on Deviations

*Required whenever SLOs are at risk or violated.*

| Service | Metric | Root Cause / Context | Corrective Action (Owner) | ETA / Status |
| --- | --- | --- | --- | --- |
| **Swagit Web** | Latency | DB Contention on `media` table | **[SRE-456]** Implement Caching | Dec 05 |
| **Swagit Worker** | Latency | Long-running VOD jobs | **[SRE-123]** Queue Optimization | Nov 28 |

### 3.3 Weekly Trend: Latency Compliance

*Percentage of requests meeting the latency threshold.(Instruction: Wrap this table in a **Chart from Table** macro. Type: Line)*

| Week | API (%) | Worker (%) | Web (%) |
| --- | --- | --- | --- |
| Nov 17 | 100.00 | 99.77 | 8.40 |
| Nov 24 | 100.00 | 99.73 | 6.20 |
| Nov 31 |  |  |  |

### 3.4 Weekly Trend: Availability

*Uptime percentage against SLO Targets.(Instruction: Wrap this table in a **Chart from Table** macro. Type: Line)*

| Week | API (%) | Worker (%) | Web (%) | Target (Web) |
| --- | --- | --- | --- | --- |
| Nov 17 | 99.96 | 93.66 | 99.76 | 99.00 |
| Nov 24 | 99.96 | 92.85 | 99.76 | 99.00 |
| Nov 31 |  |  |  |  |

## 4. Incident Summary

*Scope: Swagit & Granicus Video incidents only.*

### Incident Volume (Weekly)

*(Instruction: Use a **Jira Chart Macro** here with filter: `project = GV AND type = Incident`)*

> [PLACEHOLDER FOR JIRA CHART]
> 

### KPIs & Efficiency

| Period | Incident Count | MTTA (Avg) | MTTR (Avg) |
| --- | --- | --- | --- |
| Last 7 Days | 0 | 0 min | 0 min |
| Last 30 Days | 1 | 1 min | 99 min |
| **Quarterly Goal** | **< 3 (Sev1)** | **< 5 min** | **< 15m (SOP) / 60m (No SOP)** |

> Analyst Note: MTTR for last 30 days was high (99 min) due to [Incident-Link]. RCA pending.
> 

## 5. Traceability: Problem Tickets & RCA

*Mapping SRE tickets to Automated Problem tickets and Dev work.*

| SRE Ticket (Kanban) | Linked Problem Ticket (RUN) | Description | Linked Dev/Infra Ticket | RCA Status | Owner |
| --- | --- | --- | --- | --- | --- |
| **[SRE-17330]** | [SA-129722] | Frequent mediacache disk utilization >96% | [OPS-445] | **Done** | Chase House |
| **[SRE-XXXXX]** |  | [Description] |  |  |  |

## 6. Monitoring & Alerting

- **Dashboards:** [Link to Elastic Swagit API], [Link to Worker Dashboard]
- **Alert Health:**
    - 95% of incidents detected by alerts (Target: >95%).
- **Recent Improvements:**
    - *[Date]*: Added alert for Swagit web 99p latency > X ms.
    - *[Date]*: Tuned false-positive alert on Wowza health.

## 7. Release Readiness

- **Go/No-Go Checklist:** [Link to Checklist]

| Release Version | Product | Planned Date | SME Review Status | Notes |
| --- | --- | --- | --- | --- |
| v2.4.1 | Swagit | Dec 01 | **Pending** | Pending Load Test results |

## 8. Action Items (Corrective Actions)

*Tracking closure of actions from RCAs and Postmortems.*

| Item | Context (RCA/Inc) | Owner | Due Date | Status |
| --- | --- | --- | --- | --- |
| Implement DB index for query Q | RUN-55441 | Nikhil | Nov 30 | In Progress |
| Update Runbook for VOD failure | RUN-55441 | Sairam | Dec 15 | Open |

*(Targets: Short-term < 14 days, Long-term < 60 days)*

## 9. Improvement Initiatives

*Ongoing projects to reduce toil and improve reliability.*

1. **Swagit Fargate Migration:** Reliability & ops simplification. (Status: Planning)
2. **Web Latency Optimization:** DB caching strategy. (Status: Dev in progress)
3. **Alert Deduplication:** AI-based digest. (Status: Testing)

## 10. Incident Reduction Goal

| Quarter | Target | Actual (Sev1) | Actual (Sev2) | Trend |
| --- | --- | --- | --- | --- |
| Q4 2025 | Sev1 ≤ 1 | 0 | 1 | 🟢 On Track |

*(Notes: One Sev2 in Oct regarding Disk Utilization. Fix deployed.)*