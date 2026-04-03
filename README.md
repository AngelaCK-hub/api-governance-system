# 🛡️ API Governance System

A web-based API Governance Dashboard built with **Python Flask**, **SQLite**, and **Chart.js** to monitor, manage, and govern APIs.

## Features

- **API Registry** — Register and track APIs with usage limits and cost per call
- **User Management** — Add users with roles (Developer, Manager, Admin)
- **Usage Monitoring** — Track API usage with color-coded status indicators
  - ✅ **Safe** (under 75% of limit)
  - ⚠️ **Warning** (75%–99% of limit)
  - 🔴 **Critical** (over limit)
- **Automated Alerts** — Alerts generated when APIs approach or exceed usage limits
- **Charts & Analytics** — Usage trends (7-day line chart) and per-API breakdown (doughnut chart)
- **Usage Simulation** — Simulate API calls for testing and demonstration

## Tech Stack

| Layer | Tool |
|-------|------|
| Backend | Python + Flask |
| Database | SQLite |
| Frontend | HTML + CSS + JavaScript |
| Charts | Chart.js |

## Project Structure

```
API System/
├── app.py                  # Main backend logic
├── db/
│   └── governance.db       # SQLite database (auto-created)
├── templates/
│   └── dashboard.html      # Dashboard UI
├── static/
│   └── style.css           # Styling
├── .gitignore
└── README.md
```

## How to Run

1. **Install Flask**
   ```bash
   pip install flask
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

The database and sample data (8 APIs, 5 users, 2 weeks of activity) are created automatically on first run.

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

## License

This project is for educational purposes.
