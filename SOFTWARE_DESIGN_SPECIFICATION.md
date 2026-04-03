# SOFTWARE DESIGN SPECIFICATION
## API Governance System

**Prepared by:** Angela Kasoha  
**Date:** February 27, 2026  
**Version:** 1.0  
**Programming Language:** Python 3  
**Framework:** Flask (Web Framework)  
**Database:** SQLite  

---

## 1.0 Introduction

This document provides the Software Design Specification (SDS) for the API Governance System. It describes how the system will be constructed — covering the data structures, system architecture, user interface, and individual component details. Think of this document as the "blueprint" that maps out *how* the software will work under the hood, building upon the requirements defined in the Software Requirements Specification (SRS).

The API Governance System will be a web-based dashboard application designed to help organizations keep track of their APIs (Application Programming Interfaces). It will allow users to register APIs, monitor how much they are being used, and automatically generate alerts when usage gets too high. According to Medjaoui et al. (2019), API governance is essential for ensuring that APIs remain consistent, secure, and aligned with business goals — and that is exactly what this system aims to achieve on a smaller, educational scale.

### 1.1 Goals and Objectives

The main goal of this project is to build a simple but functional API monitoring tool that demonstrates real-world governance concepts. Specifically, the system should be able to:

1. **Register APIs** — Allow users to add new APIs to a central catalog with details like name, description, usage limit, and cost per call.
2. **Manage Users** — Keep a list of people (developers, managers) who use the APIs.
3. **Track Usage** — Log every API call and show how much each API has been used over time.
4. **Generate Alerts Automatically** — The system should detect when an API is nearing its usage limit (75%) or has exceeded it (100%), and display warnings using a traffic-light color scheme (green, yellow, red).
5. **Show Visual Analytics** — Display charts that make it easy to understand usage patterns at a glance.
6. **Calculate Costs** — Show how much money each API has cost based on its usage and per-call pricing.

### 1.2 Statement of Scope

The API Governance System will be a web application that runs locally in a user's browser. Users will interact with it through a single dashboard page where they can view data, submit forms, and see charts.

**Major Inputs:**
- API details entered through a form (name, description, usage limit, cost per call)
- User information entered through a form (name, role)
- Usage simulation parameters (which API, which user, how many calls)

**Major Processing:**

| Priority | Feature | What It Will Do |
|----------|---------|----------------|
| **Essential** | API Registry | Users will be able to add and view APIs in a table |
| **Essential** | User Management | Users will be able to add people to the system |
| **Essential** | Usage Logging | The system will record how many times each API is called |
| **Essential** | Alert Engine | The system will check usage against limits and create warnings |
| **Essential** | Dashboard Rendering | All data will be displayed on a single web page |
| **Desirable** | Charts (Chart.js) | A line chart will show the 7-day usage trend; a doughnut chart will show per-API breakdown |
| **Desirable** | Alert Resolution | Users will be able to click "Resolve" to dismiss an alert |
| **Desirable** | Usage Simulation | A button will let users simulate API calls for demonstration purposes |
| **Future** | Login System | Password-protected access with different permissions per role |
| **Future** | Email Notifications | Sending alert emails when APIs exceed their limits |
| **Future** | Real API Integration | Connecting to an actual API gateway instead of simulating calls |

**Major Outputs:**
- A fully rendered HTML dashboard with statistics, tables, alerts, and charts
- A JSON API endpoint (`/api/chart_data`) that will feed data to the charts
- A persistent SQLite database file (`governance.db`) that will store all records

### 1.3 Software Context

In today's software industry, organizations rely heavily on APIs to connect their systems — from payment processing to notifications to user authentication. However, without proper oversight, API usage can spiral out of control, leading to unexpected costs and outages (Mathijssen & Overeem, 2023).

This system is intended to serve as a **learning tool** that demonstrates the core principles of API governance. In a real-world setting, software like Apigee, Kong, or AWS API Gateway would handle this at scale. Our system will capture the same *ideas* — cataloging, monitoring, alerting — in a lightweight package that a student can build, understand, and present.

It will be particularly useful for organizations that want to:
- Know which APIs they are using and how much they cost
- Set usage limits and get warned before they are exceeded
- Have a visual overview of API health across their team

### 1.4 Major Constraints

1. **No user authentication** — The initial version will not include login functionality. In a real system, this would need to be added for security purposes.
2. **SQLite is single-user** — SQLite cannot handle many people writing to it at the same time. For a production system, a database like PostgreSQL or MySQL would be more appropriate (Owens, 2006).
3. **Development server only** — Flask's built-in server is meant for testing, not for handling real traffic from hundreds of users.
4. **Simulated data** — We plan to generate fake API calls rather than intercepting actual network traffic. This keeps the project manageable within a semester.
5. **Semester time constraint** — The scope is limited to what can realistically be built, tested, and documented within one academic term.

---

## 2.0 Data Design

