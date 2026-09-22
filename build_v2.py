"""
CloudScale Final Report — Build v2
Rebuilds from original iomp report.docx with proper:
  - Bookman Old Style font, 1.5 line spacing (matching original)
  - No bullet points — pure paragraphs
  - Code blocks only for actual source code
  - Page breaks before every chapter
  - Scenario analysis as flowing prose
  - Results described in text (user adds screenshots)
"""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
import copy

# ─── Open original document ───────────────────────────────────────────
doc = Document('iomp report.docx')

# ─── Helpers ──────────────────────────────────────────────────────────

BODY_FONT = 'Bookman Old Style'
CODE_FONT  = 'Courier New'


def _make_pPr(style_val='Normal', page_break_before=False,
              line_spacing_240=True, space_before=0, space_after=120,
              indent_left=0, shading_fill=None):
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style_val)
    pPr.append(pStyle)
    if page_break_before:
        pbr = OxmlElement('w:pageBreakBefore')
        pPr.append(pbr)
    if shading_fill:
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), shading_fill)
        pPr.append(shd)
    if indent_left:
        ind = OxmlElement('w:ind')
        ind.set(qn('w:left'), str(indent_left))
        pPr.append(ind)
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(space_before))
    spacing.set(qn('w:after'), str(space_after))
    if line_spacing_240:
        spacing.set(qn('w:line'), '360')       # 1.5 line spacing = 360 twentieths of a pt
        spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)
    return pPr


def _make_run(text, font_name=BODY_FONT, font_size_pt=12,
              bold=False, color_hex=None):
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'),  font_name)
    rFonts.set(qn('w:hAnsi'),  font_name)
    rFonts.set(qn('w:cs'),     font_name)
    rPr.append(rFonts)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(font_size_pt * 2)))
    rPr.append(sz)
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(font_size_pt * 2)))
    rPr.append(szCs)
    if bold:
        rPr.append(OxmlElement('w:b'))
    if color_hex:
        col = OxmlElement('w:color')
        col.set(qn('w:val'), color_hex)
        rPr.append(col)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    r.append(t)
    return r


def make_para(text, bold=False, page_break_before=False,
              space_after=120):
    """Standard body paragraph — Bookman Old Style, 12pt, 1.5 spacing."""
    p = OxmlElement('w:p')
    p.append(_make_pPr('Normal', page_break_before=page_break_before,
                        space_after=space_after))
    if text:
        p.append(_make_run(text, bold=bold))
    return p


def make_subheading(text, level=2):
    """Section heading — bold Bookman Old Style, 12pt, space above."""
    p = OxmlElement('w:p')
    pPr = _make_pPr('Normal', space_before=240, space_after=120,
                    line_spacing_240=True)
    p.append(pPr)
    p.append(_make_run(text, bold=True, font_size_pt=12 if level == 2 else 12))
    return p


def make_chapter_heading(text):
    """Chapter label — bold, page break before."""
    p = OxmlElement('w:p')
    p.append(_make_pPr('Normal', page_break_before=True,
                        space_before=0, space_after=120))
    p.append(_make_run(text, bold=True, font_size_pt=12))
    return p


def make_code(code_text):
    """Code block — Courier New 9pt, light blue background, tight spacing."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'Normal')
    pPr.append(pStyle)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'EEF2FF')
    pPr.append(shd)
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), '360')
    ind.set(qn('w:right'), '180')
    pPr.append(ind)
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '60')
    spacing.set(qn('w:after'), '60')
    spacing.set(qn('w:line'), '220')
    spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)
    p.append(pPr)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'),  CODE_FONT)
    rFonts.set(qn('w:hAnsi'),  CODE_FONT)
    rFonts.set(qn('w:cs'),     CODE_FONT)
    rPr.append(rFonts)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '18')     # 9pt
    rPr.append(sz)
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), '18')
    rPr.append(szCs)
    col = OxmlElement('w:color')
    col.set(qn('w:val'), '1E293B')
    rPr.append(col)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = code_text
    r.append(t)
    p.append(r)
    return p


def make_code_caption(text):
    """Small italic caption below a code block."""
    p = OxmlElement('w:p')
    pPr = _make_pPr('Normal', line_spacing_240=False,
                    space_before=0, space_after=200)
    p.append(pPr)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'),  BODY_FONT)
    rFonts.set(qn('w:hAnsi'),  BODY_FONT)
    rPr.append(rFonts)
    i = OxmlElement('w:i')
    rPr.append(i)
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '20')   # 10pt
    rPr.append(sz)
    col = OxmlElement('w:color')
    col.set(qn('w:val'), '64748B')
    rPr.append(col)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return p


def blank():
    return make_para('')


def insert_after(anchor_elem, new_elem):
    anchor_elem.addnext(new_elem)
    return new_elem


# ─── Step 1: Add page breaks before every chapter ─────────────────────
print("Adding page breaks before chapters...")

chapter_texts = ['CHAPTER 1', 'CHAPTER 2', 'CHAPTER 3',
                 'CHAPTER 4', 'CHAPTER 5', 'CHAPTER 6',
                 'CHAPTER 7', 'CHAPTER 8']

for para in doc.paragraphs:
    text = para.text.strip()
    if any(text.startswith(ch) for ch in chapter_texts):
        pPr = para._p.find(qn('w:pPr'))
        if pPr is None:
            pPr = OxmlElement('w:pPr')
            para._p.insert(0, pPr)
        pbr = OxmlElement('w:pageBreakBefore')
        pPr.insert(0, pbr)

# ─── Step 2: Find the "4.4 Sample Code" / "4.4 Code" paragraph ────────
print("Finding insertion anchor...")

anchor_idx = None
for i, p in enumerate(doc.paragraphs):
    if '4.4 Sample Code' in p.text or '4.4 Code' in p.text:
        anchor_idx = i
        break

print(f"  Anchor: paragraph {anchor_idx} — '{doc.paragraphs[anchor_idx].text}'")
anchor = doc.paragraphs[anchor_idx]._p

# ─── Step 3: Build Chapter 4 enhanced content ─────────────────────────
# Each item is a function call that returns a <w:p> element.
# We insert them one by one, each AFTER the previous anchor.
print("Building Chapter 4 content...")

items = []

# ── Intro paragraph for 4.4 ──────────────────────────────────────────
items.append(make_para(
    "The implementation of CloudScale is organized across six core backend modules and ten "
    "dashboard pages. Each backend module is designed as a standalone Python file with a single, "
    "well-defined responsibility, following the separation of concerns principle. The backend "
    "modules contain no Streamlit dependencies, making them independently testable and reusable. "
    "The dashboard pages import from the backend and handle only presentation logic. The following "
    "sections present the complete annotated source code for each module alongside a detailed "
    "explanation of its design decisions, algorithms, and role within the wider system."
))

# ══════════════════════════════════════════════
# 4.4.1 metrics.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.1  metrics.py — CPU and Memory Calculation Module"))

items.append(make_para(
    "The metrics.py module is the mathematical foundation of CloudScale. It exposes two pure "
    "functions, calculate_cpu() and calculate_memory(), that together model the resource "
    "utilization behavior of a distributed web server fleet. These functions are called every "
    "two seconds from both the main dashboard and the autoscaling engine, supplying fresh metric "
    "readings that drive all scaling decisions and chart updates across the application."
))
items.append(make_para(
    "The CPU formula is derived from a normalized load model where each virtual machine instance "
    "represents one unit of processing capacity, capable of handling exactly one hundred concurrent "
    "users at one hundred percent CPU utilization. The system-wide CPU is therefore the ratio of "
    "total active users to total system capacity expressed as a percentage. This linear model "
    "faithfully captures the fundamental relationship between demand and compute resources that "
    "governs autoscaling decisions in production environments. A uniform random jitter of plus or "
    "minus two percent is applied to simulate the measurement variance inherent in real Amazon "
    "CloudWatch metrics, preventing the charts from displaying unrealistic perfectly flat readings."
))
items.append(make_para(
    "The memory formula models utilization as a two-component function. A constant base overhead "
    "of fifteen percent represents the operating system kernel, background daemons, and the Python "
    "application framework that consume memory regardless of user traffic. This base is consistent "
    "with observations on a typical Linux instance running a Streamlit web application. The variable "
    "component scales proportionally with user load using a higher capacity constant of one hundred "
    "and twenty users per instance compared to one hundred for CPU, reflecting that memory pressure "
    "increases more gradually than compute pressure in stateless web applications. The maximum "
    "additional memory contribution is capped at sixty percent, yielding a theoretical maximum of "
    "seventy-five percent under full load, leaving headroom before memory exhaustion. A plus or "
    "minus one and a half percent jitter adds realistic variance to the readings."
))
items.append(make_code_caption("Source Code — backend/metrics.py"))
items.append(make_code(
"""import random

def calculate_cpu(users, instances):
    \"\"\"
    Compute system-wide CPU utilization percentage.

    Model: Each instance handles 100 users at 100% CPU.
    Formula: CPU% = (users / (instances * 100)) * 100 + jitter
    Jitter simulates realistic CloudWatch measurement variance (+-2%).
    \"\"\"
    if instances == 0:
        return 100.0                      # No instances = system crashed

    base   = (users / (instances * 100)) * 100
    jitter = random.uniform(-2, 2)        # +- 2% realistic noise
    return min(max(base + jitter, 0), 100.0)   # Clamp to [0, 100]


