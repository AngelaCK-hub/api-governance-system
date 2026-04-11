import sqlite3
import os
import random
import hashlib
import csv
import io
from datetime import datetime, timedelta
from functools import wraps
# type: ignore
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response

app = Flask(__name__)
app.secret_key = "api_gov_secret"
DB_PATH = os.path.join("db", "governance.db")

# Hashed Admin PIN (SHA-256 of "1234")
ADMIN_PIN_HASH = hashlib.sha256("1234".encode()).hexdigest()


# ─── DATABASE HELPERS ─────────────────────────────────────────────
def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row  # So we can access columns by name
    return conn


def init_db():
    """Initialize the database with required tables."""
    if not os.path.exists("db"):
        os.makedirs("db")

    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS apis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        allowed_usage INTEGER DEFAULT 10,
        cost_per_call REAL DEFAULT 0.05,
        status TEXT DEFAULT 'Online',
        latency_ms INTEGER DEFAULT 45,
        uptime_pct REAL DEFAULT 99.9
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        api_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        usage_count INTEGER DEFAULT 1,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(api_id) REFERENCES apis(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        api_id INTEGER,
        user_id INTEGER,
        status TEXT DEFAULT 'new',
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(api_id) REFERENCES apis(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        entity_type TEXT,
        entity_id INTEGER,
        user_id INTEGER,
        user_name TEXT,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def log_action(action, entity_type=None, entity_id=None, details=None):
    """Record an action in the audit trail."""
    user_id = session.get("user_id")
    user_name = session.get("user_name", "System")
    conn = get_db()
    conn.execute(
        "INSERT INTO audit_log (action, entity_type, entity_id, user_id, user_name, details) VALUES (?,?,?,?,?,?)",
        (action, entity_type, entity_id, user_id, user_name, details)
    )
    conn.commit()
    conn.close()


def seed_sample_data():
    """Insert sample APIs, users, and fake usage data."""
    conn = get_db()
    c = conn.cursor()

    # Check if data already exists
    if c.execute("SELECT COUNT(*) FROM apis").fetchone()[0] > 0:
        conn.close()
        return

    # Sample APIs
    apis = [
        ("Payments-v1", "Core payment processing API", 15, 0.15, 'Online', 45, 99.9),
        ("User-Service", "Detailed user profile management", 10, 0.05, 'Online', 32, 100.0),
        ("Auth-Gateway", "OIDC/OAuth2 authentication layer", 8, 0.20, 'Online', 15, 99.99),
        ("Inventory-API", "Real-time stock tracking", 12, 0.08, 'Online', 64, 98.7),
        ("Notification-Svc", "Transactional email and SMS", 10, 0.02, 'Online', 120, 99.5),
        ("Analytics-Engine", "Data aggregation and reporting", 5, 0.50, 'Online', 250, 99.2),
    ]
    c.executemany("INSERT INTO apis (name, description, allowed_usage, cost_per_call, status, latency_ms, uptime_pct) VALUES (?,?,?,?,?,?,?)", apis)

    # Sample Users
    users = [
        ("Angela Kasoha", "Admin"),
        ("Alice Mwangi", "Developer"),
        ("Brian Ochieng", "Developer"),
        ("Catherine Wanjiku", "Manager"),
        ("David Kamau", "Developer"),
        ("Eve Akinyi", "Manager"),
    ]
    c.executemany("INSERT INTO users (name, role) VALUES (?,?)", users)

    # Simulate 2 weeks of fake usage data
    now = datetime.now()
    for day_offset in range(14):
        log_date = now - timedelta(days=day_offset)
        for _ in range(random.randint(1, 3)):
            user_id = random.randint(1, len(users))
            api_id = random.randint(1, len(apis))
            count = random.randint(1, 3)
            timestamp = log_date.strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO access_logs (user_id, api_id, timestamp, usage_count) VALUES (?,?,?,?)",
                      (user_id, api_id, timestamp, count))

    conn.commit()
    conn.close()

    # Generate alerts based on seeded data
    check_and_generate_alerts()
    print("Sample data seeded successfully.")


def get_api_usage(api_id):
    """Get total usage for an API."""
    conn = get_db()
    result = conn.execute(
        "SELECT COALESCE(SUM(usage_count), 0) as total FROM access_logs WHERE api_id = ?",
        (api_id,)
    ).fetchone()
    conn.close()
    return result["total"]


def check_and_generate_alerts():
    """Check all APIs and generate alerts if usage exceeds limits."""
    conn = get_db()
    apis = conn.execute("SELECT * FROM apis").fetchall()

    for api in apis:
        total = conn.execute(
            "SELECT COALESCE(SUM(usage_count), 0) as total FROM access_logs WHERE api_id = ?",
            (api["id"],)
        ).fetchone()["total"]

        ratio = total / api["allowed_usage"] if api["allowed_usage"] > 0 else 0

        # Clear old alerts for this API
        conn.execute("DELETE FROM alerts WHERE api_id = ? AND type IN ('warning','critical')", (api["id"],))

        if ratio >= 1.0:
            conn.execute(
                "INSERT INTO alerts (type, api_id, status, message) VALUES (?,?,?,?)",
                ("critical", api["id"], "new",
                 f"{api['name']} has exceeded its usage limit! ({total}/{api['allowed_usage']})")
            )
        elif ratio >= 0.75:
            conn.execute(
                "INSERT INTO alerts (type, api_id, status, message) VALUES (?,?,?,?)",
                ("warning", api["id"], "new",
                 f"{api['name']} is approaching its usage limit ({total}/{api['allowed_usage']})")
            )

    conn.commit()
    conn.close()


# ─── MIDDLEWARE ────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ─── ROUTES ────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    """Simple selector login with Admin security."""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        pin = request.form.get("pin")

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()

        if user:
            # Security check for Admin using hashed PIN
            if user["role"] == "Admin":
                if hashlib.sha256((pin or "").encode()).hexdigest() != ADMIN_PIN_HASH:
                    conn = get_db()
                    users = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
                    conn.close()
                    return render_template("login.html", users=users, error="Invalid Administrator PIN")

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]
            log_action("LOGIN", "user", user["id"], f"{user['name']} logged in as {user['role']}")
            return redirect(url_for("dashboard"))

    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    conn.close()
    return render_template("login.html", users=users)