This section describes how data will flow through the system — what will be stored, what will be passed between functions, and how the database will be structured.

### 2.1 Internal Software Data Structure

These are the data structures that will be built *inside* the Python code and passed between functions. They will exist only in memory while a request is being processed.

**`api_data` list** — This will be the main data structure that the dashboard uses to display the API table. It will be constructed in the `dashboard()` function by combining information from the `apis` table and the `access_logs` table:

```python
# Each item in the api_data list will look like this:
{
    "id": 1,                    # Unique ID from the database
    "name": "Payment API",      # Name of the API
    "description": "Handles payments",  # What the API does
    "total_usage": 429,         # How many times it has been called (calculated)
    "allowed_usage": 500,       # The maximum number of calls allowed
    "cost_per_call": 0.05,      # How much each call costs in dollars
    "total_cost": 21.45,        # total_usage × cost_per_call (calculated)
    "usage_percent": 85.8,      # (total_usage ÷ allowed_usage) × 100 (calculated)
    "status": "warning"         # "safe", "warning", or "critical" (calculated)
}
```

**`chart_data` dictionary** — This will be sent to the browser as JSON so that Chart.js can draw the graphs:

```python
{
    "labels": ["Feb 18", "Feb 19", "Feb 20", ...],   # Last 7 days
    "values": [320, 450, 580, ...],                   # Total calls per day
    "api_usage": [                                     # Per-API totals
        {"name": "Payment API", "usage": 429},
        {"name": "Notification API", "usage": 844},
        ...
    ]
}
```

### 2.2 Global Data Structure

These variables will be defined at the top of `app.py` and will be available to every function in the program:

| Variable | Type | What It Will Hold |
|----------|------|-------------------|
| `app` | Flask object | The main application instance that will handle all web requests |
| `DB_PATH` | String | The file path to the database: `"db/governance.db"` |

### 2.3 Temporary Data Structure

These will be short-lived variables that only exist while a specific function is running:

| Variable | Where It Will Exist | What It Will Do |
|----------|---------------------|-----------------|
| `conn` | Inside any function that talks to the database | A connection to SQLite; will be created by `get_db()` and closed after the query is done |
| `c` | Inside `init_db()` and `seed_sample_data()` | A cursor object that will execute SQL commands |
| `labels` and `values` | Inside `chart_data()` | Temporary lists that will accumulate the 7 days of chart data before being sent as JSON |
| `api_data` | Inside `dashboard()` | A temporary list of dictionaries to be built during the request, then passed to the HTML template |

No temporary files will be created on disk. Everything temporary will live in RAM and disappear when the request is finished.

### 2.4 Database Description

The database will be stored as a single file called `governance.db` inside the `db/` folder. It will be created automatically the first time the application runs. We have chosen SQLite because it requires zero setup — no server installation, no configuration files, just a single `.db` file (Owens, 2006).

The database will contain **four tables**, described below with enough detail to recreate them:

#### Table: `apis` — Will store information about each registered API

| Column | Data Type | Constraints | What It Will Store |
|--------|-----------|-------------|-------------------|
| id | INTEGER | PRIMARY KEY, auto-increments | A unique number for each API (1, 2, 3...) |
| name | TEXT | NOT NULL (required) | The API's name, e.g. "Payment Gateway API" |
| description | TEXT | Optional | A short explanation of what the API does |
| allowed_usage | INTEGER | Default: 1000 | The maximum number of calls allowed before alerts trigger |
| cost_per_call | REAL | Default: 0.01 | How much each call costs, in dollars |

#### Table: `users` — Will store information about people who use the APIs

| Column | Data Type | Constraints | What It Will Store |
|--------|-----------|-------------|-------------------|
| id | INTEGER | PRIMARY KEY, auto-increments | A unique number for each user |
| name | TEXT | NOT NULL | The person's full name |
| role | TEXT | NOT NULL | Their role: "Developer", "Manager", or "Admin" |

#### Table: `access_logs` — Will record every time an API is called

| Column | Data Type | Constraints | What It Will Store |
|--------|-----------|-------------|-------------------|
| id | INTEGER | PRIMARY KEY, auto-increments | A unique number for each log entry |
| user_id | INTEGER | Foreign key → users(id) | Which user made the call |
| api_id | INTEGER | Foreign key → apis(id) | Which API was called |
| timestamp | DATETIME | Default: current time | When the call happened |
| usage_count | INTEGER | Default: 1 | How many calls this entry represents |

#### Table: `alerts` — Will store warnings when APIs approach or exceed their limits

| Column | Data Type | Constraints | What It Will Store |
|--------|-----------|-------------|-------------------|
| id | INTEGER | PRIMARY KEY, auto-increments | A unique number for each alert |
| type | TEXT | NOT NULL | "warning" (75-99%) or "critical" (100%+) |
| api_id | INTEGER | Foreign key → apis(id) | Which API the alert is about |
| user_id | INTEGER | Foreign key → users(id) | Related user (can be empty) |
| status | TEXT | Default: "new" | "new" or "resolved" |
| message | TEXT | Optional | A human-readable message describing the alert |
| timestamp | DATETIME | Default: current time | When the alert was created |

