import time
import random
import streamlit as st

# ──────────────────────────────────────────────
# state.py
# Manages the entire system's live data.
# Think of this as the "memory" of the simulation.
# Every page reads from this to show current values.
# Two classes here:
#   InstanceInfo  → represents one individual server
#   SystemState   → represents the entire system (all servers + metrics)
# ──────────────────────────────────────────────

# Names given to each instance — like AWS instance naming
INSTANCE_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon",
    "zeta", "eta", "theta", "iota", "kappa"
]


class InstanceInfo:
    """Represents one individual EC2-like server instance."""

    def __init__(self, index):
        # Generate a fake AWS-style instance ID like "i-47382"
        self.id = f"i-{random.randint(10000,99999)}"
        # Name like "instance-alpha", "instance-beta", etc.
        self.name = f"instance-{INSTANCE_NAMES[index]}"

        self.cpu = 0.0       # This instance's current CPU usage %
        self.memory = 0.0    # This instance's current memory usage %
        self.requests = 0    # Total requests this instance has handled

        # Status lifecycle: launching → running (→ terminating when removed)
        self.status = "launching"
        self.health = "initializing"   # Health badge: healthy / warning / critical

        self.launched_at = time.time()  # Timestamp when this instance was created
        self._boot_ticks = 2            # Takes 2 ticks (4 seconds) before it's ready

    def tick(self, users_per_instance):
        """
        Called every 2 seconds to update this instance's metrics.
        users_per_instance = total users divided equally across all running instances.
        """

        # ── Boot phase: instance is still starting up ──
        if self._boot_ticks > 0:
            self._boot_ticks -= 1          # Count down the boot timer
            self.status = "launching"
            self.health = "initializing"
            # Show low CPU while booting (just OS startup activity)
            self.cpu = random.uniform(5, 15)
            self.memory = random.uniform(10, 20)
            return  # Don't process real load yet

        # ── Running phase: instance is fully up and serving users ──
        self.status = "running"

        if users_per_instance > 0:
            # Calculate CPU based on this instance's share of users
            # Each 100 users = 100% CPU on one instance
            self.cpu = min(100, (users_per_instance / 100) * 100 + random.uniform(-5, 5))
            # Memory: 15% base + scales with users (random ±3% noise)
            self.memory = min(100, 15 + (users_per_instance / 120) * 60 + random.uniform(-3, 3))
            # Count requests handled (random variation of ±20%)
            self.requests += int(users_per_instance * random.uniform(0.8, 1.2))
        else:
            # No users → instance is idle, just baseline OS activity
            self.cpu = max(0, random.uniform(1, 8))
            self.memory = max(5, random.uniform(8, 18))

        # Round to 1 decimal place for clean display
        self.cpu = round(max(0, self.cpu), 1)
        self.memory = round(max(0, self.memory), 1)

        # ── Set health badge based on CPU level ──
        if self.cpu > 90:
            self.health = "critical"    # Red badge — dangerously overloaded
        elif self.cpu > 75:
            self.health = "warning"     # Yellow badge — getting high
        else:
            self.health = "healthy"     # Green badge — normal operation


class SystemState:
    """
    Holds ALL live data for the simulation.
    Stored in st.session_state so it persists across page navigations.
    Every page accesses this via get_state().
    """

    def __init__(self):
        self.active_users = 0        # Number of simulated users hitting the site
        self.instances = 1           # Number of servers currently running
        self.cpu_usage = 0.0         # Overall system CPU % (averaged across instances)
        self.memory_usage = 0.0      # Overall system Memory %
        self.load_running = False    # Is the load generator currently active?

        # Start with one instance (instance-alpha)
        self.instance_fleet = [InstanceInfo(0)]

        # ── History arrays for charts (last 100 readings) ──
        # Each entry = one snapshot taken every 2 seconds
        self.history_cpu = []
        self.history_memory = []
        self.history_instances = []
        self.history_users = []
        self.history_timestamps = []

        self.logs = []              # Text logs shown in Scaling Activity page
        self.scaling_events = []    # Structured event objects shown as timeline cards
        self.last_scaled_time = time.time()  # Used by autoscaler cooldown check

        # Counters shown in Overview and Scaling Activity pages
        self.total_requests = 0
        self.total_scale_outs = 0
        self.total_scale_ins = 0

    def sync_fleet(self):
        """
        Keeps instance_fleet list in sync with self.instances count.
        If we scaled out → add new InstanceInfo objects.
        If we scaled in → remove excess InstanceInfo objects.
        """
        target = self.instances

        # Add new instance objects until fleet matches target count
        while len(self.instance_fleet) < target:
            idx = len(self.instance_fleet)
            self.instance_fleet.append(InstanceInfo(idx % len(INSTANCE_NAMES)))

        # Remove excess instance objects from the end
        while len(self.instance_fleet) > target:
            self.instance_fleet.pop()

    def tick_fleet(self):
        """
        Updates all individual instance metrics for one tick.
        Called every 2 seconds from Home.py.
        """
        # First make sure fleet list matches the current instance count
        self.sync_fleet()

        # Divide users equally across all running instances
        running_count = len(self.instance_fleet)
        users_per_instance = self.active_users / running_count if running_count > 0 else 0

        # Update each instance individually
        for inst in self.instance_fleet:
            inst.tick(users_per_instance)

    def get_fleet_summary(self):
        """
        Returns a list of dicts (one per instance) for display in the dashboard.
        Used by Home.py to render the Instance Fleet section.
        """
        return [
            {
                "id": inst.id,
                "name": inst.name,
                "cpu": inst.cpu,
                "memory": inst.memory,
                "requests": inst.requests,
                "status": inst.status,
                "health": inst.health,
            }
            for inst in self.instance_fleet
        ]

    def record_snapshot(self):
        """
        Takes a snapshot of current metrics and adds to history arrays.
        Called every 2 seconds. History is used to draw the line charts.
        Keeps only the last 100 snapshots (~3.3 minutes of data).
        """
        self.history_cpu.append(round(self.cpu_usage, 1))
        self.history_memory.append(round(self.memory_usage, 1))
        self.history_instances.append(self.instances)
        self.history_users.append(self.active_users)
        self.history_timestamps.append(time.time())

        # Trim to last 100 entries to prevent memory growing indefinitely
        if len(self.history_cpu) > 100:
            self.history_cpu = self.history_cpu[-100:]
            self.history_memory = self.history_memory[-100:]
            self.history_instances = self.history_instances[-100:]
            self.history_users = self.history_users[-100:]
            self.history_timestamps = self.history_timestamps[-100:]


def get_state():
    """
    Returns the single shared SystemState object for this browser session.
    If it doesn't exist yet (first load), creates a new one.
    Streamlit's session_state keeps it alive as the user navigates between pages.
    """
    if "system_state" not in st.session_state:
        st.session_state["system_state"] = SystemState()
    return st.session_state["system_state"]
