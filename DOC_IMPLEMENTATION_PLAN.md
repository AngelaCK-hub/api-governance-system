# API Governance System - Implementation Plan

## 1. Project Overview
The API Governance System is a web-based dashboard designed to monitor, manage, and govern API access. It provides real-time traffic observation, role-based access control, automated alert generation based on usage limits, and a "Chaos Hub" to simulate anomalies.

## 2. Technology Stack
*   **Backend:** Python 3.10 with Flask (WSGI framework)
*   **Database:** SQLite3 (Serverless, file-based database for simplicity and portability)
*   **Frontend:** HTML5, Vanilla CSS3 (Custom design system), Vanilla JavaScript
*   **Data Visualization:** Chart.js (for rendering API usage graphs and pie charts)
*   **Icons:** Lucide Icons
*   **Hosting/Deployment:** PythonAnywhere (Free tier with persistent storage), GitHub for version control.

## 3. Implementation Phases

### Phase 1: Foundation and Database Schema
*   **Objective:** Establish the data models.
*   **Actions:** 
    *   Initialize SQLite database (`governance.db`).
    *   Create tables: `apis`, `users`, `access_logs`, `alerts`, `audit_log`.
    *   Create `init_db()` and `seed_sample_data()` functions to auto-populate the database with test data (Users, APIs, and fake 14-day history) on initial startup.

### Phase 2: Core Backend Logic (Flask)
*   **Objective:** Develop the routing, logic, and middleware.
*   **Actions:**
    *   Implement `@login_required` middleware for security.
    *   Create the main `dashboard()` route to aggregate statistics across the APIs and users.
    *   Develop API endpoints for generating Chart.js aggregate data.
    *   Implement CRUD operations for APIs (Add, Edit, Delete).
    *   Implement CRUD operations for Team Members/Users.

### Phase 3: Frontend Interface & UX
*   **Objective:** Build a premium, dark-mode focused UI.
*   **Actions:**
    *   Design a responsive layout with a persistent sidebar and topbar.
    *   Implement single-page-application (SPA) feel using JavaScript to switch tabs (Overview, Services, Team, Alerts, Audit Trail) without full page reloads.
    *   Enhance UX with `sessionStorage` to ensure form submissions return the user to their active tab rather than defaulting to the Overview dashboard.
    *   Integrate Chart.js line and doughnut charts.

### Phase 4: Advanced Features (Chaos Hub & Export)
*   **Objective:** Implement simulation and reporting layers.
*   **Actions:**
    *   Build "Chaos Hub" to allow Admins to intentionally simulate traffic spikes or API outages.
    *   Tie Chaos Hub directly to the alerting engine so simulated outages instantly generate system alerts.
    *   Implement CSV export functionality using Python's native `csv` and `io` libraries to dump DB queries for off-platform reporting.
    *   Secure export routes based on specific Roles (Admin/Manager).

### Phase 5: Deployment
*   **Objective:** Launch the application tracking real-life availability.
*   **Actions:**
    *   Push local code to a GitHub repository.
    *   Configure PythonAnywhere virtual environment (`mkvirtualenv --python=/usr/bin/python3.10`).
    *   Configure the WSGI interface to properly target the application path (`/home/username/api-governance-system`).
    *   Perform end-to-end cloud environment verification.

## 4. Security Architecture
*   **Authentication:** Basic PIN protection (SHA-256 hashed) securely separating regular Users from Administrators.
*   **Role-Based Access Control (RBAC):** Strict view and edit permissions assigned. Developers cannot export system data, delete users, or interact with Chaos Hub. Managers can export data, but cannot trigger Chaos. Admins retain full control. 
*   **Audit Trail:** Every major modification (Login, Create API, Delete User, Chaos Triggers) is permanently recorded in the immutable `audit_log` table.
