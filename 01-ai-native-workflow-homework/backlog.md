# Shared Household Chores — Development Backlog (Django)

Based on the MVP specification in `_docs/plan.md`, this backlog outlines the tasks required to implement the application using Django.

---

## Phase 1: Project Setup & Predefined Data

- [x] **TASK-01: Initialize Django Project and App**
  - Bootstrap Django project (`household_chores`) and application (`chores`).
  - Configure `INSTALLED_APPS` in `settings.py`.
  - Set up virtual environment (`.venv`), dependencies (`requirements.txt`), and `.gitignore`.
  - Configure root and app URL routing (`household_chores/urls.py` -> `chores/urls.py`).
  - Verify configuration with `manage.py check` and `manage.py test`.

- [x] **TASK-02: Predefined Family Members Setup**
  - Implement `FamilyMember` model with `name` and `role` (`parent` or `child`).
  - Create data migration `0002_seed_family_members` with predefined members (no CRUD required per MVP spec).
  - Register in Django Admin for quick verification.

---

## Phase 2: Data Models & Core Business Logic

- [x] **TASK-03: Chore and Occurrence Models**
  - **Chore Model**:
    - Fields: `name`, `frequency` (`daily`, `weekly`, `monthly`), `assigned_to` (`ForeignKey` to `FamilyMember`), `start_date`.
    - Scheduling attributes: `is_flexible` (boolean), `specific_day_of_week` (0-6), `specific_day_of_month` (1-31).
  - **ChoreOccurrence Model**:
    - Fields: `chore` (`ForeignKey`), `due_date`, `status` (`To do`, `Pending validation`, `Overdue`, `Validated`).
    - Tracking fields: `completed_at`, `completed_by`, `was_overdue` (boolean), `validated_at`.
    - Unique constraint on `(chore, due_date)`.

- [x] **TASK-04: Recurrence & Occurrence Generation Service**
  - Implement logic to compute and generate chore occurrences from `start_date` up to a target horizon:
    - **Daily**: Consecutive daily occurrences.
    - **Weekly**: Specific weekday or flexible (due at the end of the weekly period, Sunday).
    - **Monthly**: Specific day of month or flexible (due on the last day of the month).
  - Ensure idempotent generation (`get_or_create`).

- [x] **TASK-05: Status Lifecycle and Overdue Management**
  - Implement automatic detection of overdue occurrences (status transitions from `To do` to `Overdue` when current date passes `due_date`).
  - Implement completion logic (`mark_completed`):
    - Sets status to `Pending validation`.
    - Sets `was_overdue = True` if completed past `due_date` or from `Overdue` state.
  - Implement validation logic (`validate`):
    - Sets status to `Validated` by administrator.
    - Preserves `was_overdue` indicator for display.

---

## Phase 3: Recurring Chore Management (CRUD)

- [x] **TASK-06: Chore Management Views and Forms**
  - Create `ChoreForm` with validation for frequency and specific day selection.
  - Build `ChoreListView` to view all active recurring chores.
  - Build `ChoreCreateView` to define new recurring chores and trigger initial occurrence generation.
  - Build `ChoreUpdateView` to edit chore definitions.
  - Build `ChoreDeleteView` with confirmation to remove chores and future occurrences.

---

## Phase 4: Dashboard & Chore Tracking Workflow

- [x] **TASK-07: Tracking Dashboard**
  - Build main dashboard view displaying chore occurrences grouped by status:
    1. **To do** (upcoming / due today)
    2. **Overdue** (due date has passed without completion)
    3. **Pending validation** (completed, awaiting admin approval)
    4. **Validated** (completed and approved, remains visible for tracking)
  - Refresh occurrence statuses on dashboard load.

- [x] **TASK-08: Completion and Validation Actions**
  - Add quick action button for family members: "Mark as Completed" (with member selector or toggle).
  - Add quick action button for admin: "Validate Chore".
  - Display distinct visual badge/indicator for chores completed after the due date (`was_overdue`).

---

## Phase 5: UI Styling & Verification

- [x] **TASK-09: User Interface & Templates**
  - Design clean, mobile-friendly templates using responsive CSS/Bootstrap.
  - Add navigation between Dashboard and Chore Management.
  - Add status badge colors:
    - `To do`: Blue/Neutral
    - `Overdue`: Red/Amber
    - `Pending validation`: Yellow/Orange
    - `Validated`: Green (with Overdue indicator if applicable)

- [x] **TASK-10: Automated Tests & Verification**
  - Write model and service tests:
    - Occurrence calculation for daily, weekly, and monthly (flexible vs fixed).
    - Overdue transition on due date expiration.
    - Retention of `was_overdue` flag upon completion and validation.
  - Write view and workflow tests for chore CRUD and completion/validation flow.
