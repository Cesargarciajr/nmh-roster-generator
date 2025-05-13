# NMH Roster Generator

A staff management and roster scheduling system for maternity hospitals. This application automates roster generation, ensuring fair and efficient shift allocation based on rules such as full-time/part-time contracts, leave management, and unit-specific restrictions.

## Modular Structure

This project is divided into several core apps, each focusing on a specific functionality:

- **Staff Management**: Handles all staff details, contracts, preferences, and historical data.
- **Roster Generation**: Responsible for creating weekly staff rosters, considering shifts, leave, and weekend rotations.
- **Allocation Engine**: Manages the allocation of staff to specific units, considering gender, training, and rotation rules.
- **Shift Management**: Defines and manages various shift types, ensuring compliance with staff contracts and rest periods.
- **Reporting & Analytics**: Generates reports on staff work history, shift distributions, and compliance with contract hours.
- **Manual Override & Editing**: Allows for manual adjustments and overrides of automatically generated rosters.
- **Notifications & Audit Trail**: Tracks all changes made to rosters and staff records, and sends notifications to staff and managers.

---

## 🧩 Epic 1.1: Staff Registration
🎯 **Goal:** Allow administrators to register new staff members with all required attributes.

### Key User Stories:
- As an admin, I want to register new staff members by entering their:
  - Staff Name
  - Weekend Group (1–4)
  - Shift Period Assigned (D1, D2, D3, E, N)
  - Gender (Male/Female)
  - Unit Restrictions
  - **Assigned Unit** (if the staff works only in a specific unit)
  - Contract Type (Full-time/Part-time)
  - Status (default to Active)

- As a system, I must:
  - Auto-generate a unique Staff ID
  - Validate all required fields before saving

---

## 🧩 Epic 1.2: Staff Listing & Detail View
🎯 **Goal:** Provide a clear overview of all registered staff with summary and detail views.

### Key User Stories:
- As an admin, I want to view all staff in a table/list showing:
  - Staff ID
  - Staff Name
  - Status (Active/Inactive)
  - Contract Type
  - Gender

- As an admin, I want to click on a staff entry to view the full profile for more detailed information and editing access.

- As a system, I must:
  - Display up-to-date information from the database
  - Paginate or search/filter if the list grows large

---

## 🧩 Epic 1.3: Staff Profile Management
🎯 **Goal:** Allow the editing of staff information after registration.

### Key User Stories:
- As an admin, I want to edit a staff member’s:
  - Name
  - Weekend Group
  - Shift Period
  - Gender
  - Unit Restrictions
  - **Assigned Unit**
  - Contract Type
  - Status (Active/Inactive)

- As a system, I must:
  - Prevent duplicate Staff IDs
  - Ensure updates do not corrupt related data

---

## 🧩 Epic 1.4: Staff Deletion
🎯 **Goal:** Safely remove staff members from the system when no longer needed.

### Key User Stories:
- As an admin, I want to delete staff records

- As a system, I must:
  - Prevent deletion if the staff is linked to critical data
  - Prompt the admin with a warning before deleting
---