#### Entity-Relationship Diagram

The diagram below shows how the four tables will relate to each other. The arrows represent foreign key relationships (for example, each `access_log` entry will point to one user and one API):

```
  ┌───────────────┐          ┌─────────────────────┐          ┌───────────────┐
  │     USERS      │          │    ACCESS_LOGS       │          │     APIS       │
  ├───────────────┤          ├─────────────────────┤          ├───────────────┤
  │ PK  id         │───┐     │ PK  id               │     ┌───│ PK  id         │
  │     name       │   │     │ FK  user_id      ◄────│─────┘   │     name       │
  │     role       │   └────►│ FK  api_id       ◄────│─────┐   │     description│
  └───────────────┘          │     timestamp         │     │   │     allowed_   │
                              │     usage_count       │     │   │       usage    │
                              └─────────────────────┘     │   │     cost_per_  │
                                                           │   │       call     │
  ┌───────────────────────────────────────────────────┐   │   └───────────────┘
  │                    ALERTS                          │   │
  ├───────────────────────────────────────────────────┤   │
  │ PK  id                                             │   │
  │     type ("warning" / "critical")                  │   │
  │ FK  api_id  ◄──────────────────────────────────────│───┘
  │ FK  user_id                                        │
  │     status ("new" / "resolved")                    │
  │     message                                        │
  │     timestamp                                      │
  └───────────────────────────────────────────────────┘
```

#### Data Normalization

The database will be designed in **Third Normal Form (3NF)**, which is a standard way to organize database tables to avoid redundancy (Codd, 1970):

- **1NF (First Normal Form):** Every column will hold a single value — no lists or repeating groups.
- **2NF (Second Normal Form):** Every non-key column will depend on the full primary key. Since we plan to use single-column primary keys (just `id`), this will be automatically satisfied.
- **3NF (Third Normal Form):** No column will depend on another non-key column. For example, we will *not* store `total_cost` in the database — instead, it will be calculated on the fly as `usage_count × cost_per_call`. This prevents data from getting out of sync.

#### Data Dictionary

| Field | Table | Type | Description | Example |
|-------|-------|------|-------------|---------|
| id | All | INTEGER | Auto-generated unique identifier | 1, 2, 3... |
| name | apis | TEXT | Display name of the API | "Payment Gateway API" |
| description | apis | TEXT | Brief purpose description | "Handles payment processing" |
| allowed_usage | apis | INTEGER | Max permitted calls | 500 |
| cost_per_call | apis | REAL | Dollar cost per call | 0.05 |
| name | users | TEXT | Person's full name | "Alice Mwangi" |
| role | users | TEXT | Job role | "Developer" |
| user_id | access_logs | INTEGER | Reference to who made the call | 3 |
| api_id | access_logs | INTEGER | Reference to which API was called | 1 |
| timestamp | access_logs | DATETIME | When the call happened | "2026-02-24 08:42:18" |
| usage_count | access_logs | INTEGER | Number of calls in this entry | 50 |
| type | alerts | TEXT | Severity level | "warning" or "critical" |
| status | alerts | TEXT | Whether it has been handled | "new" or "resolved" |
| message | alerts | TEXT | Human-readable alert text | "Payment API is approaching its limit" |

---

## 3.0 Architectural and Component-Level Design

This section explains how the system will be structured — the overall architecture we plan to use and the individual pieces (components) that will make it work.

### 3.1 System Structure

The system will follow the **Model-View-Controller (MVC)** design pattern, which is one of the most widely used architectural patterns in web development. As Grove and Ozkan (2013) explain, MVC separates an application into three layers so that each part can be developed and understood independently:

- **Model** — The data layer. In our system, this will be the SQLite database and the Python functions that read/write to it (`get_db()`, `init_db()`, `seed_sample_data()`, etc.).
- **View** — The presentation layer. This will be the `dashboard.html` template and `style.css` that the user will see in their browser.
- **Controller** — The logic layer. These will be the Flask route functions (`dashboard()`, `add_api()`, `simulate_usage()`, etc.) that will receive requests, process data, and decide what to display.

#### 3.1.1 Architecture Diagram

The following diagram shows how the three layers will interact. When a user opens the dashboard in their browser, the request will flow from top to bottom:

