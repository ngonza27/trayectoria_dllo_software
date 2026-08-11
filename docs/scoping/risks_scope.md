# Riesgos, Supuestos y Dependencias — RFP-001: Restaurant Reservation System

**Reference:** RFP-001 · [SOW.md](../SOW.md) · [mvp_scope.md](./mvp_scope.md)

## 4. Riesgos, Supuestos y Dependencias

### Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Staff may find the system difficult to use. | Low adoption; staff may return to notebooks or WhatsApp. | Keep UI simple, test with staff, create onboarding guide. |
| Availability rules may be unclear or different per branch. | Incorrect bookings or continued double bookings. | Confirm table capacity, time slots, and branch rules during discovery. |
| Scope may grow beyond the MVP. | Delays and unfinished features. | Clearly separate IN, OUT, LATER, and UNKNOWN scope. |
| Mobile browser experience may be poor. | Staff may struggle during busy service hours. | Design responsive screens and test on common phones. |
| Customer data may be duplicated or incomplete. | Customer history becomes less useful. | Use phone number as a simple identifier in MVP. |

### Assumptions

| Assumption | Why It Matters |
|---|---|
| Staff will manually enter reservations received by phone or WhatsApp. | Avoids complex integrations in the MVP. |
| The MVP does not need payment processing. | Keeps the project aligned with the RFP constraints. |
| A shared calendar/list view is enough for the first version. | Avoids building a complex table floor plan. |
| Managers can define branch schedules and capacity rules before development. | Required for accurate availability checking. |
| The system will be used by a small number of staff members. | Simplifies user management and permissions. |

### Dependencies / Pending Decisions

| Dependency or Decision | Owner |
|---|---|
| Confirm whether MVP starts with one branch or all three branches. | Client / Manager |
| Confirm table capacity, time slots, and reservation duration rules. | Restaurant Manager |
| Decide required customer fields for MVP. | Client / Project Team |
| Confirm role permissions for host/receptionist vs manager. | Client / Project Team |
