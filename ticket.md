
TITLE:
Setup Production-Parity Alerting in INT Environment

DESCRIPTION:
The INT (integration/pre-production) environment currently has monitoring data being 
collected and sent to Elasticsearch, but has NO alerting configured. This means 
infrastructure issues occurring in INT are silent failures - they go undetected until 
the code reaches production and impacts customers.

The recent incident (elastic lock scaling issue) started immediately after release and 
would have been caught in INT if alerting had been present.

ACCEPTANCE CRITERIA:
✓ INT alerts match production alert rules and thresholds
✓ Alert recipients configured (on-call/team)
✓ Test 3 alerts to verify notification delivery
✓ Document which metrics/events trigger alerts
✓ Verify no duplicate alerting between INT and Prod


We do have monitoring and we don't have alertings, so without alerting, even though 
the data is going into elastic, no one's going to notice it because there won't be any 
alerts triggered.

Setting up some alerting in INT... might have enabled us to notice this before it 
went into production.

IMPACT:
- Would have caught the elastic lock latency issue in pre-prod
- Prevents customer-facing outages from infrastructure issues
- Enables early warning for infrastructure degradation






TITLE:
Implement Infrastructure-Level Testing in INT Environment

DESCRIPTION:
Current testing strategy in INT focuses exclusively on application-level logic 
(code paths, business logic, API contracts). Infrastructure-level issues 
(connection pooling, elastic scaling, DNS resolution, resource exhaustion) 
are never tested and only discovered on release day in production.

PROBLEM STATEMENT:
The elastic lock scaling issue was an infrastructure problem that:
- Would NOT have been caught by application-level tests
- Only manifested under production load
- Caused production outage with customer impact

All these infrastructure level issues we we we just find it on the release day 
on we try to fail forward in the prod we never thought about we never look into 
it on the link

ACCEPTANCE CRITERIA:
✓ Infrastructure test plan created (list all infrastructure components to test)
✓ Connection pool stress test implemented
✓ Elasticsearch connectivity test created
✓ Kubernetes resource constraint tests added
✓ DNS/CoreDNS resolution tests added
✓ Network latency simulation tests created
✓ Tests integrated into pre-release gate
✓ Documentation: how to add new infrastructure tests

TEST SCENARIOS TO COVER:
- Connection pool exhaustion (max connections)
- Elasticsearch unavailability
- CoreDNS scaling limits and response times
- Kubernetes pod/node resource constraints
- Database connection timeout scenarios
- Network latency/packet loss simulation
- Load spike handling




Investigate Current Elastic Monitoring State in EKS Clusters
Ticket Type: Investigation/Discovery Story
Story Points: 5
Priority: High
Parent: SRE-16016 (govM: Set up Elastic dashboard for Kubernetes)
Team: Site Reliability: Team Forge
Epic: govM: Kubernetes issues

Description
As a govM SRE engineer, I need to understand the current state of Kubernetes monitoring infrastructure in our EKS clusters so we can build a comprehensive Elastic monitoring solution.

Acceptance Criteria
 Document current state of kube-state-metrics (is it deployed? what version?)

 List all Elastic agents running in aasmp-eks1 and amomp-eks1 clusters

 Verify Elasticsearch indices exist for Kubernetes metrics (metrics-kubernetes.*)

 Check if metrics are currently flowing into Elasticsearch (check last 24h data)

 Document any existing Metricbeat or Elastic Agent configurations

 Identify networking/connectivity issues between clusters and Elasticsearch

 Create visual inventory of current monitoring components (Confluence diagram/checklist)

 Identify any RBAC or permission blockers


 Success Criteria
Investigation document published to Confluence with clear status of:

What components are present

What's working/broken

What's missing

Blockers identified for next phase