```
┌═══════════════════════════════════════════════════════════════┐
│                    🖥️  CLIENT (Web Browser)                   │
│                                                               │
│   dashboard.html          style.css          Chart.js         │
│   (HTML structure)    (Visual styling)    (Graphs/Charts)     │
│                                                               │
│   The user will see and interact with this layer.             │
│   Forms will send data to the server; charts will load via    │
│   AJAX (asynchronous JavaScript requests).                    │
└═══════════════════════╤═══════════════════════════════════════┘
                        │
                        │  HTTP Requests (GET / POST)
                        ▼
┌═══════════════════════════════════════════════════════════════┐
│                   🐍  SERVER (Flask — app.py)                 │
│                                                               │
│   ┌─── CONTROLLER (Route Handlers) ────────────────────────┐ │
│   │                                                         │ │
│   │  GET  /               →  dashboard()     (main page)    │ │
│   │  POST /add_api        →  add_api()       (new API)      │ │
│   │  POST /add_user       →  add_user()      (new user)     │ │
│   │  POST /simulate_usage →  simulate_usage()(log calls)    │ │
│   │  GET  /resolve_alert  →  resolve_alert() (dismiss)      │ │
│   │  GET  /api/chart_data →  chart_data()    (JSON for JS)  │ │
│   │                                                         │ │
│   └─────────────────────────┬───────────────────────────────┘ │
│                             │                                  │
│   ┌─── MODEL (Business Logic) ─────────────────────────────┐ │
│   │                                                         │ │
│   │  get_db()                  → Open database connection   │ │
│   │  init_db()                 → Create the 4 tables        │ │
│   │  seed_sample_data()        → Fill in demo data          │ │
│   │  check_and_generate_alerts() → Alert engine             │ │
│   │  get_api_usage(api_id)     → Sum up usage for an API    │ │
│   │                                                         │ │
│   └─────────────────────────┬───────────────────────────────┘ │
│                             │                                  │
│   ┌─── DATABASE ────────────▼───────────────────────────────┐ │
│   │                                                         │ │
│   │   SQLite File: db/governance.db                         │ │
│   │   Tables: apis │ users │ access_logs │ alerts           │ │
│   │                                                         │ │
│   └─────────────────────────────────────────────────────────┘ │
└═══════════════════════════════════════════════════════════════┘
```

### 3.2 Component Descriptions

Below is a detailed description of each component we plan to build. Each description covers what the component will do, what will go in and out of it, and how it will work internally.

---

#### 3.2.1 Component 1: Database Module

**Processing Narrative (PSPEC):**
The Database Module will be responsible for everything related to storing and retrieving data. It will create the database file and tables when the application starts, provide connection objects to other components, and seed the database with sample data for demonstration purposes.

**Interface Description:**

| Function | What Will Go In | What Will Come Out |
|----------|----------------|-------------------|
| `get_db()` | Nothing | A database connection object (with column-name access enabled) |
| `init_db()` | Nothing | Will create the `db/` folder and 4 tables if they do not already exist |
| `seed_sample_data()` | Nothing | Will insert 8 APIs, 5 users, and approximately 140 fake usage records across 14 days |
| `get_api_usage(api_id)` | An API's ID number | The total number of calls that API has received (an integer) |

**Processing Detail (Pseudocode):**

```
FUNCTION init_db():
    IF the "db" folder does not exist:
        Create it
    Open a connection to db/governance.db
    CREATE TABLE apis       (if it doesn't already exist)
    CREATE TABLE users      (if it doesn't already exist)
    CREATE TABLE access_logs (if it doesn't already exist)
    CREATE TABLE alerts     (if it doesn't already exist)
    Save changes and close the connection
    Print "Database initialized successfully."

FUNCTION seed_sample_data():
    Open a connection to the database
    IF the apis table already has data:
        Close the connection and stop (to avoid duplicating data)
    INSERT 8 sample APIs (Payment, Notification, Auth, etc.)
    INSERT 5 sample users (Alice, Brian, Catherine, etc.)
    FOR each of the last 14 days:
        INSERT between 5 and 20 random usage log entries
    Save changes and close the connection
    Run check_and_generate_alerts() to create initial alerts
    Print "Sample data seeded successfully."
```

**Restrictions/Limitations:** SQLite does not support multiple programs writing to the database at the same time. This is acceptable for our single-user demo but would need to be addressed in a production environment.

**Performance Issues:** With thousands of log entries, the `SUM()` queries that calculate total usage could become slow. Adding a database index on the `api_id` column of `access_logs` would help speed things up if needed.

---

#### 3.2.2 Component 2: Alert Engine

**Processing Narrative (PSPEC):**
The Alert Engine will serve as the "brain" of the governance system. It will compare each API's actual usage against its allowed limit and decide whether to generate a warning or critical alert. It is designed to run every time someone simulates API usage and during the initial data seeding.

**Interface Description:**

| Function | What Will Go In | What Will Come Out |
|----------|----------------|-------------------|
| `check_and_generate_alerts()` | Nothing (will read directly from the database) | Will create or update alert records in the `alerts` table |

**Processing Detail (Pseudocode):**

