# API Governance System - User Manual

## 1. Accessing the System
1. Navigate to the live web address (`http://angelack.pythonanywhere.com` or your local development server at `http://127.0.0.1:5000`).
2. **Login:** Select your name from the dropdown. 
   *(Note: Core administrative roles such as "Angela Kasoha" are protected. Input the PIN `1234` to successfully log in).*

## 2. Navigating the Dashboard
The system utilizes a persistent dark-mode layout with a sidebar navigation pane containing five modules:
*   **Overview:** Provides a real-time aggregate of total active APIs, API calls, active warnings, latency readings, and a 7-day usage graph.
*   **Services:** Contains the API Registry logic to add, edit, and maintain gateways.
*   **Team:** (Admin/Manager only) Directory of onboarded team members and roles.
*   **Alerts:** (Admin/Manager only) Aggregated hub for Warning and Critical alerts.
*   **Audit Trail:** (Admin/Manager only) Highly detailed accounting of every system mutation.

## 3. Managing APIs and Users
### Registering an API (Admin)
1. Go to the **Services** tab.
2. In the "Register Service" card, type the API Name, Description, Allowed Usage (limit until alerts trigger), and Cost per call.
3. Click **Register Service**. It will immediately appear in the active UI.

### Editing or Deleting an API/User (Admin)
1. Navigate to either **Services** or **Team**.
2. Locate the entity on the master table.
3. On the far right column, click the **Pencil Icon** to open the Edit Modal.
4. Click the **Red Trash Icon** to permanently delete the user or API (requires confirmation). Note: deleting an entity securely strips all attached history and log cascades for system sanitation.

## 4. Handling System Alerts
1. Open the **Alerts** tab.
2. An alert generates automatically if an API is approaching 75% usage capacity (Warning) or hits 100% (Critical).
3. Review the alert timestamp and root cause.
4. If the incident is acknowledged, press **Resolve**. The alert tag will switch to a green *Resolved* badge and disappear from the active queue.

## 5. Generating Reports
1. Navigate to the section you wish to export (Services, Alerts, or Audit Trail).
2. Locate the **CSV Export** button sitting parallel to the section title (depicted by a download icon).
3. Clicking the button securely packages the SQLite data into a format suitable for Excel or Numbers and automatically pipes the file to your local computer's download folder.

## 6. Utilizing the Chaos Hub (Admin Only)
The Chaos Hub is an advanced engineering tool designed to verify system integrity and test the warning boundaries.
1. From any tab on the dashboard, click the **Chaos** lightning-bolt button situated in the top right Topbar.
2. A specialized Modal will appear.
3. **Trigger Traffic Spike:** Sends a global blitz wave heavily bloating traffic to random active APIs while degrading latency metrics up to 5x. Verifies threshold warning systems.
4. **Service Outage:** Randomly assassinates an active service entirely, verifying catastrophic critical alert handlers.
5. **Stabilize:** Instantly revitalizes all downed networks, zeroes out artificial latencies and mass deletes any alerts generated explicitly from the Outage sequence.
