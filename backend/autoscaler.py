import time
import math
from datetime import datetime
from backend.metrics import calculate_cpu, calculate_memory

# ──────────────────────────────────────────────
# autoscaler.py
# This is the CORE ENGINE of the project.
# It decides when to add or remove servers (instances)
# based on current CPU usage — exactly like AWS Auto Scaling Group (ASG).
# Called every 2 seconds from Home.py dashboard.
# ──────────────────────────────────────────────

# ── Scaling Rules (thresholds) ──
SCALE_OUT_THRESHOLD = 70   # If CPU > 70% → add more servers
SCALE_IN_THRESHOLD  = 30   # If CPU < 30% → remove idle servers
COOLDOWN = 2               # Wait at least 2 seconds between scaling actions (prevents rapid flip-flop)
MAX_INSTANCES = 10         # Never run more than 10 servers
MIN_INSTANCES = 1          # Always keep at least 1 server running


def apply_autoscaling(state):
    """
    Main autoscaling function.
    Runs the full scaling loop — scales up/down AND recalculates metrics
    until the system stabilizes. Simulates what AWS CloudWatch + ASG does continuously.
    """

    now = time.time()

    # ── Cooldown check ──
    # If we scaled very recently, skip this tick entirely
    # Prevents the system from scaling up and down too rapidly
    if now - state.last_scaled_time < COOLDOWN:
        return

    # ── Stabilization loop ──
    # Run up to 10 rounds per tick.
    # After adding servers, CPU drops — maybe enough to trigger scale-in.
    # We keep adjusting until the system is stable (no more changes needed).
    for _ in range(10):

        # Recalculate CPU and memory with current instance count before deciding
        state.cpu_usage = calculate_cpu(state.active_users, state.instances)
        state.memory_usage = calculate_memory(state.active_users, state.instances)

        scaled = False  # Track if any scaling happened this round

        # ── SCALE OUT: CPU too high → add servers ──
        if state.cpu_usage > SCALE_OUT_THRESHOLD and state.instances < MAX_INSTANCES:
            old = state.instances

            # Calculate exactly how many instances we need to bring CPU down to ~50%
            # total_load = how much total work is being done right now
            total_load = (state.cpu_usage / 100) * state.instances
            # desired = how many instances needed so each runs at 50% CPU
            desired = math.ceil(total_load / 0.5)
            # At minimum add 1 instance, but use the math if it says add more
            new_count = max(old + 1, desired)
            # Never exceed the max limit
            new_count = min(new_count, MAX_INSTANCES)

            state.instances = new_count
            state.total_scale_outs += 1  # Increment scale-out counter

            # Log the event so it appears in Scaling Activity page
            _log_event(state, "SCALE OUT", "up", old, state.instances,
                       f"CPU {state.cpu_usage:.1f}% > {SCALE_OUT_THRESHOLD}% → added {state.instances - old} instance(s)")
            scaled = True

        # ── SCALE IN: CPU too low → remove idle servers ──
        elif state.cpu_usage < SCALE_IN_THRESHOLD and state.instances > MIN_INSTANCES:
            old = state.instances

            if state.cpu_usage < 5 and state.active_users == 0:
                # Zero users and nearly 0 CPU → drop straight to minimum (1 instance)
                new_count = MIN_INSTANCES
            elif state.cpu_usage < 15:
                # Very low CPU → cut instances in half
                new_count = max(MIN_INSTANCES, old // 2)
            else:
                # Moderate low CPU → calculate the right number mathematically
                total_load = (state.cpu_usage / 100) * state.instances
                desired = math.ceil(total_load / 0.5)
                new_count = max(MIN_INSTANCES, min(desired, old - 1))  # Remove at least 1

            if new_count < old:
                state.instances = new_count
                state.total_scale_ins += 1  # Increment scale-in counter
                removed = old - new_count

                # Log the event so it appears in Scaling Activity page
                _log_event(state, "SCALE IN", "down", old, state.instances,
                           f"CPU {state.cpu_usage:.1f}% < {SCALE_IN_THRESHOLD}% → removed {removed} instance(s)")
                scaled = True

        # If nothing changed this round, system is stable — stop the loop early
        if not scaled:
            break

        # Recalculate after scaling to see the new CPU with updated instance count
        state.cpu_usage = calculate_cpu(state.active_users, state.instances)
        state.memory_usage = calculate_memory(state.active_users, state.instances)

    # Record the time of this scaling tick (used for cooldown check next time)
    state.last_scaled_time = now


def _log_event(state, event_type, direction, old_count, new_count, reason):
    """
    Records a scaling event into state.
    This data is shown in the Scaling Activity page (page 5).
    direction: "up" = scale out, "down" = scale in
    """
    event = {
        "time": datetime.now().strftime("%H:%M:%S"),  # Current time as string e.g. "14:32:05"
        "type": event_type,       # "SCALE OUT" or "SCALE IN"
        "direction": direction,   # "up" or "down"
        "from": old_count,        # How many instances before
        "to": new_count,          # How many instances after
        "cpu": round(state.cpu_usage, 1),  # CPU % at time of event
        "reason": reason,         # Human-readable explanation
    }
    # Add to the events list (shown as timeline cards in page 5)
    state.scaling_events.append(event)
    # Add to the text logs list (shown as monospace logs in page 5)
    state.logs.append(f"[{event_type}] {old_count} → {new_count} instances (CPU: {state.cpu_usage:.1f}%)")