def calculate_memory(users, instances):
    \"\"\"
    Compute system-wide memory utilization percentage.

    Model: 15% OS base overhead + up to 60% from user load.
    Each instance serves 120 users before memory reaches maximum.
    Jitter simulates realistic measurement variance (+-1.5%).
    \"\"\"
    if instances == 0:
        return 95.0                       # No instances = near-full memory

    base   = 15 + (users / (instances * 120)) * 60
    jitter = random.uniform(-1.5, 1.5)   # +- 1.5% realistic noise
    return min(max(base + jitter, 5), 100.0)   # Clamp to [5, 100]"""))

# ══════════════════════════════════════════════
# 4.4.2 state.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.2  state.py — System State Management"))

items.append(make_para(
    "The state.py module defines two classes that together form the entire runtime memory of the "
    "CloudScale simulation. The InstanceInfo class models a single virtual machine instance, "
    "mirroring the properties exposed by the AWS EC2 DescribeInstances API. Each instance carries "
    "a randomly generated AWS-style identifier such as i-48293, a human-readable Greek-alphabet "
    "name in the format instance-alpha through instance-kappa, individual CPU and memory readings, "
    "a cumulative request counter, a lifecycle status flag, and a health badge."
))
items.append(make_para(
    "The InstanceInfo.tick() method simulates the instance lifecycle. Newly created instances begin "
    "in a launching state with a boot counter of two, representing four seconds of startup time. "
    "During this boot phase the instance shows only idle operating system level CPU and memory "
    "values, exactly replicating the real AWS EC2 behavior where a newly launched instance requires "
    "sixty to one hundred and twenty seconds before it accepts traffic. After the boot counter "
    "reaches zero the instance transitions to running status and begins receiving its proportional "
    "share of the total user load. The per-instance CPU is computed from the user load divided "
    "equally across all running instances, with a plus or minus five percent noise term to reflect "
    "the natural load imbalance seen in real fleets. The health badge is assigned as healthy when "
    "CPU is below seventy-five percent, warning between seventy-five and ninety percent, and "
    "critical above ninety percent."
))
items.append(make_para(
    "The SystemState class aggregates all instances into a single shared object stored in "
    "Streamlit's st.session_state dictionary, which ensures the simulation data persists "
    "seamlessly as the user navigates between the ten dashboard pages. Five parallel history "
    "arrays record timestamped snapshots of CPU usage, memory usage, instance count, user count, "
    "and Unix timestamps every two seconds, providing the data series for all time-series charts. "
    "The arrays are trimmed to one hundred entries to prevent unbounded memory growth, retaining "
    "approximately three minutes and twenty seconds of history. The sync_fleet() method maintains "
    "consistency between the integer instance counter modified by the autoscaler and the actual "
    "list of InstanceInfo objects, adding new instances or removing from the end of the list as "
    "the count changes."
))
items.append(make_code_caption("Source Code — backend/state.py"))
items.append(make_code(
"""import time
import random
import streamlit as st

INSTANCE_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon",
    "zeta", "eta", "theta", "iota", "kappa"
]


class InstanceInfo:
    \"\"\"Models one individual EC2-like server instance.\"\"\"

    def __init__(self, index):
        self.id        = f"i-{random.randint(10000, 99999)}"   # AWS-style ID
        self.name      = f"instance-{INSTANCE_NAMES[index % len(INSTANCE_NAMES)]}"
        self.cpu       = 0.0
        self.memory    = 0.0
        self.requests  = 0
        self.status    = "launching"
        self.health    = "initializing"
        self.launched_at  = time.time()
        self._boot_ticks  = 2          # 2 ticks x 2s = 4-second simulated boot delay

    def tick(self, users_per_instance):
        \"\"\"Update this instance's metrics for one 2-second tick.\"\"\"
        if self._boot_ticks > 0:
            self._boot_ticks -= 1
            self.status = "launching"
            self.health = "initializing"
            self.cpu    = random.uniform(5, 15)    # OS startup CPU
            self.memory = random.uniform(10, 20)   # OS startup memory
            return

        self.status = "running"
        if users_per_instance > 0:
            self.cpu     = min(100, (users_per_instance / 100) * 100
                               + random.uniform(-5, 5))
            self.memory  = min(100, 15 + (users_per_instance / 120) * 60
                               + random.uniform(-3, 3))
            self.requests += int(users_per_instance * random.uniform(0.8, 1.2))
        else:
            self.cpu    = max(0, random.uniform(1, 8))
            self.memory = max(5, random.uniform(8, 18))

        self.cpu    = round(max(0, self.cpu), 1)
        self.memory = round(max(0, self.memory), 1)

        if self.cpu > 90:    self.health = "critical"
        elif self.cpu > 75:  self.health = "warning"
        else:                self.health = "healthy"


class SystemState:
    \"\"\"Central data store — persists across all page navigations via session_state.\"\"\"

    def __init__(self):
        self.active_users   = 0
        self.instances      = 1
        self.cpu_usage      = 0.0
        self.memory_usage   = 0.0
        self.load_running   = False
        self.instance_fleet = [InstanceInfo(0)]   # Start with one instance

        # Rolling history arrays (last 100 entries = ~3.3 minutes)
        self.history_cpu        = []
        self.history_memory     = []
        self.history_instances  = []
        self.history_users      = []
        self.history_timestamps = []

        self.logs            = []
        self.scaling_events  = []
        self.last_scaled_time = time.time()
        self.total_requests   = 0
        self.total_scale_outs = 0
        self.total_scale_ins  = 0

    def sync_fleet(self):
        \"\"\"Keep instance_fleet list in sync with self.instances integer.\"\"\"
        while len(self.instance_fleet) < self.instances:
            self.instance_fleet.append(InstanceInfo(len(self.instance_fleet)))
        while len(self.instance_fleet) > self.instances:
            self.instance_fleet.pop()

    def tick_fleet(self):
        \"\"\"Update all instance metrics for one tick. Users split equally.\"\"\"
        self.sync_fleet()
        n = len(self.instance_fleet)
        users_per = self.active_users / n if n > 0 else 0
        for inst in self.instance_fleet:
            inst.tick(users_per)

    def get_fleet_summary(self):
        return [{"id": i.id, "name": i.name, "cpu": i.cpu,
                 "memory": i.memory, "requests": i.requests,
                 "status": i.status, "health": i.health}
                for i in self.instance_fleet]

    def record_snapshot(self):
        self.history_cpu.append(round(self.cpu_usage, 1))
        self.history_memory.append(round(self.memory_usage, 1))
        self.history_instances.append(self.instances)
        self.history_users.append(self.active_users)
        self.history_timestamps.append(time.time())
        if len(self.history_cpu) > 100:
            self.history_cpu        = self.history_cpu[-100:]
            self.history_memory     = self.history_memory[-100:]
            self.history_instances  = self.history_instances[-100:]
            self.history_users      = self.history_users[-100:]
            self.history_timestamps = self.history_timestamps[-100:]


def get_state():
    if "system_state" not in st.session_state:
        st.session_state["system_state"] = SystemState()
    return st.session_state["system_state"]"""))

# ══════════════════════════════════════════════
# 4.4.3 autoscaler.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.3  autoscaler.py — Auto Scaling Engine"))

