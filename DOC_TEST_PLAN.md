# API Governance System - Test Plan

## 1. Introduction
This test plan serves as a blueprint for verifying the functional and non-functional specifications of the API Governance System, targeting the core interactions, data isolation rules, alerting parameters, and cloud stability.

## 2. Test Environments
*   **Local Development:** `127.0.0.1:5000` via Windows CLI (`python app.py`)
*   **Production Deployment:** `http://angelack.pythonanywhere.com`

## 3. Core Test Cases

### 3.1 Authentication & RBAC Rules
| Test ID | Scenario | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **TC-1** | Valid Admin Login | Select "Angela Kasoha", Enter `1234`. | Success. Redirect to Dashboard. Topbar contains Chaos button. Left nav contains Team, Alerts, Audit. | [ ] |
| **TC-2** | Invalid Admin Login | Select "Angela Kasoha", Enter `9999`. | Rejects login. Presents error string "Invalid Administrator PIN". | [ ] |
| **TC-3** | Standard User Access | Select developer account (e.g., "Alice Mwangi"). Input no pin. | Success. Redirect to Dashboard. Sidebar heavily constrained (No Team, No Alerts, No Audit, No Chaos Button). | [ ] |
| **TC-4** | Export Restriction | As a standard user, attempt to navigate directly to `/export/alerts`. | Server denies data execution and forcibly redicts user to `/`. | [ ] |

### 3.2 Component and Data Manipulation
| Test ID | Scenario | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **TC-5** | Dashboard Rendering | Successfully log in. | The UI immediately loads the clock module, usage metrics, and Chart.js line graph displaying recent trends. | [ ] |
| **TC-6** | Create New API | Navigate to "Services". Fill out name and parameters. Press submit. | Backend executes INSERT operation. Page refreshes and API displays immediately on the registry graph layout. | [ ] |
| **TC-7** | Delete API Integrity | Press the trash icon on the test API generated in TC-6. Confirm prompt. | System deletes the specific API and safely severs all associated foreign-key constraints (Access Logs & Alerts bound to the API). | [ ] |
| **TC-8** | Tab Persistence | Click "Resolve" on an active Alert situated within the Alerts tab. | JavaScript securely remembers active tab location using `sessionStorage`. Post-resolution, the site strictly returns you to the exact 'Alerts' tab instead of defaulting to Overview. | [ ] |

### 3.3 Dynamic Threat Handling (Chaos Hub & Alerts)
| Test ID | Scenario | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- |
| **TC-9** | Overage Alert Generation | Navigate to Team tab. Simulate manual usage on an API blowing past its defined `allowed_usage` cap. | `check_and_generate_alerts()` evaluates logic ratio > 1.0. Plops a "CRITICAL" tier warning aggressively onto the UI. | [ ] |
| **TC-10** | Chaos Spiking | Click topbar Chaos Button. Click "Traffic Spike". | Network logs immense payload simulation. Global latency spikes visually. `check_and_generate_alerts` is triggered. | [ ] |
| **TC-11** | Chaos Outage | Click topbar Chaos Button. Click "Service Outage". | System violently crashes a chosen gateway's metric to 0ms latency, paints status tag Red ('Offline'). Directly pipes a critical database alert logging the dead line. | [ ] |
| **TC-12** | System Stabilization | Open Chaos Hub -> Trigger "Stabilize". | System neutralizes latency metrics and securely wipes all synthetic "CHAOS OUTAGE" alerts via targeted query deletion without deleting legitimate user warnings. | [ ] |

## 4. Automation Notice
While testing on specific hosting constraints like PythonAnywhere relies predominantly on manual checks, future revisions of the platform test plan should adapt Selenium WebDriver to construct programmatic E2E (End-to-End) validation checks scaling across multiple OS footprints.
