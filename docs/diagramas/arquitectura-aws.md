# Diagrama de arquitectura (AWS) — Reservation Management Web Application

**Reference:** RFP-001, scope frozen in [SOW.md](../SOW.md)

**Editable source:** [arquitectura-aws.drawio](./arquitectura-aws.drawio) — open at [app.diagrams.net](https://app.diagrams.net) (File → Open From → Device) or with the draw.io VS Code extension. The Mermaid diagram below is a GitHub-native preview of the same architecture and is kept in sync with it.

## Design constraints driving the choices below

The SOW is explicit about the constraints that make a heavyweight architecture the wrong choice here:

- **No dedicated IT team** and a small-business budget — see [Value](../SOW.md#value) (USD 14,800 total, hosting estimated at USD 25–40/month).
- **Low, predictable load** — ≤ 2s response under ~30 concurrent staff users across three branches (issue [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18)).
- **≥ 99.0% uptime during business hours only**, not 24/7 enterprise SLA (issue [#17](https://github.com/ngonza27/trayectoria_dllo_software/issues/17)).
- **No dedicated server infrastructure to procure** (managed cloud hosting assumed per [Value](../SOW.md#value)).

Given this, a **serverless microservices** architecture is the simple-yet-efficient fit: no servers to patch or size, near-zero idle cost outside business hours, and each bounded context from the [component diagram](./componentes.md) maps to one independently deployable AWS Lambda function behind a shared API Gateway. This avoids the operational overhead of a container orchestrator (ECS/EKS) that this client has no team to run, while still keeping services independently deployable and scalable — the definition of "microservices" that matters here, not container count.

## Diagram

```mermaid
graph TB
    Staff["👤 Staff\n(host, manager, owner)"]

    subgraph AWSCloud["AWS Cloud"]
        CF["Amazon CloudFront\n(CDN)"]
        S3["Amazon S3\nstatic web app hosting"]
        WAF["AWS WAF\nbasic request filtering"]

        APIGW["Amazon API Gateway\n(HTTP API, custom domain, throttling)"]
        Cognito["Amazon Cognito\nstaff user pool + roles/groups"]

        subgraph Lambdas["AWS Lambda — one function per microservice"]
            AuthFn["fresh-fork-auth-fn"]
            ReservationFn["fresh-fork-reservation-fn"]
            TableScheduleFn["fresh-fork-table-schedule-fn"]
            CustomerFn["fresh-fork-customer-fn"]
            ReportingFn["fresh-fork-reporting-fn"]
            AuditFn["fresh-fork-audit-fn"]
            NotificationFn["fresh-fork-notification-fn"]
        end

        EventBridge["Amazon EventBridge\nreservation domain events"]
        SQS["Amazon SQS\nnotification queue (DLQ included)"]

        RDSProxy["Amazon RDS Proxy\nconnection pooling"]
        RDS[("Amazon RDS for PostgreSQL\nMulti-AZ, single small instance\nMain relational store")]
        SES["Amazon SES\ntransactional email"]

        SecretsMgr["AWS Secrets Manager\nDB credentials"]
        CloudWatch["Amazon CloudWatch\nlogs, metrics, alarms"]
    end

    Staff -->|HTTPS| CF
    CF --> S3
    Staff -->|HTTPS API calls| WAF --> APIGW
    S3 -.->|"SPA calls REST API\n(fetch/XHR, HTTPS)"| WAF

    APIGW -->|authorize| Cognito
    APIGW --> AuthFn
    APIGW --> ReservationFn
    APIGW --> TableScheduleFn
    APIGW --> CustomerFn
    APIGW --> ReportingFn

    AuthFn --> Cognito
    ReservationFn -->|sync call| TableScheduleFn
    ReservationFn -->|sync call| CustomerFn
    ReservationFn -->|publish ReservationCreated/Modified/Cancelled| EventBridge

    EventBridge --> AuditFn
    EventBridge --> SQS --> NotificationFn
    NotificationFn --> SES

    AuthFn --> RDSProxy
    ReservationFn --> RDSProxy
    TableScheduleFn --> RDSProxy
    CustomerFn --> RDSProxy
    ReportingFn --> RDSProxy
    AuditFn --> RDSProxy
    RDSProxy --> RDS

    RDSProxy -.->|reads secret| SecretsMgr
    Lambdas -.->|logs & metrics| CloudWatch
```

Each Lambda is named `fresh-fork-<domain>-fn` so the function list in the AWS console maps 1:1 back to the bounded contexts in the [component diagram](./componentes.md). For a closer look inside two of these services, see the lower-level component diagrams: [componentes-customer-service.md](./componentes-customer-service.md) and [componentes-table-schedule-service.md](./componentes-table-schedule-service.md).

## Why each service was picked (and what was deliberately left out)

| Layer | AWS service | Why this one, at this scale |
|---|---|---|
| Frontend hosting | S3 + CloudFront | Static SPA, pay-per-request, no servers; satisfies "responsive web app, no install" (issue [#25](https://github.com/ngonza27/trayectoria_dllo_software/issues/25)) at near-zero fixed cost |
| Edge protection | AWS WAF | Basic bot/exploit filtering in front of the API without operating a firewall appliance |
| API entry point | API Gateway (HTTP API) | Single routing point to all services, built-in throttling to protect the small RDS instance under load spikes |
| Auth | Cognito | Managed staff directory with groups for role-based access (host vs. manager vs. owner) — avoids building and hardening custom auth (issue [#11](https://github.com/ngonza27/trayectoria_dllo_software/issues/11)) |
| Compute | Lambda, one function per bounded context | Matches the [component diagram](./componentes.md) 1:1; scales to zero outside business hours, which is most of the day for a 3-branch restaurant group — directly minimizes the hosting bill in [Value](../SOW.md#value) |
| Decoupling | EventBridge + SQS | Reservation Fn never waits on Audit or Notification — keeps booking response time inside the ≤2s budget (issue [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18)) even if email delivery is slow |
| Notifications | SES | Email-only per the descoped requirement (issue [#15](https://github.com/ngonza27/trayectoria_dllo_software/issues/15)); no SMS provider needed |
| Data | RDS for PostgreSQL (single small Multi-AZ instance) + RDS Proxy | Relational integrity and constraints are required to enforce double-booking prevention at the DB level (issue [#12](https://github.com/ngonza27/trayectoria_dllo_software/issues/12)) — a NoSQL store would push that logic into application code; RDS Proxy avoids Lambda connection-exhaustion at this small scale |
| Secrets | Secrets Manager | DB credentials never hardcoded in Lambda config |
| Observability | CloudWatch | Uptime and latency metrics needed to verify issue [#17](https://github.com/ngonza27/trayectoria_dllo_software/issues/17) and [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18), included free at this traffic volume |

Deliberately **not** included, to keep the architecture simple: ECS/EKS (no team to operate a cluster), a service mesh (7 services at this traffic don't need one), multi-region failover (99.0% business-hours target doesn't warrant it), and a payment or SMS gateway (explicitly out of scope per the SOW's [Scope](../SOW.md#scope) section).
