# Statement of Work — RFP-001 Restaurant Reservation System

**Client:** Fresh Fork Restaurant Group
**Reference RFP:** RFP-001: Restaurant Reservation System
**Backlog:** [Issues #11–#27](https://github.com/ngonza27/trayectoria_dllo_software/issues) in this repository
**Status:** Draft for client review — lab-01 deliverable
**Date:** 2026-08-11

---

## Contents

- [Title](#title)
- [Abstract](#abstract)
- [Value](#value)
- [Scope](#scope)
- [Payment](#payment)
- [Purpose](#purpose)
  - [Objectives](#objectives)
  - [Performance](#performance)
- [Who does what](#who-does-what)
  - [People](#people)
  - [Roles](#roles)
  - [Responsibilities](#responsibilities)
- [Context](#context)
  - [Present](#present)
  - [Future](#future)
- [Planning](#planning)
  - [Requirements](#requirements)
- [Other terms and conditions](#other-terms-and-conditions)
  - [Client's obligations](#clients-obligations)
- [Schedule](#schedule)
  - [Expected start date and completion date](#expected-start-date-and-completion-date)
  - [Sign-off](#sign-off)

---

## Title

Reservation Management Web Application for Fresh Fork Restaurant Group.

## Abstract

This Statement of Work (SOW) outlines the objectives, scope, deliverables, and timeline for the design and development of a reservation management web application for Fresh Fork Restaurant Group, a three-branch casual dining group currently tracking bookings by phone, WhatsApp, and handwritten notebooks. The project's purpose is to eliminate double bookings and reduce the manual effort staff spend checking availability, by giving front-desk staff and managers a single web application to create, update, cancel, and check reservations, backed by a shared calendar and customer history across the three locations. The contractor will deliver the web application, a staff onboarding guide, and testing evidence for the booking and cancellation workflows. The MVP is scoped to launch first with a single branch before enabling multi-branch selection, given the client's small-business budget and lack of a dedicated IT team. The estimated timeline is 10 weeks from kickoff to go-live, with a total estimated value of USD 14,800, paid across four milestones tied to specific deliverables.

## Value

The estimated value of the work described in this SOW is **USD 14,800**, fixed price, covering discovery and design, development of the core booking and table-management features, the staff onboarding guide, and testing evidence for the booking/cancellation workflows, plus 30 days of post-launch support. This estimate assumes managed cloud hosting (no dedicated server infrastructure to procure) and does not include ongoing hosting fees beyond the first 30 days, which are estimated separately at USD 25–40/month depending on the provider chosen. Costs outside this value — such as a payment gateway, SMS provider, or advanced analytics — are explicitly out of scope per the RFP and are not included; see [Scope](#scope).

## Scope

The scope of this project is the design, development, and deployment of a single reservation management web application usable by Fresh Fork's three branches, covering: staff login with role-based access (host/receptionist vs. manager); availability search by date, time, and party size with database-level double-booking prevention; creation, modification, and cancellation of reservations; basic customer contact records with a shared history across branches so repeat customers are recognized; table and operating-hours configuration per branch; and a manager view of the shared calendar. The application will be delivered as a responsive web app that works on common laptop and mobile browsers without requiring staff to install anything. Work will proceed in two phases: Phase 1 delivers full booking functionality for one pilot branch; Phase 2 extends branch selection to the remaining two branches and adds the manager's cross-branch view. Per the RFP's explicit Out-of-Scope Warning, this project **excludes** food ordering, loyalty programs, advanced analytics/reporting beyond a basic dashboard, complex payment processing (deposits/prepayment), and real-time SMS integrations — these were confirmed against the client's stated constraints during backlog review (see [Requirements](#requirements)) and would require a separate SOW if requested later.

## Payment

The total value of USD 14,800 is paid in four installments tied to the milestones defined in the project's GitHub backlog: 20% (USD 2,960) upon signing this SOW and completion of **M1 – Discovery & Analysis** (confirmed requirements, resolved clarifications); 40% (USD 5,920) upon completion of **M2 – Core Features** (single-branch booking, staff login, table/schedule management, and cancellation/modification flows working end-to-end); 25% (USD 3,700) upon completion of **M3 – Technical Proposal** deliverables (multi-branch view, onboarding guide, and testing evidence signed off by the client); and the final 15% (USD 2,220) 30 days after go-live, once post-launch support concludes with no open critical defects. Payments are due via bank transfer within 15 days of invoice issuance. Any request to add out-of-scope functionality (e.g., payments, SMS, loyalty features) will be quoted and billed separately, subject to the client's prior written approval.

## Purpose

### Objectives

The primary objective is to replace Fresh Fork's phone/WhatsApp/notebook booking process with a single web application that prevents double bookings and gives every branch a shared view of table usage and customer history, without requiring the client to hire IT staff to operate it. By completion, the client will have: a working reservation web app covering all three branches; staff trained using a short onboarding guide; and documented test evidence for the booking and cancellation workflows. Success means a host with no prior technical training can book, modify, and cancel a reservation without assistance, and that double bookings caused by the old manual process no longer occur.

Example key results for the first 90 days post-launch:
- 0 double-booking incidents across all three branches (down from a recurring peak-evening problem).
- 100% of front-desk staff onboarded using only the delivered guide, with no additional contractor training sessions required.
- All three branches actively using the shared calendar within 30 days of their respective go-live.

### Performance

Performance will be tracked through the milestone reviews defined in [Payment](#payment) and through the acceptance criteria recorded on each backlog issue. Metrics are deliberately scaled to a small-business operation with no dedicated IT team, rather than to enterprise SLAs.

Business performance metrics:
- **Double-booking rate:** 0 confirmed double bookings per month, verified against the reservation log, starting the month after go-live.
- **Staff time on manual availability checks:** reduced by at least 70% versus the pre-project baseline (self-reported by branch managers at 30 and 90 days).
- **Onboarding effectiveness:** at least 90% of host/receptionist staff can complete a full booking–modify–cancel cycle unaided after reading the onboarding guide (issue [#26](https://github.com/ngonza27/trayectoria_dllo_software/issues/26)).

Technical performance metrics:
- **Availability:** ≥ 99.0% monthly uptime during business hours, on standard managed hosting (issue [#17](https://github.com/ngonza27/trayectoria_dllo_software/issues/17)).
- **Response time:** availability search and booking confirmation respond in ≤ 2 seconds under a peak load of ~30 concurrent staff users across the three branches (issue [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18)).
- **Data integrity:** double-booking prevention is enforced at the database level, verified by a concurrent-request test case (issue [#12](https://github.com/ngonza27/trayectoria_dllo_software/issues/12)).
- **Test coverage:** 100% of the documented booking/cancellation test cases pass before go-live sign-off (issue [#27](https://github.com/ngonza27/trayectoria_dllo_software/issues/27)).

## Who does what

### People

Detailed contact information for each participant (names, phone numbers, emails, availability) will be maintained in a separate `people.md` document, kept up to date as contacts are confirmed. At minimum it should record: the Fresh Fork owner(s) or designated decision-maker, one manager per branch, the contractor's project lead ("Work Authority" for this SOW, see [Sign-off](#sign-off)), and the contractor's developer(s).

### Roles

| Role | Description |
|---|---|
| Client owner/decision-maker | Approves scope, budget, and sign-off at each milestone |
| Branch manager | Confirms branch-specific data (tables, hours), reviews the manager dashboard, approves onboarding guide |
| Host/receptionist | Primary daily user; creates, modifies, cancels reservations |
| Contractor project lead | Single point of contact for the client; owns schedule and this SOW |
| Contractor developer(s) | Design, build, test, and deploy the application |

### Responsibilities

RACIO matrix (**R**esponsible, **A**ccountable, **C**onsultable, **I**nformable, **O**mittable):

| Area of responsibility | Client owner | Branch manager | Host/receptionist | Contractor lead | Contractor dev |
|---|---|---|---|---|---|
| Approve scope & budget | A | C | O | R | I |
| Provide branch data (tables, hours, existing bookings) | I | R | C | A | I |
| Requirements clarification (backlog issues) | A | C | O | R | C |
| Development & testing | I | O | O | A | R |
| UAT / booking & cancellation test sign-off | A | R | C | R | C |
| Onboarding guide review | I | R | C | A | C |
| Go-live decision | A | C | I | R | I |
| Post-launch support (30 days) | I | C | C | A | R |

## Context

### Present

Fresh Fork operates three casual dining restaurants under one local brand. Reservations currently arrive through phone calls, WhatsApp messages, and handwritten notebooks, and each branch tracks them differently, so management has no shared view of table usage. This causes double bookings during peak evenings and forces staff to spend time manually checking availability and confirming bookings by hand. There is no dedicated IT team, and front-desk staff have limited technical training, so any solution must be simple to learn and must work on the laptops and phones staff already use — no new hardware or specialized tooling.

### Future

The RFP explicitly excludes food ordering, loyalty programs, advanced analytics, complex payment processing, and real-time SMS integrations from this engagement (see [Scope](#scope)). Several of these were raised as candidate backlog items during discovery (payment gateway integration, SMS reminders) and have been closed or descoped for this SOW rather than deferred silently — see issue [#19](https://github.com/ngonza27/trayectoria_dllo_software/issues/19) (closed as not planned) and issue [#15](https://github.com/ngonza27/trayectoria_dllo_software/issues/15) (email-only for MVP). Should Fresh Fork later want deposit collection, loyalty tracking, or an analytics dashboard beyond basic occupancy reporting, those would be scoped and budgeted as a follow-on phase once the core reservation system is stable and adopted.

## Planning

### Requirements

Detailed requirements are tracked as GitHub Issues in this repository, each written as a formal `SHALL` statement with acceptance criteria and traced back to a section of RFP-001, following the backlog convention in the project [README](../../README.md). The table below maps the RFP's stated needs to the current backlog, including the issues that were revised or added while preparing this SOW so the traceability stays accurate.

| RFP section / need | Backlog issue | Status |
|---|---|---|
| Staff login and role-based access (Suggested User Roles) | [#11](https://github.com/ngonza27/trayectoria_dllo_software/issues/11) | Rescoped from customer OAuth to staff accounts; `clarificacion-pendiente` on whether customer self-service is ever needed |
| Table reservation booking, no double-booking (2.2) | [#12](https://github.com/ngonza27/trayectoria_dllo_software/issues/12) | Ready |
| Reservation modification and cancellation (2.3) | [#13](https://github.com/ngonza27/trayectoria_dllo_software/issues/13) | Ready |
| Table and schedule management (2.4) | [#14](https://github.com/ngonza27/trayectoria_dllo_software/issues/14) | Ready |
| Notifications and reminders (2.5) | [#15](https://github.com/ngonza27/trayectoria_dllo_software/issues/15) | Revised: email-only, SMS removed (out of scope) |
| Admin dashboard and reporting (2.6) | [#16](https://github.com/ngonza27/trayectoria_dllo_software/issues/16) | Ready |
| System availability (4.1) | [#17](https://github.com/ngonza27/trayectoria_dllo_software/issues/17) | Revised down to 99.0%/business hours; still `tbd` pending hosting choice |
| Response time under load (4.2) | [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18) | Revised: concurrency estimate lowered to 30 staff users; still `tbd` |
| Payment/deposit integration (3.1) | [#19](https://github.com/ngonza27/trayectoria_dllo_software/issues/19) | **Closed** — explicitly out of scope per RFP |
| Audit trail (restriction) | [#20](https://github.com/ngonza27/trayectoria_dllo_software/issues/20) | Ready |
| WCAG 2.1 AA accessibility (restriction) | [#21](https://github.com/ngonza27/trayectoria_dllo_software/issues/21) | Ready |
| Multi-branch selection (Suggested MVP Scope) | [#23](https://github.com/ngonza27/trayectoria_dllo_software/issues/23) | New — phased rollout, single branch first |
| Shared customer history (Desired Outcome) | [#24](https://github.com/ngonza27/trayectoria_dllo_software/issues/24) | New |
| Common browsers / low-training UI (Constraints) | [#25](https://github.com/ngonza27/trayectoria_dllo_software/issues/25) | New |
| Staff onboarding guide (Deliverables Expected) | [#26](https://github.com/ngonza27/trayectoria_dllo_software/issues/26) | New |
| Testing evidence (Deliverables Expected) | [#27](https://github.com/ngonza27/trayectoria_dllo_software/issues/27) | New |

Work follows the two-phase sequence described in [Scope](#scope): Phase 1 (single branch) must reach a fully passing test suite (issue [#27](https://github.com/ngonza27/trayectoria_dllo_software/issues/27)) before Phase 2 (multi-branch, issue [#23](https://github.com/ngonza27/trayectoria_dllo_software/issues/23)) begins. Each issue's acceptance criteria are the method of acceptance for that unit of work; milestone-level acceptance additionally requires a client review meeting and written sign-off, per [Payment](#payment).

## Other terms and conditions

### Client's obligations

- Designate one point of contact per branch who can answer questions about current table layout, capacity, and operating hours within 3 business days of a request.
- Provide existing reservation data (notebooks, WhatsApp logs, or spreadsheets) needed to seed initial table/branch configuration; the contractor is not responsible for reconstructing historical bookings not provided.
- Review and comment on draft deliverables (design mockups, onboarding guide draft, test evidence) within 5 working days of receipt.
- Make at least one staff member per branch available for a 1-hour training/feedback session before go-live.
- Confirm the two `tbd` items (hosting tier / availability target on issue [#17](https://github.com/ngonza27/trayectoria_dllo_software/issues/17), and branch staff headcount on issue [#18](https://github.com/ngonza27/trayectoria_dllo_software/issues/18)) before the end of M1.

## Schedule

### Expected start date and completion date

The services of the contractor will be required for a period of approximately 10 weeks, commencing on or about **2026-08-25**, with expected completion on or about **2026-11-03**, followed by 30 days of post-launch support ending on or about **2026-12-03**. Indicative milestone dates:

| Milestone | Target date |
|---|---|
| M1 – Discovery & Analysis (SOW sign-off, clarifications resolved) | 2026-09-01 |
| M2 – Core Features (single-branch booking live in staging) | 2026-09-29 |
| M3 – Technical Proposal (multi-branch, onboarding guide, test evidence) | 2026-10-27 |
| Go-live (all three branches) | 2026-11-03 |
| Post-launch support ends | 2026-12-03 |

This estimate assumes no more than 2 rounds of revision per deliverable and a maximum of 20 billable hours per week from the contractor's side.

### Sign-off

**Work Authority:** Contractor Project Lead — contact details recorded in the `people.md` document referenced in [People](#people).

NOTE: Before signing the Statement of Work, if you have any questions or concerns, please call the Work Authority indicated above to negotiate any issues.

If you agree to the requirements of this Statement of Work, please sign and date the document which will be accepted as your proposal by Client, and return to my attention.

Please return an original signature copy by mail.

Printed Name:

Nicolas Gonzalez & Carlos Teza

Signature:

__________________________________________

Date:

11/08/2026