@app.route("/logout")
def logout():
    """Log out user."""
    user_name = session.get("user_name", "Unknown")
    log_action("LOGOUT", "user", session.get("user_id"), f"{user_name} logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    """Main dashboard page."""
    conn = get_db()

    # "Jitter" API stats to make it look alive
    apis_raw = conn.execute("SELECT * FROM apis").fetchall()
    for api in apis_raw:
        if api['status'] != 'Offline':
            new_latency = max(5, api['latency_ms'] + random.randint(-5, 5))
            new_uptime = min(100.0, max(95.0, api['uptime_pct'] + random.uniform(-0.01, 0.01)))
            conn.execute("UPDATE apis SET latency_ms = ?, uptime_pct = ? WHERE id = ?",
                         (new_latency, round(float(new_uptime), 2), api['id']))
    conn.commit()

    # Get all APIs with their usage stats
    apis = conn.execute("SELECT * FROM apis").fetchall()
    api_data = []
    for api in apis:
        total_usage = conn.execute(
            "SELECT COALESCE(SUM(usage_count), 0) as total FROM access_logs WHERE api_id = ?",
            (api["id"],)
        ).fetchone()["total"]
        ratio = total_usage / api["allowed_usage"] if api["allowed_usage"] > 0 else 0

        if ratio >= 1.0:
            status = "critical"
        elif ratio >= 0.75:
            status = "warning"
        else:
            status = "safe"

        api_data.append({
            "id": api["id"],
            "name": api["name"],
            "description": api["description"],
            "total_usage": total_usage,
            "allowed_usage": api["allowed_usage"],
            "cost_per_call": api["cost_per_call"],
            "total_cost": round(total_usage * api["cost_per_call"], 2),
            "usage_percent": round(ratio * 100, 1),
            "status": api["status"],
            "usage_status": status,
            "latency_ms": api["latency_ms"],
            "uptime_pct": api["uptime_pct"]
        })

    # Get users
    users = conn.execute("SELECT * FROM users").fetchall()

    # Get alerts
    alerts = conn.execute(
        "SELECT alerts.*, apis.name as api_name FROM alerts LEFT JOIN apis ON alerts.api_id = apis.id ORDER BY alerts.timestamp DESC LIMIT 20"
    ).fetchall()

    # Get stats
    total_apis = len(apis)
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_calls = conn.execute("SELECT COALESCE(SUM(usage_count), 0) FROM access_logs").fetchone()[0]
    active_alerts = conn.execute("SELECT COUNT(*) FROM alerts WHERE status = 'new'").fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           apis=api_data,
                           users=users,
                           alerts=alerts,
                           total_apis=total_apis,
                           total_users=total_users,
                           total_calls=total_calls,
                           active_alerts=active_alerts,
                           current_user=session)


@app.route("/add_api", methods=["POST"])
@login_required
def add_api():
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))
    """Add a new API."""
    name = request.form.get("name")
    description = request.form.get("description", "")
    allowed_usage = int(request.form.get("allowed_usage", 1000))
    cost_per_call = float(request.form.get("cost_per_call", 0.01))

    conn = get_db()
    conn.execute("INSERT INTO apis (name, description, allowed_usage, cost_per_call) VALUES (?,?,?,?)",
                 (name, description, allowed_usage, cost_per_call))
    conn.commit()
    conn.close()
    log_action("CREATE_API", "api", None, f"Registered new API: {name}")
    return redirect(url_for("dashboard"))


@app.route("/edit_api/<int:api_id>", methods=["POST"])
@login_required
def edit_api(api_id):
    """Edit an existing API."""
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))

    name = request.form.get("name")
    description = request.form.get("description", "")
    allowed_usage = int(request.form.get("allowed_usage", 10))
    cost_per_call = float(request.form.get("cost_per_call", 0.01))

    conn = get_db()
    conn.execute(
        "UPDATE apis SET name = ?, description = ?, allowed_usage = ?, cost_per_call = ? WHERE id = ?",
        (name, description, allowed_usage, cost_per_call, api_id)
    )
    conn.commit()
    conn.close()
    log_action("UPDATE_API", "api", api_id, f"Updated API: {name}")
    check_and_generate_alerts()
    return redirect(url_for("dashboard"))


@app.route("/delete_api/<int:api_id>", methods=["POST"])
@login_required
def delete_api(api_id):
    """Delete an API and its associated data."""
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))

    conn = get_db()
    api = conn.execute("SELECT name FROM apis WHERE id = ?", (api_id,)).fetchone()
    api_name = api["name"] if api else "Unknown"
    conn.execute("DELETE FROM access_logs WHERE api_id = ?", (api_id,))
    conn.execute("DELETE FROM alerts WHERE api_id = ?", (api_id,))
    conn.execute("DELETE FROM apis WHERE id = ?", (api_id,))
    conn.commit()
    conn.close()
    log_action("DELETE_API", "api", api_id, f"Deleted API: {api_name}")
    return redirect(url_for("dashboard"))


@app.route("/edit_user/<int:user_id>", methods=["POST"])
@login_required
def edit_user(user_id):
    """Edit an existing user."""
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))

    name = request.form.get("name")
    role = request.form.get("role", "Developer")

    conn = get_db()
    conn.execute("UPDATE users SET name = ?, role = ? WHERE id = ?", (name, role, user_id))
    conn.commit()
    conn.close()
    log_action("UPDATE_USER", "user", user_id, f"Updated user: {name} ({role})")
    return redirect(url_for("dashboard"))


@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    """Delete a user and their associated data."""
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))

    # Prevent deleting yourself
    if user_id == session.get("user_id"):
        return redirect(url_for("dashboard"))

    conn = get_db()
    user = conn.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
    user_name = user["name"] if user else "Unknown"
    conn.execute("DELETE FROM access_logs WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM alerts WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    log_action("DELETE_USER", "user", user_id, f"Deleted user: {user_name}")
    return redirect(url_for("dashboard"))


@app.route("/add_user", methods=["POST"])
@login_required
def add_user():
    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))
    """Add a new user."""
    name = request.form.get("name")
    role = request.form.get("role", "Developer")

    conn = get_db()
    conn.execute("INSERT INTO users (name, role) VALUES (?,?)", (name, role))
    conn.commit()
    conn.close()
    log_action("CREATE_USER", "user", None, f"Added new user: {name} ({role})")
    return redirect(url_for("dashboard"))


@app.route("/simulate_usage", methods=["POST"])
@login_required
def simulate_usage():
    """Simulate API usage."""
    api_id = int(request.form.get("api_id"))
    user_id = int(request.form.get("user_id"))
    count = int(request.form.get("count", 10))

    conn = get_db()
    api = conn.execute("SELECT name FROM apis WHERE id = ?", (api_id,)).fetchone()
    conn.execute("INSERT INTO access_logs (user_id, api_id, usage_count) VALUES (?,?,?)",
                 (user_id, api_id, count))
    conn.commit()
    conn.close()

    api_name = api["name"] if api else "Unknown"
    log_action("SIMULATE_USAGE", "api", api_id, f"Simulated {count} calls on {api_name}")
    check_and_generate_alerts()
    return redirect(url_for("dashboard"))


@app.route("/resolve_alert/<int:alert_id>")
@login_required
def resolve_alert(alert_id):
    if session.get("user_role") == "Developer":
        return redirect(url_for("dashboard"))
    """Mark an alert as resolved."""
    conn = get_db()
    alert = conn.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    conn.execute("UPDATE alerts SET status = 'resolved' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    msg = alert["message"] if alert else f"Alert #{alert_id}"
    log_action("RESOLVE_ALERT", "alert", alert_id, f"Resolved: {msg}")
    return redirect(url_for("dashboard"))


@app.route("/api/chart_data")
@login_required
def chart_data():
    """Return usage data for Chart.js (last 7 days)."""
    conn = get_db()
    labels = []
    values = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        labels.append((datetime.now() - timedelta(days=i)).strftime("%b %d"))
        total = conn.execute(
            "SELECT COALESCE(SUM(usage_count), 0) FROM access_logs WHERE DATE(timestamp) = ?",
            (day,)
        ).fetchone()[0]
        values.append(total)

    # Per-API breakdown
    apis = conn.execute("SELECT id, name FROM apis").fetchall()
    api_usage = []
    for api in apis:
        total = conn.execute(
            "SELECT COALESCE(SUM(usage_count), 0) FROM access_logs WHERE api_id = ?",
            (api["id"],)
        ).fetchone()[0]
        api_usage.append({"name": api["name"], "usage": total})

    conn.close()
    return jsonify({"labels": labels, "values": values, "api_usage": api_usage})


# ─── AUDIT LOG ENDPOINT ────────────────────────────────────────────
@app.route("/api/audit_log")
@login_required
def get_audit_log():
    """Return audit log data."""
    if session.get("user_role") not in ["Admin", "Manager"]:
        return jsonify([])

    conn = get_db()
    logs = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in logs])


# ─── EXPORT ROUTES ─────────────────────────────────────────────────
@app.route("/export/apis")
@login_required
def export_apis():
    """Export API registry as CSV."""
    if session.get("user_role") not in ["Admin", "Manager"]:
        return redirect(url_for("dashboard"))
    conn = get_db()
    apis = conn.execute("SELECT * FROM apis").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Description", "Usage Limit", "Cost per Call", "Status", "Latency (ms)", "Uptime (%)"])
    for api in apis:
        writer.writerow([api["id"], api["name"], api["description"], api["allowed_usage"],
                         api["cost_per_call"], api["status"], api["latency_ms"], api["uptime_pct"]])

    log_action("EXPORT", "api", None, "Exported API registry as CSV")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=api_registry.csv"}
    )


@app.route("/export/usage")
@login_required
def export_usage():
    """Export usage data as CSV."""
    if session.get("user_role") not in ["Admin", "Manager"]:
        return redirect(url_for("dashboard"))
    conn = get_db()
    logs = conn.execute(
        """SELECT access_logs.id, users.name as user_name, apis.name as api_name,
           access_logs.usage_count, access_logs.timestamp
           FROM access_logs
           LEFT JOIN users ON access_logs.user_id = users.id
           LEFT JOIN apis ON access_logs.api_id = apis.id
           ORDER BY access_logs.timestamp DESC"""
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User", "API", "Usage Count", "Timestamp"])
    for log in logs:
        writer.writerow([log["id"], log["user_name"], log["api_name"], log["usage_count"], log["timestamp"]])

    log_action("EXPORT", "usage", None, "Exported usage data as CSV")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=usage_data.csv"}
    )


@app.route("/export/alerts")
@login_required
def export_alerts():
    """Export alerts as CSV."""
    if session.get("user_role") not in ["Admin", "Manager"]:
        return redirect(url_for("dashboard"))
    conn = get_db()
    alerts = conn.execute(
        """SELECT alerts.id, alerts.type, apis.name as api_name, alerts.status,
           alerts.message, alerts.timestamp
           FROM alerts
           LEFT JOIN apis ON alerts.api_id = apis.id
           ORDER BY alerts.timestamp DESC"""
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Type", "API", "Status", "Message", "Timestamp"])
    for alert in alerts:
        writer.writerow([alert["id"], alert["type"], alert["api_name"], alert["status"],
                         alert["message"], alert["timestamp"]])

    log_action("EXPORT", "alert", None, "Exported alerts as CSV")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=alerts.csv"}
    )


@app.route("/export/audit")
@login_required
def export_audit():
    """Export audit trail as CSV."""
    if session.get("user_role") not in ["Admin", "Manager"]:
        return redirect(url_for("dashboard"))

    conn = get_db()
    logs = conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Action", "Entity Type", "Entity ID", "User", "Details", "Timestamp"])
    for log in logs:
        writer.writerow([log["id"], log["action"], log["entity_type"], log["entity_id"],
                         log["user_name"], log["details"], log["timestamp"]])

    log_action("EXPORT", "audit", None, "Exported audit trail as CSV")
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_trail.csv"}
    )


# ─── CHAOS SIMULATION ─────────────────────────────────────────────
@app.route("/simulate_chaos", methods=["POST"])
@login_required
def simulate_chaos():
    """Trigger a simulated crisis (Chaos Simulation)."""
    if session.get("user_role") != "Admin":
        return jsonify({"success": False, "message": "Access Denied"}), 403

    chaos_type = request.json.get("type", "spike")
    conn = get_db()

    if chaos_type == "outage":
        apis = conn.execute("SELECT id, name FROM apis").fetchall()
        target = random.choice(apis)
        conn.execute("UPDATE apis SET status = 'Offline', latency_ms = 0 WHERE id = ?", (target['id'],))
        msg = f"Simulated outage triggered on {target['name']}."
        conn.execute("INSERT INTO alerts (type, api_id, status, message) VALUES (?,?,?,?)",
                     ("critical", target['id'], "new", f"CHAOS OUTAGE: {target['name']} went offline!"))
        log_action("CHAOS_OUTAGE", "api", target['id'], msg)
    elif chaos_type == "spike":
        conn.execute("UPDATE apis SET status = 'Degraded', latency_ms = latency_ms * 5")
        users = conn.execute("SELECT id FROM users").fetchall()
        apis = conn.execute("SELECT id FROM apis").fetchall()
        for _ in range(10):
            u_id = random.choice(users)['id']
            a_id = random.choice(apis)['id']
            conn.execute("INSERT INTO access_logs (user_id, api_id, usage_count) VALUES (?,?,?)",
                         (u_id, a_id, random.randint(5, 15)))  # Increased payload
        msg = "Simulation: Worldwide traffic spike in progress. Latency high."
        log_action("CHAOS_SPIKE", "system", None, msg)
    else:
        conn.execute("UPDATE apis SET status = 'Online', latency_ms = ABS(RANDOM() % 100) + 10")
        msg = "Systems stabilized. Chaos simulated cleared."
        conn.execute("DELETE FROM alerts WHERE message LIKE 'CHAOS OUTAGE:%'")
        log_action("CHAOS_RESET", "system", None, msg)

    conn.commit()
    conn.close()

    # Trigger threshold alerts after spike
    if chaos_type == "spike":
        check_and_generate_alerts()

    return jsonify({"success": True, "message": msg})


if __name__ == "__main__":
    init_db()
    seed_sample_data()
    app.run(debug=True)