```
FUNCTION check_and_generate_alerts():
    Open a connection to the database
    Get the list of ALL APIs
    
    FOR each API:
        Calculate total_usage = SUM of all usage_count from access_logs for this API
        Calculate ratio = total_usage ÷ allowed_usage
        
        Delete any existing warning/critical alerts for this API
            (so we don't get duplicate alerts)
        
        IF ratio >= 1.0 (100% or more):
            Create a CRITICAL alert:
                type = "critical"
                message = "{API name} has exceeded its usage limit! ({usage}/{limit})"
        
        ELSE IF ratio >= 0.75 (75% to 99%):
            Create a WARNING alert:
                type = "warning"
                message = "{API name} is approaching its usage limit ({usage}/{limit})"
        
        (If ratio < 0.75, no alert will be created — the API is considered safe)
    
    Save changes and close the connection
```

**Alert Threshold Rules:**

| Usage Level | Status | Color on Dashboard | What the User Will See |
|------------|--------|-------------------|----------------------|
| 0% – 74% | Safe | 🟢 Green | ✅ Safe (42.2%) |
| 75% – 99% | Warning | 🟡 Yellow | ⚠️ Warning (85.8%) |
| 100%+ | Critical | 🔴 Red | 🔴 Over Limit (117.4%) |

**Design Constraints:** Alerts will be recalculated from scratch each time (old ones deleted and new ones created). This will keep the logic simple but means we will not keep a history of past alerts.

---

#### 3.2.3 Component 3: Route Handlers (Controller)

**Processing Narrative (PSPEC):**
The Route Handlers will be Flask functions that respond to requests from the user's browser. Each route will correspond to a URL. When the user clicks a button or submits a form, the browser will send a request to one of these routes, and the route function will process it.

**Interface Description:**

| URL Route | HTTP Method | Function Name | What It Will Do |
|-----------|------------|--------------|-----------------|
| `/` | GET | `dashboard()` | Load all data and render the main dashboard page |
| `/add_api` | POST | `add_api()` | Add a new API from the form, then redirect back to dashboard |
| `/add_user` | POST | `add_user()` | Add a new user from the form, then redirect back to dashboard |
| `/simulate_usage` | POST | `simulate_usage()` | Log API calls and check for alerts, then redirect back |
| `/resolve_alert/<id>` | GET | `resolve_alert()` | Mark a specific alert as "resolved", then redirect back |
| `/api/chart_data` | GET | `chart_data()` | Return JSON data that Chart.js will use to draw the graphs |

**Processing Detail for `dashboard()` — the main route:**

This will be the most complex function because it will need to gather data from multiple tables and calculate several derived values:

```
FUNCTION dashboard():
    Open a connection to the database
    
    1. FETCH all APIs from the apis table
    2. FOR each API:
        a. Calculate total_usage by summing all access_logs for that API
        b. Calculate usage_percent = (total_usage ÷ allowed_usage) × 100
        c. Determine status:
            - If usage >= 100%: status = "critical"
            - If usage >= 75%:  status = "warning"
            - Otherwise:        status = "safe"
        d. Calculate total_cost = total_usage × cost_per_call
        e. Add all this to the api_data list
    
    3. FETCH all users from the users table
    4. FETCH the latest 20 alerts (joined with API names)
    5. Calculate summary statistics:
        - total_apis  = count of APIs
        - total_users = count of users
        - total_calls = sum of ALL usage_count entries
        - active_alerts = count of alerts where status = "new"
    
    6. Close the database connection
    7. RENDER the dashboard.html template, passing in all the data
```

**Class Hierarchy:** This project will use a procedural (function-based) approach rather than object-oriented classes, which will keep the code simpler and more beginner-friendly. Each function will have a single clear responsibility.

---

### 3.3 Dynamic Behavior

This section shows how the components will interact with each other over time, using sequence diagrams. These diagrams should be read from top to bottom and show the expected order of events.

#### 3.3.1 Sequence Diagram: Simulating API Usage

This diagram shows what will happen when a user clicks the "Simulate Calls" button:

```
  👤 User         🌐 Browser        🐍 Flask Server     🗄️ SQLite DB
    │                │                    │                   │
    │ Fills form &   │                    │                   │
    │ clicks button  │                    │                   │
    │───────────────>│                    │                   │
    │                │  POST /simulate_   │                   │
    │                │  usage (form data) │                   │
    │                │───────────────────>│                   │
    │                │                    │                   │
    │                │                    │  INSERT INTO      │
    │                │                    │  access_logs      │
    │                │                    │──────────────────>│
    │                │                    │           OK ◄────│
    │                │                    │                   │
    │                │                    │  check_and_       │
    │                │                    │  generate_alerts()│
    │                │                    │──────────────────>│
    │                │                    │  (reads apis,     │
    │                │                    │   recalculates,   │
    │                │                    │   inserts alerts) │
    │                │                    │           OK ◄────│
    │                │                    │                   │
    │                │  302 Redirect → /  │                   │
    │                │<───────────────────│                   │
    │                │                    │                   │
    │                │  GET / (reload)    │                   │
    │                │───────────────────>│                   │
    │                │                    │  SELECT all data  │
    │                │                    │──────────────────>│
    │                │                    │        results ◄──│
    │                │   Updated HTML     │                   │
    │                │<───────────────────│                   │
    │                │                    │                   │
    │ Sees updated   │                    │                   │
    │ dashboard with │                    │                   │
    │ new usage &    │                    │                   │
    │ possible alert │                    │                   │
    │<───────────────│                    │                   │
```

