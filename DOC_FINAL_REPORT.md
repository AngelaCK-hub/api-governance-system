# API Governance System - Final Report Document

## 1. Executive Summary
The API Governance System project was initiated to build a comprehensive dashboard allowing organizations to track, govern, and monitor their internal and external API gateways. The final product successfully meets all core requirements, offering real-time usage visualization, automated anomaly alerting, role-based security, and a robust "Chaos Hub" for system stress testing. The backend is powered by Python/Flask, running entirely on a lightweight SQLite database. The project was successfully brought to a close with a stable deployment on the PythonAnywhere cloud platform.

## 2. Project Objectives Met
*   **API Registry Management:** Functionality securely embedded to allow Administrators to register, update, and remove service endpoints from the pool.
*   **Traffic & Usage Limits:** Each API enforces unique `allowed_usage` capacities. 
*   **Alert Engine:** Built-in cron logic automatically evaluates current usage against allowed caps, generating "Warning" alerts at 75% capacity and "Critical" alerts at 100%.
*   **Chaos Engineering Hub:** The system successfully ships with a dedicated diagnostic pane where admins can inject virtual traffic spikes or simulate dead latency (API Outages) to verify the system's reaction and alerting pipeline.
*   **Reporting:** Full comma-separated-value (CSV) export systems integrated to dump Registry data, Usage Logs, Alerts, and Audit Trails natively out of the dashboard.
*   **Deployment:** Successfully bridged from local development to a live GitHub repository, and finally deployed into production on PythonAnywhere.

## 3. Challenges & Resolutions

### 3.1 UX Regression on Action Handling
**Challenge:** Initially, taking actions (such as Resolving an alert, or adding a new API) required a traditional server POST, which refreshed the page. Because the entire platform is a custom multi-tab layout without proper Single Page App (SPA) backend integration, users were constantly shifted back to the 'Overview' tab after taking actions on deeper tabs (like 'Alerts'). 
**Resolution:** Implemented `sessionStorage` in the JavaScript `switchSection` handler. The user's active tab is recorded continuously. Upon any server-side reload or redirect, the browser immediately evaluates the session storage and restores the user to their original working tab.

### 3.2 Secure Data Retrieval Policies
**Challenge:** Data exports were originally secured loosely, simply ensuring the requester was logged in. This exposed sensitive internal audit trails and organizational API usage metrics to standard developer accounts.
**Resolution:** Re-designed the Flask `@app.route` handlers to strictly enforce Role-Based Access Control (RBAC). Only authenticated users actively holding the "Admin" or "Manager" roles are permissible to query the `/export/` routes.

### 3.3 Chaos alerting failures
**Challenge:** The initial design of the Chaos Hub performed database mutations directly, successfully simulating outages and traffic visually on the dashboard but failing to invoke the underlying `check_and_generate_alerts()` engine. 
**Resolution:** Programmed the system to organically trigger manual alerts upon outage, and chained the native system alert function to execute directly subsequent to any virtual traffic spike payload dump.

## 4. Conclusion
The API Governance System represents a production-ready template for API monitoring. The deployment onto PythonAnywhere effectively abstracts hosting complexity, leveraging its persistent file system storage so that the SQLite database natively handles production workloads without complicated PostgreSQL migration steps. The system fulfills both dynamic user-experience guidelines and critical security isolation requirements seamlessly.