items.append(make_para(
    "The autoscaler.py module contains the core algorithmic logic of CloudScale. Its single "
    "public function, apply_autoscaling(), implements the same decision process used by an AWS "
    "Auto Scaling Group working in conjunction with CloudWatch metric alarms. The function is "
    "invoked every two seconds from the live dashboard fragment, operating as a continuous "
    "monitoring and adjustment loop over the entire lifetime of the simulation session."
))
items.append(make_para(
    "The function begins with a cooldown check that compares the current time against the "
    "timestamp of the last scaling action. If fewer than two seconds have elapsed, the function "
    "returns immediately without making any changes. This cooldown mechanism prevents the "
    "phenomenon known as thrashing, where the system oscillates rapidly between scale-out and "
    "scale-in events faster than the load can stabilize. In real AWS environments, the default "
    "cooldown period is three hundred seconds; CloudScale uses two seconds to allow the full "
    "scaling lifecycle to be observed within a short demonstration session."
))
items.append(make_para(
    "If the cooldown has passed, the function enters a stabilization loop that runs for up to "
    "ten rounds per tick. In each round, current CPU and memory values are recalculated, then a "
    "scaling decision is made. When CPU exceeds seventy percent and the fleet is below the "
    "maximum of ten instances, a scale-out is triggered using the target-tracking formula. The "
    "formula calculates the total load in instance-equivalent units by multiplying CPU percentage "
    "by current instance count, then divides by a target utilization of fifty percent and takes "
    "the ceiling. This computes the exact number of instances needed to bring CPU down to fifty "
    "percent in a single step, which is the same calculation used by AWS Target Tracking Scaling "
    "Policies. A hard floor of current count plus one ensures at least one new instance is always "
    "added, and a hard ceiling of ten prevents exceeding the defined maximum. When CPU falls below "
    "thirty percent and more than one instance is running, a scale-in is triggered. Three distinct "
    "sub-cases handle different degrees of underutilization: near-zero CPU with no active users "
    "causes an immediate drop to the minimum of one instance; CPU below fifteen percent halves "
    "the fleet; and CPU between fifteen and thirty percent uses the same load-based formula as "
    "scale-out but capped to remove at most the surplus capacity."
))
items.append(make_code_caption("Source Code — backend/autoscaler.py"))
items.append(make_code(
"""import time
import math
from datetime import datetime
from backend.metrics import calculate_cpu, calculate_memory

SCALE_OUT_THRESHOLD = 70    # CPU% above this triggers scale-out
SCALE_IN_THRESHOLD  = 30    # CPU% below this triggers scale-in
COOLDOWN     = 2            # Minimum seconds between scaling actions
MAX_INSTANCES = 10
MIN_INSTANCES = 1


def apply_autoscaling(state):
    \"\"\"
    Core autoscaling decision engine — mirrors AWS Auto Scaling Group logic.
    Called every 2 seconds. Uses a stabilization loop to converge to a
    stable fleet size in a single tick when possible.
    \"\"\"
    now = time.time()

    if now - state.last_scaled_time < COOLDOWN:
        return    # Still in cooldown — skip this tick

    for _ in range(10):   # Stabilization loop: up to 10 rounds per tick
        state.cpu_usage    = calculate_cpu(state.active_users, state.instances)
        state.memory_usage = calculate_memory(state.active_users, state.instances)
        scaled = False

        # ── SCALE OUT ──────────────────────────────────────────────────
        if state.cpu_usage > SCALE_OUT_THRESHOLD and state.instances < MAX_INSTANCES:
            old = state.instances
            total_load = (state.cpu_usage / 100) * state.instances
            desired    = math.ceil(total_load / 0.5)   # Target 50% CPU
            new_count  = min(max(old + 1, desired), MAX_INSTANCES)
            state.instances = new_count
            state.total_scale_outs += 1
            _log_event(state, "SCALE OUT", "up", old, new_count,
                       f"CPU {state.cpu_usage:.1f}% > {SCALE_OUT_THRESHOLD}%"
                       f" - added {new_count - old} instance(s)")
            scaled = True

        # ── SCALE IN ───────────────────────────────────────────────────
        elif state.cpu_usage < SCALE_IN_THRESHOLD and state.instances > MIN_INSTANCES:
            old = state.instances
            if state.cpu_usage < 5 and state.active_users == 0:
                new_count = MIN_INSTANCES                         # Case 1: fully idle
            elif state.cpu_usage < 15:
                new_count = max(MIN_INSTANCES, old // 2)          # Case 2: halve fleet
            else:
                total_load = (state.cpu_usage / 100) * state.instances
                desired    = math.ceil(total_load / 0.5)
                new_count  = max(MIN_INSTANCES, min(desired, old - 1))  # Case 3
            if new_count < old:
                state.instances = new_count
                state.total_scale_ins += 1
                _log_event(state, "SCALE IN", "down", old, new_count,
                           f"CPU {state.cpu_usage:.1f}% < {SCALE_IN_THRESHOLD}%"
                           f" - removed {old - new_count} instance(s)")
                scaled = True

        if not scaled:
            break   # System is stable — exit the stabilization loop

        state.cpu_usage    = calculate_cpu(state.active_users, state.instances)
        state.memory_usage = calculate_memory(state.active_users, state.instances)

    state.last_scaled_time = now


def _log_event(state, event_type, direction, old_count, new_count, reason):
    state.scaling_events.append({
        "time":      datetime.now().strftime("%H:%M:%S"),
        "type":      event_type,
        "direction": direction,
        "from":      old_count,
        "to":        new_count,
        "cpu":       round(state.cpu_usage, 1),
        "reason":    reason,
    })
    state.logs.append(
        f"[{event_type}] {old_count} to {new_count} instances "
        f"(CPU: {state.cpu_usage:.1f}%)"
    )"""))

# ══════════════════════════════════════════════
# 4.4.4 db.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.4  db.py — Database Operations Module"))

items.append(make_para(
    "The db.py module handles all persistent storage for the user authentication system using "
    "SQLite as the database backend. SQLite was selected because it requires no external server "
    "process, stores the entire database in a single portable file named cloudscale.db, and is "
    "available in Python's standard library without additional installation. The database file "
    "is created automatically when the application starts for the first time, making deployment "
    "a simple matter of running the application with no pre-configuration required."
))
items.append(make_para(
    "Password security follows the OWASP Authentication Cheat Sheet and NIST SP 800-132 "
    "guidelines. The PBKDF2-HMAC-SHA256 algorithm is applied with one hundred thousand iterations, "
    "the same mechanism used by Django's default password hasher, AWS Cognito, and the majority "
    "of production authentication frameworks. Each user's password is combined with a unique "
    "one hundred and twenty-eight bit random salt generated by Python's cryptographically secure "
    "secrets module before hashing. The salt and the resulting hash are stored together as a single "
    "string in the format salt-colon-hash-hex, making the stored value entirely self-contained. "
    "During login, the salt is extracted from the stored value, the submitted password is re-hashed "
    "with that same salt, and the result is compared byte-for-byte with the stored hash. Plain "
    "text passwords are never stored anywhere in the system."
))
items.append(make_para(
    "Every SQL query in the module uses parameterized placeholders in the form of question marks "
    "rather than string concatenation, completely eliminating the risk of SQL injection attacks. "
    "The database connection is opened with Write-Ahead Logging mode enabled, which prevents "
    "database corruption if the application is terminated mid-write and allows multiple concurrent "
    "readers while a write is in progress — an important property for a Streamlit application "
    "where multiple browser tabs may share a single SQLite file. The login function returns the "
    "identical error message whether the email address is not found or the password is incorrect, "
    "a deliberate security measure that prevents attackers from enumerating which email addresses "
    "are registered in the system."
))
items.append(make_code_caption("Source Code — backend/db.py"))
items.append(make_code(
"""import sqlite3, os, hashlib, secrets

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cloudscale.db")
AVATAR_COLORS = ['#3b82f6','#22c55e','#a855f7','#f59e0b',
                 '#ef4444','#06b6d4','#ec4899','#14b8a6']


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # Prevents corruption on crash
    return conn


def init_db():
    conn = get_db()
    conn.executescript(\"\"\"
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT    NOT NULL,
            avatar_color  TEXT    DEFAULT '#3b82f6',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    \"\"\")
    conn.commit(); conn.close()

init_db()   # Runs on every import — safe due to IF NOT EXISTS


def _hash_password(password, salt=None):
    \"\"\"
    PBKDF2-HMAC-SHA256 with 100,000 iterations and a unique per-user salt.
    Returns: 'salt:hash_hex' stored as a single string.
    The same password produces a completely different stored value for
    every user because each salt is 128-bit cryptographically random.
    \"\"\"
    if salt is None:
        salt = secrets.token_hex(16)           # 128-bit random salt
    h = hashlib.pbkdf2_hmac('sha256', password.encode(),
                             salt.encode(), 100_000)
    return f"{salt}:{h.hex()}"


def _verify_password(password, stored):
    salt, _ = stored.split(':', 1)
    return _hash_password(password, salt) == stored


def signup(full_name, email, password):
    if not full_name or not email or not password:
        return None, "All fields are required."
    if len(password) < 6:
        return None, "Password must be at least 6 characters."
    if '@' not in email or '.' not in email:
        return None, "Please enter a valid email."
    conn = get_db()
    if conn.execute("SELECT id FROM users WHERE email=?",
                    (email.lower(),)).fetchone():
        conn.close()
        return None, "An account with this email already exists."
    pw   = _hash_password(password)
    color = secrets.choice(AVATAR_COLORS)
    cur  = conn.execute(
        "INSERT INTO users (full_name, email, password_hash, avatar_color)"
        " VALUES (?,?,?,?)",
        (full_name.strip(), email.lower().strip(), pw, color))
    conn.commit()
    user = conn.execute(
        "SELECT id, full_name, email, avatar_color, created_at"
        " FROM users WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(user), None


def login(email, password):
    if not email or not password:
        return None, "Email and password are required."
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?",
                        (email.lower().strip(),)).fetchone()
    conn.close()
    # Same error for wrong email AND wrong password — no enumeration
    if not user or not _verify_password(password, user['password_hash']):
        return None, "Invalid email or password."
    return {'id': user['id'], 'full_name': user['full_name'],
            'email': user['email'], 'avatar_color': user['avatar_color'],
            'created_at': user['created_at']}, None"""))

# ══════════════════════════════════════════════
# 4.4.5 auth.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.5  auth.py — Authentication User Interface"))