#### 3.3.2 Sequence Diagram: Loading the Dashboard

This diagram shows what will happen when a user first opens the website:

```
  👤 User         🌐 Browser        🐍 Flask Server     🗄️ SQLite DB
    │                │                    │                   │
    │ Opens browser  │                    │                   │
    │ to localhost   │                    │                   │
    │───────────────>│                    │                   │
    │                │  GET /             │                   │
    │                │───────────────────>│                   │
    │                │                    │  Query: apis,     │
    │                │                    │  users, logs,     │
    │                │                    │  alerts, stats    │
    │                │                    │──────────────────>│
    │                │                    │      all data ◄───│
    │                │                    │                   │
    │                │  HTML page         │                   │
    │                │<───────────────────│                   │
    │                │                    │                   │
    │                │ (JavaScript runs)  │                   │
    │                │  GET /api/chart_   │                   │
    │                │  data (AJAX)       │                   │
    │                │───────────────────>│                   │
    │                │                    │  Query: 7-day     │
    │                │                    │  usage + per-API  │
    │                │                    │──────────────────>│
    │                │                    │     chart data ◄──│
    │                │   JSON response    │                   │
    │                │<───────────────────│                   │
    │                │                    │                   │
    │                │ Chart.js draws     │                   │
    │                │ the graphs         │                   │
    │                │                    │                   │
    │ Sees complete  │                    │                   │
    │ dashboard      │                    │                   │
    │<───────────────│                    │                   │
```

### 3.4 Database Modelling

#### Data Normalization

As mentioned in Section 2.4, the database will be designed in Third Normal Form (3NF) (Codd, 1970). This means:
- No repeating groups (1NF)
- No partial dependencies (2NF)
- No transitive dependencies (3NF) — calculated fields like `total_cost` and `usage_percent` will be computed at runtime, not stored

#### Entity-Relationship Model

| Entity | Key Attributes | Relationships |
|--------|---------------|---------------|
| **API** | id, name, description, allowed_usage, cost_per_call | Will have many AccessLogs; will have many Alerts |
| **User** | id, name, role | Will have many AccessLogs; will have many Alerts |
| **AccessLog** | id, user_id, api_id, timestamp, usage_count | Will belong to one User; will belong to one API |
| **Alert** | id, type, api_id, user_id, status, message, timestamp | Will belong to one API; optionally will belong to one User |

#### Database Schema (SQL)

```sql
CREATE TABLE apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    allowed_usage INTEGER DEFAULT 1000,
    cost_per_call REAL DEFAULT 0.01
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    api_id INTEGER REFERENCES apis(id),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 1
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    api_id INTEGER REFERENCES apis(id),
    user_id INTEGER REFERENCES users(id),
    status TEXT DEFAULT 'new',
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4.0 User Interface Design

### 4.1 Description of the User Interface

The entire application will be presented as a **single-page dashboard** that the user will access at `http://127.0.0.1:5000`. Everything — statistics, tables, charts, alerts, and forms — will be visible on one scrollable page. This design follows Nielsen's usability heuristic of "visibility of system status" (Nielsen, 1994), ensuring that users can see all important information at once without navigating between pages.

The page will be divided into these sections from top to bottom:

1. **Header** — A purple gradient banner with the system name and tagline
2. **Statistics Cards** — Four summary cards showing total APIs, users, calls, and active alerts
3. **Charts** — A line chart (7-day usage trend) and a doughnut chart (per-API breakdown)
4. **API Registry Table** — A table listing every API with usage stats and color-coded status badges
5. **Alerts Panel** — Active and resolved alerts with "Resolve" buttons
6. **Action Forms** — Three forms: Register API, Add User, Simulate Usage
7. **Footer** — Copyright notice

#### 4.1.1 Screen Images

The dashboard will feature the following visual design elements:

- **Header:** A deep purple gradient background (`#1e1b4b` → `#4338ca`) with white text, creating a professional appearance
- **Stat Cards:** White cards with rounded corners (12px radius), emoji icons, large bold numbers, and uppercase labels
- **API Table:** Clean rows with alternating hover effects; status shown as colored badges (green, yellow, red)
- **Alert Cards:** Left-bordered cards — yellow border for warnings, red border for critical alerts
- **Forms:** Clean input fields with blue focus outlines, styled dropdown menus, and gradient buttons
- **Charts:** A line chart with purple fill and smooth curves; a doughnut chart with a vibrant 8-color palette

#### 4.1.2 Objects and Actions

Every interactive element planned for the screen:

