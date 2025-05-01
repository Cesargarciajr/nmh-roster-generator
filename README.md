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


## Table of Contents
- [Epic 1: Staff Roster Generation](#-epic-1-staff-roster-generation)
- [Epic 2: Staff Management](#-epic-2-staff-management)
- [Epic 3: Shift Management](#-epic-3-shift-management)
- [Epic 4: Rule Engine for Allocation](#-epic-4-rule-engine-for-allocation)
- [Epic 5: Reporting & Analytics](#-epic-5-reporting--analytics)
- [Epic 6: Manual Override & Editing](#-epic-6-manual-override--editing)
- [Epic 7: Notifications & Audit Trail](#-epic-7-notifications--audit-trail)

## Epics

### 🧩 **Epic 1: Staff Roster Generation**
**Goal:** Automatically generate fair, efficient, and rules-compliant weekly staff rosters.

#### Key User Stories:
- As a scheduler, I want to automatically generate weekly rosters based on shift patterns, so I don't have to do it manually.
- As a system, I must ensure full-time staff work 39 hours per week with one “short day” per week.
- As a system, I must follow part-time patterns (2-day/3-day alternating weeks) without short days.
- As a system, I must ensure that weeks run from Monday to Sunday.
- As a system, I must ensure full-time staff get one weekend off per 4-week cycle, based on a predefined rotation group (Week 1, Week 2, etc.).
- As a scheduler, I want to assign each full-time staff member to a fixed weekend-off group (Week 1–4) that repeats every four weeks.
- As a system, I must determine the current week number in the 4-week cycle to ensure correct weekend-off allocation.
- As a scheduler, I need the system to consider staff holidays, sick leave, and other leave types during roster generation.
- As a system, I must ensure fair rotation of staff across eligible units unless marked as fixed.
- As a system, I must restrict staff from being scheduled into units they’re not trained for.
- As a system, I must ensure only female staff are assigned to gender-restricted areas.

### 🧩 **Epic 2: Staff Management**
**Goal:** Manage all staff details, contracts, and preferences.

#### Key User Stories:
- As an admin, I want to register staff with ID, name, gender, contract type, and training/unit restrictions.
- As an admin, I want to assign each full-time staff member to a weekend-off rotation group (Week 1–4).
- As an admin, I want to view and update staff work history to help inform fair allocation.
- As an admin, I want to assign unit restrictions and mark staff as fixed to a unit or eligible for rotation.
- As an admin, I want to book holidays and other leave types for staff.
- As an admin, I want to enter and track specific day-off requests.

### 🧩 **Epic 3: Shift Management**
**Goal:** Define and manage shift structures.

#### Key User Stories:
- As an admin, I want to define standard day, evening, and night shifts.
- As a system, I must match shift lengths with contract hours (e.g., full-time = 39h/week).
- As a system, I should ensure that no one works overlapping shifts or violates rest period rules (future-proofing).

### 🧩 **Epic 4: Rule Engine for Allocation**
**Goal:** Build a flexible rule engine to enforce hospital policies and scheduling fairness.

#### Key User Stories:
- As a scheduler, I want to define rules for short days, day-off positioning, and leave prioritization.
- As a system, I must enforce weekend-off rotations for full-time staff based on their assigned week group.
- As a system, I must determine the correct 4-week cycle position to enforce weekend-off fairness.
- As a system, I must enforce maximum weekly hours and track under/over time.
- As a system, I must ensure fairness in shift allocation (e.g., rotate unpopular shifts evenly).
- As a system, I must enforce gender-based and skill-based allocation constraints.

### 🧩 **Epic 5: Reporting & Analytics**
**Goal:** Generate insights and reports on staff distribution, workload, and history.

#### Key User Stories:
- As a manager, I want to generate reports showing hours worked per staff per week.
- As a manager, I want to see the distribution of shifts across the team (e.g., % of night shifts per staff).
- As a manager, I want to visualize unit allocation per staff over time.
- As a manager, I want to track weekend-off assignments across 4-week cycles to ensure fairness.
- As a system, I want to track compliance with contract hours and alert for deviations.

### 🧩 **Epic 6: Manual Override & Editing**
**Goal:** Allow human intervention and customization of generated rosters.

#### Key User Stories:
- As a scheduler, I want to manually adjust the generated roster before finalizing.
- As a scheduler, I want to override specific allocations in case of emergencies or staff swaps.
- As a system, I must recalculate impacts (e.g., hours, fairness, etc.) if overrides happen.

### 🧩 **Epic 7: Notifications & Audit Trail**
**Goal:** Track changes and alert stakeholders when needed.

#### Key User Stories:
- As a system, I must log all changes made to a roster or staff record.
- As a scheduler, I want to notify staff of their assigned shifts.
- As a system, I must alert managers when leave exceeds available balance or causes understaffing.