items.append(make_para(
    "The auth.py module implements the premium login and signup user interface that serves as "
    "the entry gate to CloudScale. The design follows a glassmorphism aesthetic — a contemporary "
    "UI language used by products such as Vercel, Linear, and Notion, featuring frosted glass "
    "cards with semi-transparent backgrounds, backdrop blur effects, and layered gradients. "
    "The entire visual style is achieved through CSS injected via Streamlit's st.markdown() "
    "function with the unsafe_allow_html parameter enabled, requiring no external frontend "
    "framework."
))
items.append(make_para(
    "The animated background consists of two floating gradient orbs — one blue positioned at "
    "the top right and one purple at the bottom left — rendered as CSS pseudo-elements on the "
    "application root. These elements animate independently with sixteen and twenty second "
    "floating cycles using CSS keyframe animations, creating a sense of depth and motion without "
    "any JavaScript. A gradient accent line along the top of the viewport pulses in opacity on "
    "a four second cycle. All Streamlit default interface chrome including the sidebar, navigation "
    "bar, toolbar, and footer is hidden with CSS on the login page, presenting a clean full-screen "
    "product landing page to first-time visitors."
))
items.append(make_para(
    "The layout uses a three-column Streamlit split where the wider left column contains the "
    "product logo, headline copy, three animated feature highlight cards, and a system status "
    "line. The narrower right column holds the authentication card with two tabs for Sign In "
    "and Create Account. Three utility functions form the rest of the authentication API: "
    "get_user() reads the current user from session state, require_auth() blocks any page "
    "immediately with st.stop() if no authenticated user exists, and show_user_sidebar() "
    "renders the user avatar badge, name, email, and Sign Out button at the bottom of the "
    "sidebar on every protected page."
))
items.append(make_code_caption("Source Code — backend/auth.py (core functions)"))
items.append(make_code(
"""import streamlit as st
from backend.db import signup, login


def get_user():
    \"\"\"Return the logged-in user dict or None if not authenticated.\"\"\"
    return st.session_state.get("auth_user", None)


def require_auth():
    \"\"\"
    Enforce authentication on any page.
    Place at the top of every page before rendering any content.
    Calls st.stop() immediately if no user is logged in, ensuring
    that no page content is ever rendered to unauthenticated users.
    \"\"\"
    user = get_user()
    if not user:
        st.warning("Please sign in from the Home page to access this feature.")
        st.stop()
    return user


def show_user_sidebar():
    \"\"\"Render user avatar, name, email, and Sign Out button in sidebar.\"\"\"
    user = get_user()
    if not user:
        return
    with st.sidebar:
        st.divider()
        col1, col2 = st.columns([1, 3])
        with col1:
            initial = user['full_name'][0].upper() if user['full_name'] else 'U'
            color   = user.get("avatar_color", "#3b82f6")
            st.markdown(
                f'<div style="width:38px;height:38px;border-radius:10px;'
                f'background:linear-gradient(135deg,{color},#6366f1);'
                f'display:flex;align-items:center;justify-content:center;'
                f'color:white;font-weight:700;font-size:16px">'
                f'{initial}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f"**{user['full_name']}**")
            st.caption(user['email'])
        if st.button("Sign Out", use_container_width=True, key="logout_btn"):
            del st.session_state["auth_user"]
            st.rerun()


def show_login_page():
    \"\"\"
    Full-page glassmorphism login and signup UI.
    Hides all Streamlit chrome. Returns True if already authenticated.
    CSS injected for: dark background, animated orbs, pill tabs,
    glassmorphic inputs, gradient submit button with glow.
    \"\"\"
    if get_user():
        return True

    # Full CSS block injected here (approx 200 lines) covering:
    # - Streamlit chrome hiding  - Dark app background with radial gradients
    # - Animated ::before/::after orbs   - Tab pill toggle styling
    # - Text input glassmorphic style    - Gradient submit button with glow hover
    st.markdown(\"\"\"<style>
    [data-testid="stSidebar"], header, #MainMenu, footer,
    .stDeployButton { display: none !important; }
    .stApp { background: #030712 !important; }
    </style>\"\"\", unsafe_allow_html=True)

    col_brand, _, col_auth = st.columns([1.15, 0.15, 0.85])

    with col_brand:
        st.markdown(
            '<h1 style="font-size:46px;font-weight:800;color:#f9fafb">'
            'Infrastructure that '
            '<span style="background:linear-gradient(135deg,#60a5fa,#a78bfa);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent">'
            'scales with you.</span></h1>', unsafe_allow_html=True)

    with col_auth:
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])
        with tab_login:
            with st.form("login_form", border=False):
                em = st.text_input("Email", placeholder="you@company.com")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    user, err = login(em, pw)
                    if err:  st.error(err)
                    else:
                        st.session_state["auth_user"] = user
                        st.rerun()
        with tab_signup:
            with st.form("signup_form", border=False):
                nm = st.text_input("Full Name")
                em = st.text_input("Email")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    user, err = signup(nm, em, pw)
                    if err:  st.error(err)
                    else:
                        st.session_state["auth_user"] = user
                        st.rerun()
    return False"""))

# ══════════════════════════════════════════════
# 4.4.6 Home.py
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_subheading("4.4.6  Home.py — Main Live Dashboard"))

items.append(make_para(
    "Home.py is the entry point of the CloudScale application. The most architecturally "
    "significant feature it employs is Streamlit's fragment system, specifically the "
    "@st.fragment(run_every=2) decorator applied to the live_dashboard function. Unlike the "
    "st.rerun() approach which re-executes the entire page script including CSS injection, "
    "header rendering, and sidebar setup, a fragment re-renders only its own output section "
    "at the specified interval. This means static elements such as the page header and injected "
    "styles are rendered once at load time and remain completely stable, while the dynamic "
    "dashboard content refreshes smoothly every two seconds without any visible flickering or "
    "layout shift. This produces a professional live monitoring experience comparable to real "
    "infrastructure dashboards."
))
items.append(make_para(
    "The execution sequence inside the live_dashboard fragment deliberately mirrors the control "
    "loop of a real cloud monitoring agent. First, CPU and memory are calculated from the current "
    "user count and instance count. Second, the autoscaling engine runs, which may modify the "
    "instance count if thresholds are crossed. Third, metrics are recalculated to reflect the "
    "updated instance count resulting from any scaling actions. Fourth, per-instance metrics "
    "are updated by calling tick_fleet(). Fifth, the current values are recorded to the history "
    "arrays. Only after all data has been updated does the user interface render, ensuring that "
    "every visible element shows a fully consistent, synchronized state. A dynamic status banner "
    "at the top changes between red, blue, and green based on whether the system is scaling out, "
    "scaling in, or stable, giving the user instant visual feedback on system state."
))
items.append(make_code_caption("Source Code — Home.py"))
items.append(make_code(
"""import streamlit as st
from backend.state import get_state
from backend.metrics import calculate_cpu, calculate_memory
from backend.autoscaler import apply_autoscaling
from backend.auth import show_login_page, show_user_sidebar, get_user

st.set_page_config(page_title="CloudScale Platform",
                   page_icon="cloud", layout="wide",
                   initial_sidebar_state="expanded")

if not get_user():           # Authentication gate
    show_login_page()
    st.stop()

st.markdown(\"\"\"<style>
    .stApp { background-color: #f8fafc !important; }
    .metric-card {
        background:#ffffff; border:1px solid #e2e8f0;
        border-radius:16px; padding:24px; text-align:center;
    }
    .status-scaling-out { background:#fef2f2; border:1px solid #fecaca; color:#dc2626; }
    .status-scaling-in  { background:#eff6ff; border:1px solid #bfdbfe; color:#2563eb; }
    .status-stable      { background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a; }
    .inst-card {
        background:#ffffff; border:1px solid #e2e8f0;
        border-radius:14px; padding:16px;
    }
    .live-dot {
        display:inline-block; width:8px; height:8px; border-radius:50%;
        background:#22c55e; animation:livePulse 2s ease-in-out infinite;
    }
    @keyframes livePulse {
        0%,100% { opacity:1; box-shadow:0 0 0 0 rgba(34,197,94,0.4); }
        50%      { opacity:0.7; box-shadow:0 0 0 6px rgba(34,197,94,0); }
    }
</style>\"\"\", unsafe_allow_html=True)

show_user_sidebar()

# Header rendered once — outside the fragment so it never flickers
st.markdown('<span style="font-size:1.6rem;font-weight:800;'
            'background:linear-gradient(135deg,#3b82f6,#6366f1);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent">'
            'CloudScale Dashboard</span>', unsafe_allow_html=True)
st.caption(f"Logged in as **{get_user()['full_name']}** - real-time monitoring")


@st.fragment(run_every=2)
def live_dashboard():
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    state = get_state()

    # Step 1 — calculate metrics with current state
    state.cpu_usage    = calculate_cpu(state.active_users, state.instances)
    state.memory_usage = calculate_memory(state.active_users, state.instances)

    # Step 2 — run autoscaler (may change state.instances)
    apply_autoscaling(state)

    # Step 3 — recalculate with potentially updated instance count
    state.cpu_usage    = calculate_cpu(state.active_users, state.instances)
    state.memory_usage = calculate_memory(state.active_users, state.instances)

    # Step 4 — update per-instance metrics
    state.tick_fleet()

    # Step 5 — record snapshot for history charts
    state.record_snapshot()

    if state.load_running:
        state.total_requests += state.active_users

    # Step 6 — render UI
    if state.cpu_usage > 70:
        banner = ('status-scaling-out',
                  'High load detected - Auto Scaling OUT in progress')
    elif state.cpu_usage < 30 and state.instances > 1:
        banner = ('status-scaling-in',
                  'Low load - Auto Scaling IN to optimize costs')
    else:
        banner = ('status-stable', 'System stable - All instances healthy')

    st.markdown(
        f'<div class="status-banner {banner[0]}">{banner[1]}</div>',
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cpu_col = ("#ef4444" if state.cpu_usage > 70
               else "#f59e0b" if state.cpu_usage > 50 else "#22c55e")
    mem_col = ("#ef4444" if state.memory_usage > 80
               else "#f59e0b" if state.memory_usage > 60 else "#22c55e")

    for col, icon, label, value, extra in [
        (c1, "Users",     "Active Users",    f"{state.active_users:,}", ""),
        (c2, "Server",    "Active Instances", str(state.instances),     "Min 1 / Max 10"),
        (c3, "CPU",       "CPU Usage",
         f'<span style="color:{cpu_col}">{state.cpu_usage:.1f}%</span>', ""),
        (c4, "Memory",    "Memory Usage",
         f'<span style="color:{mem_col}">{state.memory_usage:.1f}%</span>', ""),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:0.82rem;color:#64748b">{label}</div>'
                f'<div style="font-size:1.9rem;font-weight:700">{value}</div>'
                f'<div style="font-size:0.75rem;color:#94a3b8">{extra}</div>'
                f'</div>', unsafe_allow_html=True)

    # Instance fleet grid
    st.markdown("### Instance Fleet")
    fleet = state.get_fleet_summary()
    for row in range(0, len(fleet), 5):
        cols = st.columns(5)
        for i, inst in enumerate(fleet[row:row+5]):
            cc = ("#ef4444" if inst["cpu"] > 75
                  else "#f59e0b" if inst["cpu"] > 50 else "#22c55e")
            with cols[i]:
                st.markdown(
                    f'<div class="inst-card">'
                    f'<b>{inst["name"]}</b><br>'
                    f'<small style="color:#94a3b8;font-family:monospace">'
                    f'{inst["id"]}</small><br>'
                    f'CPU <b style="color:{cc}">{inst["cpu"]}%</b> &nbsp; '
                    f'Mem {inst["memory"]}%</div>', unsafe_allow_html=True)

    # Charts
    if len(state.history_cpu) > 1:
        c_left, c_right = st.columns(2)
        lo = dict(template="plotly_white", height=300,
                  margin=dict(l=20,r=20,t=40,b=20),
                  paper_bgcolor='#ffffff', plot_bgcolor='#ffffff')
        with c_left:
            fig = go.Figure([
                go.Scatter(y=state.history_cpu, name='CPU %',
                           line=dict(color='#3b82f6', width=2.5),
                           fill='tozeroy', fillcolor='rgba(59,130,246,0.06)'),
                go.Scatter(y=state.history_memory, name='Memory %',
                           line=dict(color='#8b5cf6', width=2.5)),
            ])
            fig.add_hline(y=70, line_dash="dash",
                          line_color="rgba(239,68,68,0.4)",
                          annotation_text="Scale Out")
            fig.add_hline(y=30, line_dash="dash",
                          line_color="rgba(59,130,246,0.4)",
                          annotation_text="Scale In")
            fig.update_layout(title="CPU & Memory Utilization",
                              yaxis_range=[0,100], **lo)
            st.plotly_chart(fig, use_container_width=True)
        with c_right:
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Scatter(y=state.history_instances,
                name='Instances', line=dict(color='#22c55e', width=2.5)),
                secondary_y=False)
            fig2.add_trace(go.Scatter(y=state.history_users,
                name='Users', line=dict(color='#f59e0b', width=2.5),
                fill='tozeroy', fillcolor='rgba(245,158,11,0.05)'),
                secondary_y=True)
            fig2.update_layout(title="Instances & User Load", **lo)
            st.plotly_chart(fig2, use_container_width=True)

    # Scaling events
    st.markdown("### Recent Scaling Events")
    if state.scaling_events:
        for ev in reversed(state.scaling_events[-5:]):
            icon = "Scale Out" if ev["direction"] == "up" else "Scale In"
            st.markdown(
                f'<div class="event-card">'
                f'<b>{icon}</b> - {ev["from"]} to {ev["to"]} instances | '
                f'{ev["time"]} | {ev["reason"]}</div>',
                unsafe_allow_html=True)
    else:
        st.info("No scaling events yet. Use Load Generator to simulate traffic.")


live_dashboard()"""))