| Screen Object | Type | What Will Happen When the User Interacts |
|--------------|------|----------------------------------------|
| Stat Cards (×4) | Display only | Will show totals — no interaction needed |
| Usage Trend Chart | Chart.js canvas | Will display a 7-day usage line chart (auto-loads via AJAX) |
| Usage by API Chart | Chart.js canvas | Will display a doughnut chart showing per-API breakdown |
| API Registry Table | HTML table | Will show all APIs — read-only display |
| Status Badges | Colored labels | Green (Safe), Yellow (Warning), or Red (Over Limit) |
| "Resolve" Button | Link button | Will send a request to `/resolve_alert/<id>`; will mark alert as resolved |
| Register API Form | HTML form | Will submit to `/add_api` — adds a new API to the registry |
| Add User Form | HTML form | Will submit to `/add_user` — adds a new user to the system |
| API dropdown | Select menu | Will let users pick which API to simulate calls for |
| User dropdown | Select menu | Will let users pick which user is making the calls |
| "Simulate Calls" Button | Submit button | Will submit to `/simulate_usage` — logs fake API calls |

### 4.2 Interface Design Rules

The user interface will follow **Shneiderman's Eight Golden Rules of Interface Design** (Shneiderman et al., 2016):

| Rule | How We Plan to Apply It |
|------|------------------------|
| **1. Consistency** | All cards, buttons, and forms will use the same border-radius (12px), font, and color scheme |
| **2. Shortcuts for frequent users** | Everything will be on one page — no navigation menus or multi-step workflows |
| **3. Informative feedback** | After any action (add API, simulate usage), the page will immediately refresh to show updated data |
| **4. Closure** | Submitting a form will produce a visible result — a new row in the table, an updated stat card, or a new alert |
| **5. Error prevention** | Required fields will use the HTML `required` attribute; number inputs will prevent negative values |
| **6. Easy reversal** | Alerts will be resolvable (changed from "new" to "resolved") with a single click |
| **7. Internal locus of control** | The user will choose which API, which user, and how many calls to simulate — they will always be in control |
| **8. Reduce memory load** | All critical information will be visible simultaneously — no need to remember data from other pages |

### 4.3 Components Available

These are the front-end building blocks we plan to use for the interface:

| Component | Technology | What It Will Do |
|-----------|-----------|----------------|
| `<form>` elements | HTML5 | Collect user input for APIs, users, and simulation |
| `<table>` | HTML5 | Display the API registry in rows and columns |
| `<select>` dropdowns | HTML5 | Let users choose roles, APIs, and users from a list |
| `<input>` fields | HTML5 | Accept text and number data |
| `<button>` | HTML5 | Submit forms |
| `<canvas>` | Chart.js library | Render the line chart and doughnut chart |
| CSS Grid | CSS3 | Create responsive multi-column layouts |
| CSS Flexbox | CSS3 | Align items within cards and alert rows |
| CSS Animations | CSS3 | Fade-in effect when the page loads |
| Jinja2 `{{ }}` tags | Flask templating | Insert dynamic data (like API names and counts) into the HTML |

---

## 5.0 Restrictions, Limitations, and Constraints

1. **No login system** — The initial version will not include authentication. Anyone who can reach the URL will be able to see and change data. Adding Flask-Login would address this in a future version.
2. **No server-side input validation** — While HTML `required` will prevent empty submissions, the server will not check for duplicate names or invalid data types.
3. **No pagination** — The API table and alerts list will show all records at once. With hundreds of entries, the page could become slow to load.
4. **Single timezone** — All timestamps will use the server's local time. Users in different timezones would see times that do not match their local clock.
5. **No data export** — There will be no "Download as CSV" or "Generate PDF Report" feature in this version.
6. **Internet required for charts** — Chart.js will be loaded from a CDN (content delivery network). Without internet access, the charts will not render.
7. **Browser compatibility** — The CSS will use modern features like Grid and animations. Very old browsers (such as Internet Explorer) may not display the page correctly.
8. **No delete functionality** — Once an API or user is added, there will be no way to remove them from the dashboard. This would be a future improvement.

---

## 6.0 Testing Issues

### 6.1 Classes of Tests

Testing will ensure that every part of the system works correctly. We plan to use two main approaches:

**Black-Box Testing** — We will test from the user's perspective without looking at the code. We simply check: "If I do X, does Y happen?"

| Test Case | What We Will Do | What Should Happen |
|-----------|----------------|-------------------|
| Load Dashboard | Open `http://127.0.0.1:5000` | Page should display with stats, table, charts, and alerts |
| Add an API | Fill in "Register API" form and submit | New API should appear in the table with "Safe (0.0%)" status |
| Add a User | Fill in "Add User" form and submit | New user should appear in the simulation dropdown |
| Simulate Usage | Select an API and user, enter 100 calls, click "Simulate" | Usage count should increase in the table |
| Trigger Warning | Simulate calls until an API reaches 75% of its limit | A yellow ⚠️ Warning alert should appear |
| Trigger Critical | Simulate calls until an API exceeds 100% of its limit | A red 🔴 Critical alert should appear |
| Resolve Alert | Click the "Resolve" button on an alert | Alert should change from "Resolve" button to "Resolved" badge |
| Chart Data API | Visit `/api/chart_data` directly | Browser should show JSON with `labels`, `values`, and `api_usage` |

