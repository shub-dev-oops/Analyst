# Swagit & Granicus Video – Release Health Template (INT/PROD)


---

## 1. Release Snapshot

| Field                 | Value                                  |
|-----------------------|----------------------------------------|
| Release Name / Train  | `<Dec 2025 Swagit/Video>`             |
| Environment           | `<INT / PROD>`                         |
| Window (CST / IST)    | `<Start–End>`                          |
| Prepared By           | `<Name>`                               |
| Overall Health        | `<Healthy / Healthy w/ warnings / Risk>` |

---

## 2. Endpoint Status

| Endpoint                                      | Role              | Status | Note (1–2 words)        |
|-----------------------------------------------|-------------------|--------|-------------------------|
| https://admin.v3.swagit.com/readiness_check   | Legacy Admin      | `<200>` | `<OK / slow / spike>`  |
| https://admin.new.swagit.com/readiness_check  | New Admin         | `<200>` | `<OK / better / worse>`|
| https://api.v3.swagit.com/readiness_check     | Legacy Video API  | `<200>` | `<OK / spike>`         |
| https://api.new.swagit.com/readiness_check    | New Video API     | `<200>` | `<OK / spike>`         |

---

## 3. Readiness Duration (Charts + 1-line analysis)

| Area        | What the chart shows (max 1–2 sentences)                                                       | Chart placeholder          |
|-------------|-------------------------------------------------------------------------------------------------|----------------------------|
| Admin v3    | `<Baseline ~Xs, brief spikes on <dates>, returns to baseline; no post-release regression.>`     | `[CHART-ADMIN-V3-DUR]`     |
| Admin new   | `<Similar or better than v3; note any new spikes after release and if they recover quickly.>`  | `[CHART-ADMIN-NEW-DUR]`    |
| API v3      | `<Low baseline; mention any isolated spikes and confirm post-release level is same as before.`>| `[CHART-API-V3-DUR]`       |
| API new     | `<Compare to API v3; call out if baseline is higher/lower and if spikes align with deploy time.`| `[CHART-API-NEW-DUR]`      |

> **How to fill:** Use Synthetics/Uptime *Duration trends* for each URL, range: 3–5 days before + 2–3 days after release. Focus only on changes vs pre-release (baseline shift, new spikes, or clear improvement).

---

## 4. Log / Warning Snapshot (Video Path)

| Pattern / Warning (short)                        | Current Impact (now)                   | Future Risk / Follow-up           |
|--------------------------------------------------|----------------------------------------|-----------------------------------|
| `<RubyGems required_ruby_version warning>`       | `Warning only; runtime OK`             | `Fix before Ruby/Bundler upgrade` |
| `<Any encoder / storage / CDN warning>`          | `<None / minor / user-facing>`         | `<Risk if frequency grows>`       |

---

## 5. Risks & Actions (Combined)

| Area      | Risk / Observation                               | Owner    | Pri | Due |
|-----------|---------------------------------------------------|----------|-----|-----|
| Logs      | `<High access-log rate may hide real errors>`    | `<Team>` | P2  | `<d>` |
| Platform  | `<Ruby/RubyGems needs upgrade before base change>`| `<Team>` | P2  | `<d>` |
| Readiness | `<API new shows intermittent spikes post-release>`| `<Team>` | P1  | `<d>` |