# ══════════════════════════════════════════════
# 4.5 MATHEMATICAL FORMULATIONS
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.5  Mathematical Formulations"))

items.append(make_para(
    "CloudScale implements a set of deterministic mathematical formulas derived from distributed "
    "systems theory and validated against documented AWS CloudWatch behavior patterns. These "
    "formulas govern all metric calculations, autoscaling decisions, and cost computations within "
    "the simulation. Understanding these formulas is essential to appreciating how the simulation "
    "faithfully replicates real cloud infrastructure behavior."
))

items.append(blank())
items.append(make_subheading("4.5.1  CPU Utilization Model"))
items.append(make_para(
    "The CPU utilization model treats each virtual machine instance as a processing unit with a "
    "normalized capacity of one hundred concurrent users at one hundred percent CPU. The "
    "system-wide CPU percentage is the ratio of total active users to total system capacity. A "
    "random noise term of plus or minus two percent simulates the measurement variance inherent "
    "in real monitoring systems. The output is clamped to the range zero to one hundred to "
    "prevent invalid readings. The formula is expressed as:"
))
items.append(make_code(
"""CPU (%) = [ active_users / (instances x 100) ] x 100  +  jitter

  active_users  = total concurrent simulated users  (0 to 1000)
  instances     = number of running EC2 instances   (1 to 10)
  jitter        = random.uniform(-2, 2)             (+- 2% noise)
  Output range  = [0.0, 100.0]

Example — 500 users across 5 instances:
  CPU = (500 / 500) x 100 = 100%  ->  scale-out fires immediately

Example — 500 users across 10 instances:
  CPU = (500 / 1000) x 100 = 50%  ->  stable, no scaling action

Example — 50 users across 5 instances:
  CPU = (50 / 500) x 100 = 10%  ->  scale-in fires"""))

items.append(blank())
items.append(make_subheading("4.5.2  Memory Utilization Model"))
items.append(make_para(
    "Memory utilization is modeled as a two-component additive function. A constant base "
    "overhead of fifteen percent represents the operating system, runtime libraries, and "
    "application server consuming memory regardless of user traffic. The variable component "
    "scales proportionally with load but uses a higher capacity constant of one hundred and "
    "twenty users per instance, reflecting that memory pressure increases more slowly than "
    "CPU pressure. Plus or minus one and a half percent noise is applied. Memory never triggers "
    "scaling in CloudScale, matching the default AWS configuration where CPU is the primary "
    "autoscaling metric. The formula is:"
))
items.append(make_code(
"""Memory (%) = 15 + [ active_users / (instances x 120) ] x 60  +  jitter

  15     = constant OS base overhead (always present)
  120    = users per instance before memory component reaches maximum
  60     = maximum additional memory percentage from user load
  jitter = random.uniform(-1.5, 1.5)
  Output range = [5.0, 100.0]

Example — zero users:
  Memory = 15 + 0 = 15%  (pure OS overhead, regardless of instance count)

Example — 600 users, 5 instances:
  Memory = 15 + (600 / 600) x 60 = 15 + 60 = 75%"""))

items.append(blank())
items.append(make_subheading("4.5.3  Scale-Out Formula"))
items.append(make_para(
    "When CPU exceeds seventy percent, the autoscaler calculates the exact number of instances "
    "required to bring CPU down to a target of fifty percent using the target-tracking formula "
    "identical to AWS Target Tracking Scaling Policies. The formula computes the total load in "
    "instance-equivalent units and divides by the target utilization to find the required count. "
    "A floor of current count plus one ensures at least one new instance is always added. A "
    "ceiling of ten prevents exceeding the maximum fleet size."
))
items.append(make_code(
"""When CPU > 70% and instances < 10:

  total_load = (cpu_usage / 100) x current_instances
  desired    = ceil( total_load / 0.50 )
  new_count  = max(current_instances + 1, desired)
  new_count  = min(new_count, 10)

Example — CPU 85%, 2 instances:
  total_load = (85/100) x 2 = 1.70 load units
  desired    = ceil(1.70 / 0.50) = ceil(3.40) = 4
  new_count  = max(3, 4) = 4 instances
  CPU after  = (200 users / (4 x 100)) x 100 = 50%  ->  stable"""))

items.append(blank())
items.append(make_subheading("4.5.4  Scale-In Formula"))
items.append(make_para(
    "The scale-in formula applies three cases based on the degree of underutilization. Near-zero "
    "CPU with no active users causes an immediate drop to the minimum of one instance. CPU below "
    "fifteen percent halves the fleet, reflecting severe over-provisioning. CPU between fifteen "
    "and thirty percent applies the same target-tracking calculation as scale-out but ensures "
    "at least one instance is always removed and the count never drops below the minimum of one."
))
items.append(make_code(
"""When CPU < 30% and instances > 1:

  Case 1 — CPU < 5% AND users == 0:
    new_count = 1  (drop to minimum immediately — no traffic at all)

  Case 2 — CPU < 15%:
    new_count = max(1, floor(instances / 2))  (halve the fleet)

  Case 3 — 15% <= CPU < 30%:
    total_load = (cpu_usage / 100) x instances
    desired    = ceil(total_load / 0.50)
    new_count  = max(1, min(desired, instances - 1))

Example — CPU 20%, 6 instances (Case 3):
  total_load = (20/100) x 6 = 1.2 load units
  desired    = ceil(1.2 / 0.50) = ceil(2.4) = 3
  new_count  = max(1, min(3, 5)) = 3 instances
  CPU after  = approx 40%  ->  back in stable zone"""))

items.append(blank())
items.append(make_subheading("4.5.5  Cost Model"))
items.append(make_para(
    "The cost model uses AWS EC2 t2.micro on-demand pricing of zero point zero one one six "
    "dollars per instance per hour as the unit rate. Monthly cost is derived by multiplying "
    "the hourly rate by twenty-four hours and thirty days. The savings percentage is computed "
    "by comparing the current auto-scaled monthly cost against the worst-case baseline of always "
    "running the maximum fleet of ten instances. This comparison quantifies the core financial "
    "justification for auto scaling and forms the basis of the Cost Analysis dashboard page."
))
items.append(make_code(
"""Unit rate  = $0.0116 per instance per hour  (AWS t2.micro, US East)
Monthly    = $0.0116 x 24 x 30 = $8.352 per instance per month

current_hourly  = instances x $0.0116
current_monthly = instances x $8.352
fixed_monthly   = 10 x $8.352 = $83.52  (always-on max fleet baseline)

savings (%) = ((83.52 - current_monthly) / 83.52) x 100

Savings by instance count:
  1 instance  ->  $8.35/month   ->  90.0% savings
  2 instances ->  $16.70/month  ->  80.0% savings
  5 instances ->  $41.76/month  ->  50.0% savings
  10 instances -> $83.52/month  ->   0.0% (baseline)"""))

