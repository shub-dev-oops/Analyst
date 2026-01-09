# Elastic Monitoring Gaps (Logs + APM) — Control Tower

**Owner:** SRE — Team Forge  
**Purpose:** A single living tracker for all observability coverage gaps (Logs + APM) across GovMeetings / Swagit / related products. Closure requires **evidence links**.

---

## 1) Quick Summary (update weekly)
- **APM coverage:** `X / Y` services ✅  
- **Logs coverage:** `X / Y` services ✅  
- **New this week:** `n`  
- **Closed this week:** `n`  
- **Top 3 blockers:** <short list>

**Legend:** ⬜ Todo · 🟨 In Progress · ✅ Done · 🟥 Blocked

### Coverage Heatmap (high-level)
| Product / Service | Logs | APM |
|---|---|---|
| Legistar sub apps | ⬜ | — |
| media-vault-web | ⬜ | — |
| meeting-data-channel | ⬜ | ⬜ |
| advance-search (Media Manager) | — | ⬜ |
| Pythagoras | — | ⬜ |
| Wowarch | — | ⬜ |
| Swagit (web/api/worker) | ⬜ | — |

> Tip: Color these cells as status changes. Keep it brutally simple.

---

## 2) Portfolio Tracker (single source of truth)
Fill owners/ETA and keep status fresh. **Do not mark Done without evidence links.**

| Product/Area | Service / Component | Gap Type | Current Gap | Target State | Jira | Owner | Priority | ETA | Status | Evidence (APM/Kibana) | Notes / Blockers |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Legistar | Legistar sub apps | Logs | Missing/insufficient app logs in Elastic | Structured logs with fields + saved view | https://jira.granicus.com/browse/SA-131864 |  |  |  | ⬜ |  |  |
| Media Vault | media-vault-web | Logs | Logs missing/insufficient | Structured logs with fields + dashboard | https://jira.granicus.com/browse/SA-131865 |  |  |  | ⬜ |  |  |
| GovMeetings | meeting-data-channel | APM | Service not visible / no traces | APM service + key transactions | https://jira.granicus.com/browse/SA-131867 |  |  |  | ⬜ |  |  |
| Media Manager | advance-search | APM | No APM instrumentation | APM service + 3 named transactions | https://jira.granicus.com/browse/SA-131869 |  |  |  | ⬜ |  |  |
| GovMeetings | meeting-data-channel | Logs | Unstructured logs / fields missing | `service.name`, `env`, `host.hostname` parsed | https://jira.granicus.com/browse/SA-131876 |  |  |  | ⬜ |  |  |
| (App) | Pythagoras | APM | No service/transactions in APM | APM service + latency/error charts | https://jira.granicus.com/browse/SA-131877 |  |  |  | ⬜ |  |  |
| (App) | Wowarch | APM | No service/transactions in APM | APM service + latency/error charts | https://jira.granicus.com/browse/SA-131880 |  |  |  | ⬜ |  |  |
| Swagit | swagit-web / swagit-api / swagit-worker | Logs | Incomplete/missing fields | Structured logs + saved search | https://jira.granicus.com/browse/SA-131882 |  |  |  | ⬜ |  |  |

---

## 3) Standards & Definition of Done (DoD)

### APM — DoD
- **Service present** in Elastic APM with correct tags: `service.name`, `environment` (`prod|stage`), `service.version` (if available)
- **Charts populated** in last 15 minutes: Transactions (tpm), Latency (p50/p95), Error rate
- **Key transactions named** (min 3): e.g., `/advanced-search/query`, `/advanced-search/suggest`, `/advanced-search/filters`
- **(Strongly recommended)** Logs↔Traces correlation (trace.id) OR note why not yet possible
- **Evidence:** Link to APM service page + screenshot(s) of transaction list and latency chart

### Logs — DoD
- Logs visible in the **intended index/datastream** (not dev/noise)
- **Required fields parsed**: `timestamp`, `message`, `service.name`, `event.dataset` (if used), `host.hostname`, `env`, `level`
- Message parsing **not** a single blob; JSON/structured where possible
- A saved **Kibana Discover** view and/or **dashboard** exists
- **Evidence:** Links to Discover/Dashboard + 1–2 screenshots

> Closure without evidence links is not allowed.

---

