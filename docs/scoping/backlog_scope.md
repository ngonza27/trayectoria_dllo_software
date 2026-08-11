# Backlog Refinado — RFP-001: Restaurant Reservation System

**Reference:** RFP-001 · [SOW.md](../SOW.md) · [mvp_scope.md](./mvp_scope.md)

## 5. Backlog Refinado

| Issue | User Story | Acceptance Criteria |
|---|---|---|
| RES-001: Create Reservation | As a host, I want to create a reservation so that I can record customer bookings digitally. | User can enter customer name, phone, branch, date, time, and party size. System saves the reservation. Reservation appears in the calendar/list view. |
| RES-002: Check Availability | As a host, I want to check availability by date, time, branch, and party size so that I avoid double bookings. | User can search availability using date, time, branch, and party size. System shows whether the slot is available. System prevents booking if capacity is exceeded. |
| RES-003: Update Reservation | As a host, I want to edit an existing reservation so that I can handle customer changes. | User can modify date, time, party size, branch, contact data, and notes. Updated reservation is saved. Calendar/list view reflects the change. |
| RES-004: Cancel Reservation | As a host, I want to cancel a reservation so that the slot becomes available again. | User can mark a reservation as cancelled. Cancelled reservation no longer blocks availability. Cancellation status is visible in reservation history. |
| RES-005: View Reservation Calendar | As a manager, I want to see reservations in a shared calendar or list so that I can understand table usage. | User can filter reservations by branch and date. Reservations display time, customer name, party size, and status. View works on laptop and mobile browser. |
| RES-006: Manage Reservation Status | As staff, I want to update reservation status so that the team knows what happened with each booking. | Supported statuses include confirmed, seated, cancelled, no-show, and completed. Status changes are saved. Status is visible in the reservation list. |
| RES-007: View Customer History | As a receptionist, I want to see basic customer history so that repeat customers can be recognized. | User can search by customer name or phone. System shows previous reservations. Customer contact data is displayed. |
| RES-008: Staff Login / Basic Roles | As a manager, I want staff to access the system with basic roles so that usage is controlled. | Host/receptionist can manage reservations. Manager can view all reservations and basic reports. Unauthorized users cannot access reservation data. |
| RES-009: Staff Onboarding Guide | As a manager, I want a simple guide so that staff can learn the system quickly. | Guide explains how to create, update, cancel, and check reservations. Guide includes screenshots or step-by-step instructions. Guide is short and easy to follow. |
| RES-010: Booking Workflow Tests | As the project team, we want testing evidence so that the client can trust the MVP. | Test cases cover create, update, cancel, and availability check. Evidence includes screenshots or documented results. Critical bugs are fixed before delivery. |