# ══════════════════════════════════════════════
# 4.6 DATABASE DESIGN
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.6  Database Design"))

items.append(make_para(
    "CloudScale uses SQLite as its embedded database for user account persistence. The choice "
    "of SQLite over a client-server database such as PostgreSQL or MySQL was deliberate: the "
    "application has a single table with modest write frequency, deploys on a local machine "
    "without network access, and requires zero configuration. The entire database is stored in "
    "a single file named cloudscale.db in the project root directory. This file is created "
    "automatically the first time the application runs via the init_db() function called at "
    "module import time. No manual database setup, migration scripts, or administrator access "
    "is required."
))
items.append(make_para(
    "The schema consists of a single table named users. The id column is a self-incrementing "
    "integer primary key assigned automatically by SQLite. The full_name column stores the "
    "display name shown in the sidebar. The email column carries a unique constraint with "
    "case-insensitive collation, meaning that the addresses john@example.com and "
    "John@EXAMPLE.COM are treated as identical and cannot both be registered. The password_hash "
    "column stores the PBKDF2 output in the format salt-colon-hash-hex; the original password "
    "is never retained. The avatar_color column holds one of eight preset hexadecimal color "
    "values randomly assigned at signup and used to render the user's initial avatar badge in "
    "the sidebar. The created_at column captures the signup timestamp automatically."
))
items.append(make_para(
    "Write-Ahead Logging mode is enabled on every database connection via the SQLite PRAGMA "
    "command. This journal mode replaces SQLite's default rollback journal and prevents the "
    "database from becoming locked or corrupted when the Streamlit application refreshes while "
    "a write is in progress, which can happen because the dashboard fragment runs every two "
    "seconds in the background. WAL mode also allows multiple concurrent read connections while "
    "a single write is active, eliminating the database-is-locked error that would otherwise "
    "occur when multiple browser tabs load the application simultaneously."
))
items.append(make_code_caption("Database Schema — cloudscale.db"))
items.append(make_code(
"""CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Unique user identifier, auto-increments: 1, 2, 3...

    full_name     TEXT NOT NULL,
    -- Display name shown in the sidebar widget and welcome messages

    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    -- Login identifier. Must be unique. COLLATE NOCASE makes
    -- 'User@Email.COM' equal to 'user@email.com'.
    -- Stored normalised to lowercase via email.lower().strip()

    password_hash TEXT NOT NULL,
    -- Format: '{32-char-salt}:{64-char-SHA256-hex}'
    -- Example: 'a3f8c2d1e9b4f06a:8b3f2a1c9e4f...'
    -- The plain-text password is NEVER stored.

    avatar_color  TEXT DEFAULT '#3b82f6',
    -- One of 8 preset hex colors randomly chosen at signup.
    -- Used as the gradient start color of the avatar badge.

    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- Auto-set to UTC signup time by SQLite.
);

PRAGMA journal_mode = WAL;
-- Applied on every connection via get_db().
-- Prevents 'database is locked' with concurrent Streamlit tabs.
-- Allows simultaneous reads while one write is in progress."""))

# ══════════════════════════════════════════════
# 4.7 SECURITY
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.7  Security Implementation"))

items.append(make_para(
    "CloudScale addresses the most relevant security risks from the OWASP Top Ten for "
    "web-based authentication systems. Each measure is implemented directly in the Python "
    "source code and applies to the production-ready authentication flow rather than being "
    "a theoretical addition."
))
items.append(make_para(
    "Password storage is the most critical security concern. The PBKDF2-HMAC-SHA256 algorithm "
    "with one hundred thousand iterations is applied to every password before it reaches the "
    "database. This iteration count means that a single password attempt requires approximately "
    "one tenth of a second of computation time. An attacker who obtained the database file and "
    "attempted to brute-force all passwords would be limited to roughly ten guesses per second "
    "per processor core, making large-scale offline attacks computationally infeasible within "
    "any practical timeframe. Each user receives a unique one hundred and twenty-eight bit "
    "random salt generated by Python's secrets module, so that even if two users happen to "
    "choose the same password, their stored hashes are completely different. This property "
    "also makes precomputed rainbow table attacks impossible."
))
items.append(make_para(
    "SQL injection is prevented throughout the application by using parameterized queries "
    "exclusively. Every SQL statement in db.py passes user-supplied values as separate "
    "parameters using the question mark placeholder syntax, and SQLite's connection layer "
    "handles escaping automatically. No user input is ever concatenated into a SQL string. "
    "Unauthorized page access is prevented by the require_auth() function at the top of every "
    "Streamlit page, which calls st.stop() before rendering any content if no authenticated "
    "user is found in session state. Username enumeration is blocked by the login function "
    "returning the identical message Invalid email or password regardless of whether the "
    "submitted email address exists in the database. Session data is stored server-side in "
    "Streamlit's session_state dictionary and is never exposed in browser cookies or URL "
    "parameters, preventing session token theft."
))
items.append(make_code_caption("Security Model Summary"))
items.append(make_code(
"""Attack Vector          | Mitigation Applied
-----------------------------------------------------------------
Plaintext passwords    | PBKDF2-SHA256, 100,000 iterations
Rainbow table attacks  | Unique 128-bit random salt per user
Brute-force cracking   | 0.1 sec/hash iteration cost
SQL injection          | Parameterized queries throughout db.py
Username enumeration   | Identical error: "Invalid email or password"
Unauthorized page access | require_auth() + st.stop() on all pages
Session hijacking      | Server-side session_state, no client tokens
Password reuse leakage | Per-user salt means identical passwords
                       | produce completely different stored hashes"""))

# ══════════════════════════════════════════════
# 4.8 DASHBOARD PAGES
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.8  Dashboard Pages"))

items.append(make_para(
    "CloudScale's user interface is organized into ten Streamlit pages automatically discovered "
    "from the pages directory and listed as sidebar navigation items in numeric order. Each "
    "page serves a distinct analytical purpose and is accessible to authenticated users at any "
    "time during a simulation session. All pages call require_auth() as their first statement "
    "to enforce access control."
))

items.append(blank())
items.append(make_subheading("4.8.1  Page 1 — System Overview"))
items.append(make_para(
    "The Overview page provides an executive summary of system health using three Plotly "
    "indicator gauge charts. The CPU gauge uses a blue color scheme with three color zones "
    "that map directly to the autoscaling thresholds: green from zero to thirty percent "
    "representing the scale-in zone, yellow from thirty to seventy percent representing the "
    "stable operating band, and red from seventy to one hundred percent representing the "
    "scale-out zone. The memory gauge applies the same zone pattern in purple. The instance "
    "count gauge shows a delta arrow that indicates whether the fleet grew or shrank compared "
    "to the previous reading, giving the user an at-a-glance indication of scaling activity. "
    "Below the gauges, four key performance indicator boxes display total active users, "
    "cumulative scale-out event count, cumulative scale-in event count, and total requests "
    "served since the session began."
))

items.append(blank())
items.append(make_subheading("4.8.2  Page 2 — System Architecture"))
items.append(make_para(
    "The System Architecture page renders a live interactive flow diagram built entirely "
    "through HTML and CSS injected via Streamlit's markdown function. The diagram shows the "
    "complete data path as a vertical sequence of components: Users at the top, flowing into "
    "the Application Load Balancer, then the Auto Scaling Group policy box, then a dynamic "
    "grid of EC2 instance icons that updates in real time as the instance count changes, then "
    "the CloudWatch monitoring layer, and finally the dashboard. Each component box has a "
    "colored left border that glows with increased brightness when actively processing, "
    "providing an animated visual of data flowing through the system. Scaling policy summary "
    "cards at the bottom clearly display the scale-out threshold, scale-in threshold, and "
    "capacity limits."
))

items.append(blank())
items.append(make_subheading("4.8.3  Page 3 — Load Generator"))
items.append(make_para(
    "The Load Generator is the primary control interface for the simulation. It provides "
    "a continuous slider from zero to one thousand users in steps of fifty. Five preset "
    "buttons labeled one hundred, three hundred, five hundred, seven hundred and fifty, and "
    "one thousand allow instant transition to predefined traffic scenarios without adjusting "
    "the slider manually. Three action buttons — Apply Load, Max Load, and Stop Load — "
    "update the shared SystemState object which takes effect within the next two-second "
    "dashboard refresh cycle. A load level indicator classifies the current setting as No "
    "Load, Low from one to three hundred, Medium from three hundred and one to six hundred, "
    "or High above six hundred, helping users understand the expected system response before "
    "applying the load."
))