## 4) Naming & Tagging
- `service.name`: kebab-case service identifier (e.g., `advanced-search`)
- `environment`: `prod`, `stage` (mirror deploy environments)
- `service.version`: app version/commit (if practical)
- Optional helpful tags: `team`, `component`, `deployment` (ecs/k8s/fargate)

---

## 5) Validation & Evidence (how to test)
1. **Stage first**: instrument, deploy, and generate traffic
2. Confirm **APM service appears** within 5–10 minutes
3. Open **1 trace**; verify spans and route names are clean (no “unknown route”)
4. Check **logs**: fields extracted; correlation visible if enabled
5. Capture **links + screenshots**; attach in the tracker and the Jira ticket
6. Roll to **prod** during a low-risk window and repeat checks

---

## 6) Jira Label & Macro (auto-tracking)
- Add label to all relevant tickets: `elastic-monitoring-gap`
- **JQL filter** (use in the Jira Issues macro in Confluence):
```
labels = elastic-monitoring-gap ORDER BY priority DESC, updated DESC
```
- Or track explicitly via keys:
```
key in (SA-131864, SA-131865, SA-131867, SA-131869, SA-131876, SA-131877, SA-131880, SA-131882)
```

---

## 7) “Gold Example” (copy this style for each ticket)
**Service:** Media Manager — Advanced Search  
**Gap Type:** APM  
**Current State:** No APM service/transactions visible  
**Target State:** APM service `advanced-search` with env tags; 3 key transactions named; latency/error charts populated

**Acceptance Criteria**
- APM shows `service.name = advanced-search`, `environment = stage|prod`
- Transactions tpm > 0; latency charts visible; error rate chart visible
- Key transactions: `/advanced-search/query`, `/advanced-search/suggest`, `/advanced-search/filters`
- (If enabled) trace.id appears in logs; otherwise captured as a follow-up gap
- **Evidence:** APM service URL + screenshots of transaction list & latency chart

**Validation Plan**
- Deploy OTel/APM agent in stage → generate traffic → verify → roll to prod

**Risk / Rollback**
- Disable agent via env var/ Helm value; revert PR if overhead seen

**RACI**
- **R:** SRE (instrumentation helm/agent config)  
- **A:** SRE Lead  
- **C:** App team  
- **I:** PM / Stakeholders

**Links**
- Jira: https://jira.granicus.com/browse/SA-131869  
- APM Service: <link after deployment>  
- Screenshot(s): <attach>

---

## 8) Cadence & Comms
- **Weekly update:** refresh counters, statuses, blockers (date-stamped)
- **Slack update template:**
> Coverage: APM `X/Y`, Logs `X/Y` | New: `n` | Closed: `n` | Blockers: `<short>`  
> Control Tower: <Confluence link>

---

## 9) Risks & Rollback (standard text)
- If latency/CPU overhead rises beyond agreed threshold, disable agent and revert config; document findings and follow-up plan

---

## 10) Notes & Decisions Log
| Date | Decision / Note | Owner |
|---|---|---|
| yyyy-mm-dd | Adopt OTel for <service>; agent overhead acceptable in stage | |
| yyyy-mm-dd | Standardized service naming across GovM apps | |

---

## Appendix A — **Ticket Description Template (paste into Jira)**
**Summary**: <One-line gap + product/service>

**Context / Current State**: <What’s missing today>

**Target State**: <Exactly what must exist in Elastic (APM/Logs)>

**Scope**: <In scope>

**Out of Scope**: <Explicitly out>

**Instrumentation Plan**: <APM agent vs OTel, where configured>

**Config Changes**: <Helm values, env vars, code hooks>

**Validation / Test Plan**: <Stage → prod steps>

**Acceptance Criteria**:
- APM: service visible, transactions/latency/error populated, key transactions named
- Logs: fields parsed (`service.name`, `env`, `host.hostname`, etc.), saved view exists

**Evidence to Attach**: APM service URL, Kibana links, screenshots

**Risks / Rollback**: <How to disable/revert>

**Dependencies**: <App team PRs, credentials, infra>

**RACI**: R / A / C / I

**Links**: Jira(s), Confluence tracker, dashboards

---

## Appendix B — Helpful Link Placeholders
- **Elastic APM (prod)**: <url>
- **Elastic APM (stage)**: <url>
- **Kibana Discover (prod)**: <url>
- **Kibana Dashboard (prod)**: <url>

> Keep this page short, visual, and ruthlessly up to date. The goal is **portfolio visibility with receipts**.