**White-Box Testing** — We will look inside the code and test individual functions:

| Test Case | What We Will Check | How We Will Verify |
|-----------|-------------------|-------------------|
| `init_db()` creates tables | Tables exist after function runs | Query `sqlite_master` for table names |
| `seed_sample_data()` inserts correct counts | 8 APIs, 5 users are inserted | COUNT queries on each table |
| `seed_sample_data()` skips if data exists | Running twice should not duplicate data | COUNT should remain the same |
| `check_and_generate_alerts()` at 80% | Alert type should be "warning" | Query alerts table for the API |
| `check_and_generate_alerts()` at 110% | Alert type should be "critical" | Query alerts table for the API |
| `get_api_usage()` returns correct sum | Total should match manual calculation | Compare with hand-calculated value |
| `chart_data()` returns 7 labels | JSON response should have exactly 7 items | Check length of `labels` array |

### 6.2 Expected Software Response

| User Action | Expected System Response |
|------------|------------------------|
| Run `python app.py` for the first time | Console should print "Database initialized successfully." and "Sample data seeded successfully." |
| Open `http://127.0.0.1:5000` | Dashboard should load within 2-3 seconds with all sections visible |
| Submit the "Register API" form with name "Test API" | Page should refresh; "Test API" should appear as the last row with 0 usage and "Safe" status |
| Click "Simulate Calls" with 200 calls on an API that has a limit of 500 | Usage should increase; if total exceeds 375 (75%), a warning alert should appear |
| Click "Resolve" on an active alert | The "Resolve" button should be replaced with a green "Resolved" badge |
| Visit `/api/chart_data` | JSON response should contain 7 date labels and 7 corresponding usage values |

### 6.3 Performance Bounds

| What We Will Measure | Target Performance |
|---------------------|-------------------|
| Dashboard page load time | Under 3 seconds |
| `/api/chart_data` response time | Under 1 second |
| Database initialization | Under 2 seconds |
| Sample data seeding (8 APIs + 5 users + 14 days of logs) | Under 5 seconds |

### 6.4 Identification of Critical Components

These are the parts of the system that will be most important to test thoroughly because errors in them would break core functionality:

1. **`check_and_generate_alerts()`** — This will be the heart of the governance system. If the threshold logic is wrong (e.g., triggering at 50% instead of 75%), the entire purpose of the system would be undermined. Edge cases to test: exactly 75%, exactly 100%, and APIs with `allowed_usage = 0`.

2. **`dashboard()` route** — This will be the most complex function, running 6+ database queries and building calculated fields. A bug here (like dividing by zero when `allowed_usage` is 0) would crash the entire page.

3. **Database foreign keys** — If a user or API is referenced by `access_logs` or `alerts` and then somehow removed, it could cause data integrity issues. We plan to avoid this by not implementing delete functionality in the initial version.

4. **`/api/chart_data` endpoint** — The charts will depend on this endpoint returning correctly structured JSON. If the format is wrong (e.g., mismatched array lengths), Chart.js would silently fail and show an empty graph.

---

## References

Codd, E. F. (1970). A relational model of data for large shared data banks. *Communications of the ACM*, 13(6), 377–387. https://doi.org/10.1145/362384.362685

Grove, R. F., & Ozkan, E. (2013). The MVC-Web design pattern. *Proceedings of the International Conference on Software Engineering Research and Practice (SERP)*. https://doi.org/10.5555/2555523.2555536

Mathijssen, M., & Overeem, M. (2023). A framework for guidance of API governance: A design science approach. *Master's thesis, University of Gothenburg*. Retrieved from https://gupea.ub.gu.se

Medjaoui, M., Wilde, E., Mitra, R., & Amundsen, M. (2019). *Continuous API management: Making the right decisions in an evolving landscape*. O'Reilly Media.

Nielsen, J. (1994). *Usability engineering*. Morgan Kaufmann Publishers.

Owens, M. (2006). *The definitive guide to SQLite*. Apress. https://doi.org/10.1007/978-1-4302-0172-4

Pallets Projects. (2024). Flask documentation. Retrieved from https://flask.palletsprojects.com/

Shneiderman, B., Plaisant, C., Cohen, M., Jacobs, S., Elmqvist, N., & Diakopoulos, N. (2016). *Designing the user interface: Strategies for effective human-computer interaction* (6th ed.). Pearson.

SQLite Consortium. (2024). SQLite documentation. Retrieved from https://www.sqlite.org/docs.html