items.append(blank())
items.append(make_subheading("4.8.4  Page 4 — Live Metrics"))
items.append(make_para(
    "The Live Metrics page presents a comprehensive two-by-two Plotly subplot grid showing "
    "the rolling hundred-entry history for the four primary metrics. The top-left panel "
    "displays CPU utilization in blue with two dashed reference lines at seventy percent "
    "for scale-out and thirty percent for scale-in threshold. The top-right shows memory "
    "utilization in purple. The bottom-left tracks instance count in green with circular "
    "dot markers at each data point to make individual readings visible. The bottom-right "
    "shows active user count in amber with a semi-transparent filled area beneath the line. "
    "Four delta metric boxes above the grid display each metric's current value alongside "
    "a colored arrow indicating the direction of change from the previous reading. A "
    "statistics table below the charts presents current, average, peak, and minimum values "
    "for CPU and memory over the entire history window."
))

items.append(blank())
items.append(make_subheading("4.8.5  Page 5 — Auto Scaling Activity"))
items.append(make_para(
    "The Auto Scaling Activity page provides a complete chronological audit trail of every "
    "scaling decision made during the session. Each event is displayed as a card with a "
    "green left border for scale-out events and a blue left border for scale-in events. "
    "Every card shows the event timestamp, the instance count transition expressed as a "
    "from-to pair, the CPU percentage that triggered the decision, and the autoscaler's "
    "plain-language reason string generated by the _log_event() function. A raw text log "
    "section below the event timeline shows the same information in a compact monospace "
    "format. A Clear All Logs button resets both the structured event list and the text "
    "log, allowing the user to start fresh and observe a clean scaling cycle."
))

items.append(blank())
items.append(make_subheading("4.8.6  Page 6 — Cost Analysis"))
items.append(make_para(
    "The Cost Analysis page translates the simulation's resource allocation behavior into "
    "financial terms using real AWS pricing. Four metric cards at the top show the current "
    "hourly cost, current monthly cost, the fixed ten-instance monthly baseline cost, and "
    "the savings percentage achieved by the autoscaler. A grouped bar chart compares the "
    "current auto-scaled cost against hypothetical fixed deployments of two, five, and ten "
    "instances, making the cost benefit immediately visible. A donut chart beneath the bar "
    "chart shows the historical distribution of instance counts observed during the session, "
    "revealing how efficiently the fleet has been utilized over time. An AWS pricing "
    "reference table lists t2.micro, t2.small, t2.medium, and t2.large specifications and "
    "costs for educational context. A highlighted insight callout displays the live savings "
    "percentage with a brief explanation of the cost model."
))

items.append(blank())
items.append(make_subheading("4.8.7  Pages 7 Through 10 — Advanced Analytics"))
items.append(make_para(
    "Page 7, the About Project page, serves as an in-application documentation hub. It "
    "explains the project motivation, summarizes the technology stack, describes all AWS "
    "concepts being simulated, and provides a step-by-step presentation guide. Page 8, the "
    "Scaling Decision Engine, shows a large CPU zone gauge with color-coded decision bands, "
    "a prominent box displaying the current scaling decision with its reasoning, and a "
    "capacity planning table mapping user counts to required instance counts. Page 9, the "
    "Instance Lifecycle page, displays a fleet health summary and an annotated timeline "
    "chart marking scale-out and scale-in events with vertical lines. Page 10, the Scaling "
    "Patterns page, provides advanced analytics including an efficiency score card, a zone "
    "distribution pie chart showing how much time the system spent in each CPU band, a "
    "scatter plot correlating user count with instance count, a CPU heatmap, and separate "
    "line charts for scale-out and scale-in rates over time."
))

# ══════════════════════════════════════════════
# 4.9 DATA FLOW
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.9  End-to-End Data Flow"))

items.append(make_para(
    "Understanding the complete data flow through CloudScale reveals how all six backend "
    "modules and the dashboard collaborate to produce a coherent real-time simulation. The "
    "following walkthrough traces a complete load spike scenario — setting the Load Generator "
    "to eight hundred users — from the initial user action through all internal processing "
    "steps to the final rendered output."
))
items.append(make_para(
    "The user navigates to Page 3, moves the slider to eight hundred, and clicks Apply Load. "
    "This writes eight hundred to state.active_users and sets state.load_running to True in "
    "the shared SystemState object. Two seconds later, the @st.fragment decorator fires the "
    "live_dashboard function. The function first calls calculate_cpu(800, 1), which computes "
    "eight hundred divided by one hundred equals eight hundred percent, clamped to one hundred "
    "percent. It then calls apply_autoscaling(state). The autoscaler enters its stabilization "
    "loop and in the first round finds CPU at one hundred percent above the seventy percent "
    "threshold. The target-tracking formula computes total_load as one point zero instance "
    "units, desired as two instances at fifty percent target, and scales to two. In the second "
    "round CPU recalculates to one hundred percent for two instances, desired becomes four. "
    "In the third round CPU is still one hundred for four instances, desired becomes eight. "
    "In the fourth round CPU is one hundred for eight instances, desired becomes sixteen but "
    "is capped at ten. After ten instances, CPU is eighty percent and above the threshold but "
    "the maximum has been reached, so the loop exits. Four scale-out events are logged. The "
    "function then recalculates final CPU as approximately eighty percent and memory as "
    "approximately fifty-five percent for ten instances. It calls tick_fleet() which adds nine "
    "new InstanceInfo objects and updates each with eighty users each. It records a snapshot "
    "to all five history arrays. The dashboard then renders a red status banner reading High "
    "load detected, four metric cards showing eight hundred users, ten instances, eighty "
    "percent CPU, and fifty-five percent memory, a grid of ten instance cards from "
    "instance-alpha through instance-kappa, the updated chart lines, and a timeline of the "
    "four scale-out events."
))
items.append(make_code_caption("End-to-End Data Flow Diagram"))
items.append(make_code(
"""User sets 800 users in Load Generator -> clicks Apply Load
  state.active_users = 800
  state.load_running = True

--- 2 seconds pass --- @st.fragment fires ---

[1] calculate_cpu(800, 1)        ->  100.0%  (clamped)
[2] apply_autoscaling(state)
    Loop Round 1: cpu=100%, instances=1
      total_load = 1.0 x 1 = 1.0
      desired    = ceil(1.0/0.5) = 2
      instances  = max(2,2) = 2    [SCALE OUT: 1->2, logged]
      recalc     ->  cpu = 100%

    Loop Round 2: cpu=100%, instances=2
      total_load = 1.0 x 2 = 2.0
      desired    = ceil(2.0/0.5) = 4
      instances  = max(3,4) = 4    [SCALE OUT: 2->4, logged]
      recalc     ->  cpu = 100%

    Loop Round 3: cpu=100%, instances=4
      desired=8  ->  instances=8   [SCALE OUT: 4->8, logged]
      recalc     ->  cpu = 100%

    Loop Round 4: cpu=100%, instances=8
      desired=16 ->  min(16,10)=10 [SCALE OUT: 8->10, logged]
      recalc     ->  cpu = 80%

    Loop Round 5: cpu=80% > 70%, but instances==10 (MAX) -> no action
    scaled=False -> BREAK (loop exits)

    state.last_scaled_time = now  (cooldown reset)

[3] calculate_cpu(800, 10)       ->  ~80%
    calculate_memory(800, 10)    ->  ~55%

[4] state.tick_fleet()
    sync_fleet(): adds 9 new InstanceInfo objects (beta through kappa)
    users_per_instance = 800 / 10 = 80
    each instance: cpu=~80%, memory=~55%, requests += ~80

[5] state.record_snapshot()
    history_cpu       .append(80)
    history_instances .append(10)
    history_users     .append(800)

[6] UI renders:
    Banner     ->  "High load detected - Auto Scaling OUT in progress"
    Metric cards -> 800 users | 10 instances | 80.0% CPU | 55.2% memory
    Fleet grid  ->  10 instance cards (alpha through kappa)
    Charts      ->  updated with new history points
    Event log   ->  4 scale-out event cards (1->2, 2->4, 4->8, 8->10)"""))

# ══════════════════════════════════════════════
# 4.10 PROJECT STRUCTURE
# ══════════════════════════════════════════════
items.append(blank())
items.append(make_chapter_heading("4.10  Project File Structure and Setup"))

items.append(make_para(
    "CloudScale follows a clean directory structure that separates backend logic from frontend "
    "presentation. The backend directory contains all pure Python modules with no Streamlit "
    "dependencies, making them independently testable and reusable. The pages directory "
    "follows the Streamlit multi-page convention where each numbered Python file is "
    "automatically discovered and listed as a sidebar navigation entry. The cloudscale.db "
    "file is auto-created on first run. The only prerequisites are Python 3.9 or later and "
    "the two packages listed in requirements.txt."
))
items.append(make_code_caption("Project Directory Structure"))
items.append(make_code(
"""autoscaling_project/
|
|-- Home.py                      Entry point, main live dashboard
|   Contains: auth gate, light theme CSS, @st.fragment(run_every=2)
|
|-- requirements.txt             streamlit>=1.30.0  |  plotly>=5.18.0
|-- README.md                    Full technical documentation
|-- cloudscale.db                SQLite database (auto-created on first run)
|
|-- backend/                     Core Python logic (no Streamlit dependencies)
|   |-- __init__.py              Package marker
|   |-- auth.py                  Login/Signup UI + session management
|   |-- db.py                    SQLite CRUD + PBKDF2 password hashing
|   |-- state.py                 SystemState + InstanceInfo classes
|   |-- autoscaler.py            Auto scaling engine
|   `-- metrics.py               CPU and memory calculation formulas
|
`-- pages/                       Streamlit multi-page app (auto-discovered)
    |-- 1_Overview.py            Gauge charts: CPU, Memory, Instances
    |-- 2_System_Architecture.py Interactive component flow diagram
    |-- 3_Load_Generator.py      Slider + presets (0 to 1000 users)
    |-- 4_Live_Metrics.py        2x2 subplot charts + statistics table
    |-- 5_Auto_Scaling_Activity.py  Event timeline + system logs
    |-- 6_Cost_Analysis.py       Cost comparison + savings calculator
    |-- 7_About_Project.py       In-app documentation hub
    |-- 8_Scaling_Decision_Engine.py  CPU zone visualization
    |-- 9_Instance_Lifecycle.py  Fleet health + lifecycle timeline
    `-- 10_Scaling_Patterns.py   Efficiency metrics + heatmap

Installation:
    pip install streamlit plotly

Run:
    streamlit run Home.py
    Opens at http://localhost:8501"""))

