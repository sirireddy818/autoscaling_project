# CloudScale — Dynamic Auto Scaling Simulation Platform

> A full-stack web application that **simulates AWS Auto Scaling** behavior with real-time monitoring, load testing, and cost analysis — running 100% locally with zero cloud costs.

**SDG 9 — Industry, Innovation and Infrastructure**
**Institution:** Sreyas Institute of Engineering and Technology | **Year:** 2025–26 | **Project Type:** IOMP

---

## Table of Contents

1. [What This Project Is](#1-what-this-project-is)
2. [Why We Built This](#2-why-we-built-this)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [System Architecture](#5-system-architecture)
6. [How Every File Works](#6-how-every-file-works)
7. [All Formulas Used](#7-all-formulas-used)
8. [Auto Scaling Logic — Step by Step](#8-auto-scaling-logic--step-by-step)
9. [Database Design](#9-database-design)
10. [Security Implementation](#10-security-implementation)
11. [All Pages Explained](#11-all-pages-explained)
12. [Data Flow — End to End](#12-data-flow--end-to-end)
13. [How to Run](#13-how-to-run)
14. [Demo Flow for Presentation](#14-demo-flow-for-presentation)
15. [Cost Analysis](#15-cost-analysis)
16. [SDG Contribution](#16-sdg-contribution)
17. [Future Scope](#17-future-scope)
18. [Team](#18-team)

---

## 1. What This Project Is

**CloudScale** is a simulation of how **AWS Auto Scaling Groups (ASG)** work. It is a web app where you:

- Log in with a secure account
- Simulate up to **1000 users** hitting a website
- Watch the system automatically **add or remove servers** based on CPU load
- See **live charts**, **cost savings**, and **scaling event logs** in real time

Everything runs on your laptop — no AWS account, no internet required, no cost.

---

## 2. Why We Built This

**The Problem:**
When a website gets sudden traffic, servers can crash if there aren't enough machines. But keeping 10 servers running 24/7 even during low traffic is extremely wasteful and expensive.

**The Real-World Solution:**
AWS Auto Scaling automatically adds servers when demand is high and removes them when demand is low. This saves money and prevents crashes.

**Our Problem:**
Learning AWS Auto Scaling on real AWS requires an account, billing setup, and cloud knowledge. It's risky and costly for students.

**Our Solution:**
We built a simulation that shows exactly how auto scaling behaves — visually, interactively, and for free. Anyone can learn cloud infrastructure concepts just by running this on their laptop.

---

## 3. Tech Stack

| Component | Technology | Why We Chose It |
|-----------|-----------|-----------------|
| Web Framework | **Streamlit** (Python) | Rapid UI development, built-in reactive components, no HTML/JS needed |
| Charts | **Plotly** | Interactive line charts, gauges, bar charts with dark/light theming |
| Database | **SQLite** | Lightweight, no server needed, single `.db` file, perfect for local apps |
| Language | **Python 3.12** | All-in-one: backend logic, UI, database, charts in one language |
| Password Security | **PBKDF2-SHA256** | Industry-standard hashing used by Django, AWS Cognito |
| Styling | **HTML/CSS (inline)** | Custom glassmorphism UI, animations, gradients via `st.markdown` |

---

## 4. Project Structure

```
autoscaling_project/
│
├── Home.py                        → Main dashboard (entry point, auto-refreshes every 2s)
├── requirements.txt               → Python package list (streamlit, plotly)
├── README.md                      → This file
├── cloudscale.db                  → SQLite database file (created automatically on first run)
│
├── backend/                       → All core logic lives here
│   ├── __init__.py                → Makes backend/ a Python package
│   ├── auth.py                    → Login/Signup UI + session management
│   ├── db.py                      → SQLite database operations (user accounts)
│   ├── state.py                   → SystemState and InstanceInfo classes (simulation memory)
│   ├── autoscaler.py              → Auto scaling engine (the core algorithm)
│   └── metrics.py                 → CPU and memory calculation formulas
│
└── pages/                         → Streamlit multi-page app (each file = one page in sidebar)
    ├── 1_Overview.py              → Gauge charts: CPU%, Memory%, Instance count
    ├── 2_System_Architecture.py   → Visual flow diagram (Users → LB → ASG → EC2 → CW)
    ├── 3_Load_Generator.py        → Slider + buttons to set 0–1000 simulated users
    ├── 4_Live_Metrics.py          → 4-panel line charts + statistics table
    ├── 5_Auto_Scaling_Activity.py → Timeline of scale-out/scale-in events + system logs
    └── 6_Cost_Analysis.py         → Cost comparison charts, savings %, AWS pricing table
```

---

## 5. System Architecture

### Component Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   👥 USERS (0 – 1000)                                          │
│   Simulated via Load Generator slider                           │
│              │                                                  │
│              ▼                                                  │
│   ⚖️  APPLICATION LOAD BALANCER                                 │
│   Distributes requests evenly across all running instances      │
│              │                                                  │
│              ▼                                                  │
│   📦 AUTO SCALING GROUP (ASG)                                   │
│   ┌──────────────────────────────────────────────┐             │
│   │  Scale Out Policy: CPU > 70%  → add servers  │             │
│   │  Scale In Policy:  CPU < 30%  → remove servers│            │
│   │  Min Instances: 1   Max Instances: 10         │             │
│   │  Cooldown: 2 seconds between scaling actions  │             │
│   └──────────────────────────────────────────────┘             │
│              │                                                  │
│              ▼                                                  │
│   🖥️  EC2 INSTANCES (1 to 10 servers)                           │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│   │instance │ │instance │ │instance │ │instance │  ...        │
│   │ alpha   │ │  beta   │ │  gamma  │ │  delta  │            │
│   │ CPU: 50%│ │ CPU: 50%│ │ CPU: 50%│ │ CPU: 50%│            │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│              │                                                  │
│              ▼                                                  │
│   📊 CLOUDWATCH MONITORING                                      │
│   Checks CPU/Memory every 2 seconds                             │
│   Feeds metrics back to ASG for scaling decisions               │
│              │                                                  │
│              ▼                                                  │
│   🖥️  DASHBOARD (auto-refresh every 2s)                         │
│   Shows live charts, instance fleet, scaling events             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### How Components Interact in Code

```
Home.py (every 2 seconds)
    │
    ├── calls calculate_cpu()      ← metrics.py
    ├── calls calculate_memory()   ← metrics.py
    ├── calls apply_autoscaling()  ← autoscaler.py
    │       └── calls calculate_cpu/memory again after each scaling round
    ├── calls state.tick_fleet()   ← state.py (updates each instance)
    └── calls state.record_snapshot() ← state.py (saves to history arrays)
```

### Instance Lifecycle

```
NEW INSTANCE CREATED
       │
       ▼
  status: "launching"    ← Boot phase, takes 2 ticks (4 seconds)
  health: "initializing"
  CPU: 5–15% (OS startup)
       │
  (after 2 ticks)
       │
       ▼
  status: "running"      ← Fully operational, handling user requests
  health: "healthy" / "warning" / "critical"  ← based on CPU%
       │
  (when scaled in)
       │
       ▼
  REMOVED from instance_fleet list
```

---

## 6. How Every File Works

### `backend/metrics.py` — CPU & Memory Formulas

Calculates system-wide CPU and memory based on user count and instance count.
Called every 2 seconds from `Home.py` and `autoscaler.py`.

### `backend/autoscaler.py` — Scaling Engine

The brain of the project. Decides when to add/remove instances.
Runs a stabilization loop (up to 10 rounds per tick) until metrics are in the safe range.

### `backend/state.py` — System Memory

Two classes:
- `InstanceInfo` — represents one server (id, name, cpu, memory, requests, status, health)
- `SystemState` — holds everything: users, instances, cpu%, memory%, history arrays, logs

Stored in `st.session_state` so data persists as user navigates between pages.

### `backend/db.py` — User Database

SQLite operations: create table, signup new user, login existing user.
Passwords are never stored in plain text — only PBKDF2-SHA256 hashes.

### `backend/auth.py` — Authentication UI

Shows the login/signup page (dark premium UI with animated background).
`get_user()` — checks if someone is logged in.
`require_auth()` — blocks pages if not logged in.
`show_user_sidebar()` — shows user avatar + logout button in sidebar.

### `Home.py` — Main Dashboard

Entry point. Uses `@st.fragment(run_every=2)` to auto-refresh every 2 seconds.
Shows: live metric cards, instance fleet grid, CPU/memory charts, recent scaling events.

---

## 7. All Formulas Used

### CPU Usage Formula

```
CPU% = (active_users / (instances × 100)) × 100 + jitter

Where:
  active_users  = number of simulated users (0–1000)
  instances     = number of running servers (1–10)
  100           = each instance handles 100 users at full CPU
  jitter        = random.uniform(-2, 2)  → adds ±2% realistic noise

Example 1: 500 users, 5 instances
  CPU = (500 / (5 × 100)) × 100 = (500/500) × 100 = 100%
  → System is overloaded! Will trigger scale out.

Example 2: 500 users, 10 instances
  CPU = (500 / (10 × 100)) × 100 = (500/1000) × 100 = 50%
  → System is stable. No scaling needed.

Example 3: 100 users, 1 instance
  CPU = (100 / (1 × 100)) × 100 = 100%
  → Will trigger scale out.
```

### Memory Usage Formula

```
Memory% = 15 + (active_users / (instances × 120)) × 60 + jitter

Where:
  15            = base OS overhead (always 15% minimum)
  instances×120 = each instance handles 120 users before memory fills
  60            = maximum additional memory from user load
  jitter        = random.uniform(-1.5, 1.5)  → ±1.5% noise
  Result range  = 5% (minimum idle) to 100% (maximum)

Example 1: 0 users, 1 instance
  Memory = 15 + (0/120) × 60 = 15%  (just OS overhead)

Example 2: 600 users, 5 instances
  Memory = 15 + (600/(5×120)) × 60 = 15 + (600/600) × 60 = 15 + 60 = 75%
```

### Scale Out — Desired Instance Calculation

```
When CPU > 70%, how many instances do we need?

total_load = (cpu_usage / 100) × current_instances
desired    = ceil(total_load / 0.50)
new_count  = max(current_instances + 1, desired)
new_count  = min(new_count, 10)   ← never exceed max

Goal: bring CPU down to ~50% (0.50)

Example: CPU = 85%, current instances = 2
  total_load = (85/100) × 2 = 1.70
  desired    = ceil(1.70 / 0.50) = ceil(3.4) = 4
  new_count  = max(2+1, 4) = max(3, 4) = 4 instances
```

### Scale In — Desired Instance Calculation

```
When CPU < 30%, how many instances do we need?

Case 1: CPU < 5% AND users == 0
  new_count = 1  (drop to minimum immediately)

Case 2: CPU < 15%
  new_count = max(1, current_instances // 2)  (cut fleet in half)

Case 3: CPU between 15% and 30%
  total_load = (cpu_usage / 100) × current_instances
  desired    = ceil(total_load / 0.50)
  new_count  = max(1, min(desired, current_instances - 1))

Example: CPU = 20%, current instances = 6
  total_load = (20/100) × 6 = 1.2
  desired    = ceil(1.2 / 0.50) = ceil(2.4) = 3
  new_count  = max(1, min(3, 6-1)) = max(1, min(3,5)) = max(1, 3) = 3 instances
```

### Per-Instance CPU Formula

```
(inside InstanceInfo.tick())

instance_cpu = (users_per_instance / 100) × 100 + random.uniform(-5, 5)
             = users_per_instance + noise

users_per_instance = active_users / total_running_instances
```

### Per-Instance Memory Formula

```
(inside InstanceInfo.tick())

instance_memory = 15 + (users_per_instance / 120) × 60 + random.uniform(-3, 3)
```

### Instance Health Badge Logic

```
CPU > 90%  →  health = "critical"   (red badge)
CPU > 75%  →  health = "warning"    (yellow badge)
CPU ≤ 75%  →  health = "healthy"    (green badge)
boot phase →  health = "initializing" (purple badge)
```

### Cost Formulas

```
Cost per instance per hour  = $0.0116  (AWS t2.micro price)
Cost per instance per month = $0.0116 × 24 × 30 = $8.352

Current hourly cost  = instances × 0.0116
Current monthly cost = instances × 8.352
Fixed monthly cost   = 10 × 8.352 = $83.52  (always running max)

Savings %  = ((fixed_monthly - current_monthly) / fixed_monthly) × 100

Example: currently 2 instances
  current_monthly = 2 × 8.352 = $16.70
  savings %       = ((83.52 - 16.70) / 83.52) × 100 = 80%
```

### Password Hashing

```
salt       = secrets.token_hex(16)        → random 32-character string
hash       = PBKDF2-HMAC-SHA256(password, salt, iterations=100000)
stored     = "{salt}:{hash.hex()}"

To verify:
  1. Split stored string to get original salt
  2. Re-hash the input password with the same salt
  3. Compare — if equal → correct password
```

---

## 8. Auto Scaling Logic — Step by Step

Every 2 seconds, `apply_autoscaling(state)` runs this sequence:

```
STEP 1: Check cooldown
  └── If (current_time - last_scaled_time) < 2 seconds → SKIP (return early)

STEP 2: Start stabilization loop (max 10 rounds)
  │
  ├── STEP 2a: Recalculate CPU/Memory with current instance count
  │
  ├── STEP 2b: Check if CPU > 70% AND instances < 10
  │     YES → Calculate desired instances using formula
  │           Update instance count
  │           Increment total_scale_outs
  │           Log the event with timestamp and reason
  │           scaled = True
  │
  ├── STEP 2c: Check if CPU < 30% AND instances > 1
  │     YES → Determine new count based on CPU level:
  │             CPU < 5% + 0 users → go to 1 instance
  │             CPU < 15%          → halve the fleet
  │             otherwise          → calculate mathematically
  │           Update instance count
  │           Increment total_scale_ins
  │           Log the event
  │           scaled = True
  │
  ├── STEP 2d: If nothing changed (scaled = False) → break loop (stable)
  │
  └── STEP 2e: Recalculate CPU/Memory again → go back to STEP 2a

STEP 3: Record last_scaled_time = now (for cooldown check next tick)
```

---

## 9. Database Design

**File:** `cloudscale.db` (SQLite, auto-created on first run)

### Table: `users`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Auto-increments: 1, 2, 3... |
| `full_name` | TEXT NOT NULL | User's display name |
| `email` | TEXT UNIQUE | Must be unique, stored lowercase |
| `password_hash` | TEXT | Format: `"salt:hash"` — never plain text |
| `avatar_color` | TEXT | Hex color randomly assigned at signup (e.g. `#3b82f6`) |
| `created_at` | TIMESTAMP | Auto-set to signup time |

**WAL Mode:** Database uses Write-Ahead Logging (`PRAGMA journal_mode=WAL`) to prevent corruption if the app crashes mid-write.

---

## 10. Security Implementation

| Risk | How We Handle It |
|------|-----------------|
| Plain text passwords | PBKDF2-SHA256 hashing with 100,000 iterations + random salt per user |
| Same password → same hash | Each user gets a unique random salt (32 chars) |
| Brute force cracking | 100,000 hash iterations makes cracking extremely slow |
| Leaking which field was wrong | Login always returns "Invalid email or password" — never reveals which one |
| Unauthorized page access | `require_auth()` blocks all pages with `st.stop()` if not logged in |
| SQL injection | All queries use parameterized `?` placeholders — never string concatenation |
| Session hijacking | Session stored in Streamlit's `session_state` — server-side, not in cookies |

---

## 11. All Pages Explained

### Home.py — Live Dashboard
- Auto-refreshes every 2 seconds using `@st.fragment(run_every=2)`
- Shows: 4 metric cards (users, instances, CPU%, memory%), instance fleet grid, 2 charts, recent scaling events
- Status banner changes color: 🔴 High load / 🔵 Scaling in / 🟢 Stable
- Instance cards show individual CPU/memory bars and health badges

### Page 1 — Overview
- 3 Plotly gauge charts: CPU (blue), Memory (purple), Instance count (green with delta arrow)
- Color zones on gauges: green = safe, yellow = moderate, red = danger
- 4 metric stats: active users, total scale-outs, total scale-ins, total requests
- Status message at bottom

### Page 2 — System Architecture
- Visual vertical flow diagram: Users → Load Balancer → ASG → EC2 → CloudWatch
- Each component glows with color when it's actively working
- EC2 section shows one server icon per currently running instance
- Scaling rules summary cards at the bottom

### Page 3 — Load Generator
- Slider: 0 to 1000 users (step 50)
- Load level indicator: No Load / Low / Medium / High
- 3 buttons: Apply Load, Max Load (1000), Stop Load
- 5 quick preset buttons: 100, 300, 500, 750, 1000 users
- Current status message showing active users and instances

### Page 4 — Live Metrics
- 4 metric boxes with delta arrows (change from last reading)
- 2×2 Plotly subplot grid:
  - Top-left: CPU line chart (blue) with 70% and 30% dashed threshold lines
  - Top-right: Memory line chart (purple)
  - Bottom-left: Instance count chart (green) with dot markers
  - Bottom-right: User load chart (amber)
- Statistics table: Current / Average / Peak / Min for CPU and Memory

### Page 5 — Scaling Activity
- 4 stat boxes: total events, scale-outs, scale-ins, current instances
- Scaling event timeline cards (newest first):
  - Green cards = scale out (added servers)
  - Blue cards = scale in (removed servers)
  - Each card shows: time, from→to instances, CPU% at time of event, reason
- System logs in monospace font (color coded by type)
- Clear All Logs button

### Page 6 — Cost Analysis
- 4 cost metric cards: hourly cost, monthly cost, fixed 10-instance cost, savings %
- Bar chart: auto-scaled vs fixed 2/5/10 instances (monthly cost comparison)
- Donut chart: how often each instance count appeared in history
- AWS pricing reference table: t2.micro, t2.small, t2.medium, t2.large
- Key insight callout with live savings calculation

---

## 12. Data Flow — End to End

```
USER ACTION (e.g., sets 800 users in Load Generator)
         │
         ▼
state.active_users = 800
state.load_running = True
         │
         ▼ (every 2 seconds, Home.py fragment runs)
         │
    calculate_cpu(800, current_instances)
         │  CPU = (800 / (instances × 100)) × 100 + jitter
         ▼
    apply_autoscaling(state)
         │  CPU > 70%? → add instances
         │  Recalculate after each addition
         │  Loop until stable
         ▼
    calculate_cpu/memory again (final values)
         │
    state.tick_fleet()
         │  Each instance gets its share of users
         │  Each instance updates its own CPU/memory/requests
         │  Health badge set based on CPU
         ▼
    state.record_snapshot()
         │  Appends current values to history arrays
         │  Trims to last 100 entries
         ▼
    UI renders:
         │  Metric cards (users, instances, CPU%, memory%)
         │  Instance fleet grid (one card per instance)
         │  Charts (from history arrays)
         └  Scaling events (from state.scaling_events list)
```

---

## 13. How to Run

### Prerequisites
- Python 3.9 or higher

### Install Dependencies
```bash
pip install streamlit plotly
```

### Run the App
```bash
streamlit run Home.py
```

App opens at: **http://localhost:8501**

---

## 14. Demo Flow for Presentation

**Step 1 — Login**
Open the app. Click "Create Account". Enter name, email, password. Click Create Account.

**Step 2 — Show the empty dashboard**
Point out: 1 instance, 0 users, 0% CPU. Dashboard is live (green pulsing dot).

**Step 3 — Generate High Load**
Go to Load Generator → Click "1000 Users" preset → Click Apply Load.

**Step 4 — Watch Auto Scaling OUT**
Go back to Home. Watch:
- CPU shoots above 70%
- Red banner appears: "High load detected — Scaling OUT"
- New instance cards appear (instance-alpha, instance-beta, etc.)
- Instance count goes from 1 → 5, 6, 7, 8...

**Step 5 — Show Scaling Activity page**
Go to Page 5. Show the timeline of SCALE OUT events with timestamps and reasons.

**Step 6 — Stop the Load**
Go to Load Generator → Stop Load.

**Step 7 — Watch Auto Scaling IN**
Go back to Home. Watch:
- CPU drops below 30%
- Blue banner appears: "Low load — Scaling IN"
- Instance cards disappear one by one
- Returns to 1 instance

**Step 8 — Show Cost Savings**
Go to Page 6. Show: currently running 1 instance = $8.35/month vs $83.52 for 10 fixed = **90% savings**.

---

## 15. Cost Analysis

| Scenario | Hourly Cost | Monthly Cost | Savings vs Fixed |
|----------|------------|-------------|-----------------|
| 1 instance (auto-scaled idle) | $0.0116 | $8.35 | **90%** |
| 2 instances | $0.0232 | $16.70 | 80% |
| 5 instances | $0.0580 | $41.76 | 50% |
| 10 instances (always-on fixed) | $0.1160 | $83.52 | 0% (baseline) |

**Pricing Reference (AWS t2 instances):**

| Instance | vCPUs | Memory | Hourly | Monthly |
|----------|-------|--------|--------|---------|
| t2.micro | 1 | 1 GiB | $0.0116 | $8.35 |
| t2.small | 1 | 2 GiB | $0.0230 | $16.56 |
| t2.medium | 2 | 4 GiB | $0.0464 | $33.41 |
| t2.large | 2 | 8 GiB | $0.0928 | $66.82 |

---

## 16. SDG Contribution

### Primary: SDG 9 — Industry, Innovation and Infrastructure

> "Build resilient infrastructure, promote inclusive and sustainable industrialization and foster innovation."

- Teaches cloud infrastructure to students at zero cost
- Demonstrates how auto scaling makes infrastructure **efficient and resilient**
- Shows that modern infrastructure can **self-heal and self-optimize**

### Secondary SDGs

| SDG | Connection |
|-----|-----------|
| **SDG 4 — Quality Education** | Free tool to learn enterprise cloud concepts without AWS account |
| **SDG 12 — Responsible Consumption** | Auto scaling uses resources only when needed — no idle waste |
| **SDG 13 — Climate Action** | Fewer idle servers = less electricity consumed = lower carbon footprint |

**Environmental Impact:**
Data centers consume 1–2% of global electricity. If all cloud infrastructure used auto scaling optimally, it could reduce data center energy waste by up to 40%. Our project demonstrates this principle visually.

---

## 17. Future Scope

| Feature | Description |
|---------|-------------|
| Real AWS Integration | Connect to actual AWS via boto3 SDK to control real EC2 instances |
| Predictive Scaling | Use ML (time-series forecasting) to scale before load hits, not after |
| Kubernetes Simulation | Simulate Kubernetes Horizontal Pod Autoscaler (HPA) behavior |
| Multi-Region | Simulate traffic routing across multiple AWS regions with latency |
| Custom Metrics | Scale based on network I/O, disk usage, or request queue depth |
| Alert System | Email/SMS notifications when CPU crosses thresholds |
| Terraform Integration | Generate Infrastructure-as-Code from the simulation config |

---

## 18. Team

| Field | Details |
|-------|---------|
| **Project Name** | CloudScale — Dynamic Auto Scaling Simulation Platform |
| **Project Type** | Industry Oriented Mini Project (IOMP) |
| **Institution** | Sreyas Institute of Engineering and Technology |
| **Academic Year** | 2025–26 |
| **SDG Alignment** | SDG 9 — Industry, Innovation and Infrastructure |

---

*CloudScale Platform — Simulated AWS Auto Scaling. No real cloud resources used.*
