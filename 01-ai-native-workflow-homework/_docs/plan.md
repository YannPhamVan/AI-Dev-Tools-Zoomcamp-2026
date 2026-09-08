# Shared Household Chores — MVP Specification

## 1. Recurring Chore Management

- The application manages daily, weekly, and monthly recurring chores.
- Each chore is assigned to a family member.
- A chore has a name, frequency, and start date.
- Weekly and monthly chores can be assigned to a specific day or be flexible within their period.
- The user can create, edit, and delete chores.
- Family members are predefined, with a name and a role (`parent` or `child`).

## 2. Chore Tracking and Validation

- Each chore occurrence has one of four statuses:
  - `To do`
  - `Pending validation`
  - `Overdue`
  - `Validated`
- A family member can mark a chore as completed.
- The single application user acts as the administrator and validates completed chores.
- A chore becomes `Overdue` at the end of its due day.
- A chore completed after its due date remains identified as having been overdue.
- The dashboard displays chores grouped by status.
- Validated chores remain visible for simple tracking.

## Out of Scope for the MVP

- Authentication / PIN
- Notifications
- Points and gamification
- Rewards
- Automatic chore rotation
- Chore exchanges
- Family member CRUD
- Detailed history and statistics
- Multiple households