# ──────────────────────────────────────────────────────────────────────
# CHAPTER 5: Results — now inserting AFTER Chapter 4 content
# Find the CHAPTER 5 paragraph and add expanded results AFTER it
# ──────────────────────────────────────────────────────────────────────

print("Inserting all content...")

# Insert all Chapter 4 items
cur = anchor
for elem in items:
    cur = insert_after(cur, elem)

print(f"  Chapter 4 content inserted — total items: {len(items)}")

# ─── Step 4: Find the Results section and expand it ───────────────────
print("Expanding Results section...")

# Find anchor: "These metrics help users analyze..."
results_anchor = None
for p in doc.paragraphs:
    if 'These metrics help users analyze how the autoscaling mechanism' in p.text:
        results_anchor = p._p
        break

if results_anchor is None:
    print("  WARNING: Results anchor not found, skipping results expansion")
else:
    results_items = []

    results_items.append(blank())
    results_items.append(make_subheading("5.1  Output Interface Description"))
    results_items.append(make_para(
        "The CloudScale platform presents its simulation output through a multi-page web "
        "application accessible at http://localhost:8501 after launching with the command "
        "streamlit run Home.py. The first screen encountered is the full-page authentication "
        "landing page with the dark glassmorphic design, animated background orbs, and a "
        "two-column layout featuring the product branding on the left and the tabbed login "
        "card on the right. After creating an account and signing in, the user is redirected "
        "to the main CloudScale Dashboard, which forms the live command center of the "
        "simulation. All screenshots for this section will be added to the report to "
        "illustrate the described interface states."
    ))

    results_items.append(blank())
    results_items.append(make_subheading("5.2  Live Dashboard Output"))
    results_items.append(make_para(
        "The main dashboard displays a pulsing green live indicator followed by a color-coded "
        "status banner that communicates the current system condition at a glance. In the stable "
        "state with low or no traffic, the banner appears in green and reads System stable — "
        "All instances healthy. When the Load Generator is set to a high user count and the "
        "autoscaler is adding instances, the banner switches to red and reads High load "
        "detected — Auto Scaling OUT in progress. As the load is removed and the system "
        "consolidates back to fewer instances, the banner switches to blue reading Low load "
        "— Auto Scaling IN to optimize costs."
    ))
    results_items.append(make_para(
        "Below the banner, four metric cards display the four primary system measurements in "
        "large bold numbers: active user count with a load status indicator, active instance "
        "count with the minimum and maximum bounds shown as a subtitle, CPU percentage in a "
        "color that transitions from green below fifty percent to amber between fifty and "
        "seventy percent to red above seventy percent, and memory percentage following the "
        "same color scale with thresholds at sixty and eighty percent. Each card has a subtle "
        "hover animation that raises it slightly and adds a blue border glow, providing visual "
        "feedback. The CPU and memory cards include an inline progress bar below the percentage "
        "value, colored to match the metric's status."
    ))

    results_items.append(blank())
    results_items.append(make_subheading("5.3  Instance Fleet Grid Output"))
    results_items.append(make_para(
        "The Instance Fleet section below the metric cards renders one card per currently "
        "running virtual machine, arranged in rows of five. Each card shows the instance name "
        "such as instance-alpha, its unique identifier in a monospace font such as i-48293, "
        "individual CPU and memory percentages with color-coded values and inline progress "
        "bars, a cumulative request count, and a health badge showing one of five states: "
        "initializing in purple during the four-second boot phase, launching in blue during "
        "the transition, healthy in green when CPU is below seventy-five percent, warning in "
        "yellow between seventy-five and ninety percent, and critical in red above ninety "
        "percent. When the system is at maximum capacity with ten active instances, the grid "
        "shows two complete rows of five cards filling the width of the page."
    ))

    results_items.append(blank())
    results_items.append(make_subheading("5.4  Chart Output"))
    results_items.append(make_para(
        "The dashboard renders two Plotly charts side by side below the fleet grid, both "
        "updating every two seconds with the latest history data. The left chart titled CPU "
        "and Memory Utilization shows two overlapping line series — CPU in blue with a "
        "semi-transparent filled area below the line, and memory in purple — plotted against "
        "a vertical axis from zero to one hundred percent. Two horizontal dashed reference "
        "lines mark the seventy percent scale-out threshold in light red and the thirty "
        "percent scale-in threshold in light blue, with annotation labels on the right axis. "
        "The right chart titled Instances and User Load uses a dual-axis design where the "
        "left axis tracks instance count in green with dot markers and the right axis tracks "
        "user count in amber with a filled area. This dual-axis chart visually demonstrates "
        "the relationship between the applied load and the autoscaler's response."
    ))

    results_items.append(blank())
    results_items.append(make_subheading("5.5  Scaling Event Log Output"))
    results_items.append(make_para(
        "The Recent Scaling Events section at the bottom of the dashboard shows the five most "
        "recent scaling decisions as timeline cards. Scale-out events display a green icon on "
        "the left, and scale-in events display a blue icon. Each card shows the event type, "
        "the from-to instance transition, the timestamp, and the reason string generated by "
        "the autoscaler. For example, a scale-out event might read: Scale Out — 1 to 4 "
        "instances — 14:32:05 — CPU 100.0% greater than 70% — added 3 instances. A scale-in "
        "event might read: Scale In — 8 to 4 instances — 14:35:12 — CPU 12.0% less than 30% "
        "— removed 4 instances. When no scaling events have occurred yet, the section displays "
        "an informational message directing the user to the Load Generator page."
    ))

    results_items.append(blank())
    results_items.append(make_subheading("5.6  Workload Scenario Observations"))
    results_items.append(make_para(
        "At zero user load the system maintains exactly one instance — instance-alpha — in a "
        "healthy state with CPU readings between zero and two percent and memory at the "
        "fifteen percent operating system base. No scaling events occur because the system is "
        "already at the minimum fleet size. The cost display shows eight dollars and thirty-five "
        "cents per month, representing a ninety percent saving over the fixed ten-instance "
        "baseline cost of eighty-three dollars and fifty-two cents."
    ))
    results_items.append(make_para(
        "When the load is set to one hundred users, the initial CPU immediately reads one "
        "hundred percent for a single instance, triggering the autoscaler to scale out to "
        "two instances within the first two-second tick. With two instances running, CPU "
        "stabilizes at approximately fifty percent which falls within the stable zone, and "
        "no further scaling occurs. Both instances display healthy status badges. Memory "
        "readings settle around forty-two percent."
    ))
    results_items.append(make_para(
        "At five hundred users the autoscaler performs multiple scale-out rounds within a "
        "single tick, progressing through one, two, four, and eventually five instances "
        "before CPU stabilizes near one hundred percent at five instances. The system "
        "operates at the boundary of the scale-out threshold, and small jitter in the CPU "
        "readings may cause occasional additional scale-out events that push to six instances "
        "before settling. Monthly cost at five instances is forty-one dollars and seventy-six "
        "cents, representing a fifty percent saving."
    ))
    results_items.append(make_para(
        "At eight hundred users the stabilization loop runs through four rounds in a single "
        "two-second tick, reaching the maximum fleet of ten instances. With ten instances "
        "handling eight hundred users, CPU stabilizes at approximately eighty percent — above "
        "the fifty percent target but below the point of service degradation. The system "
        "cannot scale further because it has reached the configured maximum. All ten instance "
        "cards display in the fleet grid, showing individual CPU readings near eighty percent "
        "with warning or healthy health badges depending on the jitter component in each "
        "reading. The cost at ten instances is the full eighty-three dollars and fifty-two "
        "cents per month with zero savings, the worst-case scenario the autoscaler cannot "
        "improve upon."
    ))
    results_items.append(make_para(
        "When the load is stopped by clicking Stop Load in the Load Generator, state.active_users "
        "drops to zero. On the next two-second tick the autoscaler calculates CPU near zero "
        "percent with zero active users, entering Case 1 of the scale-in logic and immediately "
        "returning the fleet to one instance. The fleet grid transitions from ten cards to a "
        "single instance-alpha card within two seconds. All nine scale-in events appear in the "
        "activity timeline simultaneously. The cost display returns to eight dollars and "
        "thirty-five cents per month. This cycle — from one instance at rest, scaling out to "
        "ten under full load, then scaling back down to one when load is removed — is the "
        "central demonstration of CloudScale's autonomous resource management."
    ))

    results_cur = results_anchor
    for elem in results_items:
        results_cur = insert_after(results_cur, elem)
    print(f"  Results section expanded — {len(results_items)} items inserted")

# ─── Save ─────────────────────────────────────────────────────────────
doc.save('CloudScale_Final_Report.docx')
print(f"SAVED: CloudScale_Final_Report.docx")
print(f"Total paragraphs: {len(doc.paragraphs)}")
