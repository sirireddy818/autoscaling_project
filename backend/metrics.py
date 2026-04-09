import random

# ──────────────────────────────────────────────
# metrics.py
# Calculates CPU and Memory usage for the system
# based on how many users are active and how many
# instances (servers) are running.
# Called every 2 seconds from Home.py and autoscaler.py
# ──────────────────────────────────────────────

def calculate_cpu(users, instances):
    # If somehow there are 0 instances, CPU is maxed out (system crash scenario)
    if instances == 0:
        return 100.0

    # Each instance can handle 100 users at 100% CPU
    # Formula: (total users / total capacity) * 100
    # Example: 500 users, 5 instances → 500/(5*100)*100 = 100% CPU
    # Example: 500 users, 10 instances → 500/(10*100)*100 = 50% CPU
    base = (users / (instances * 100)) * 100

    # Add small random noise (±2%) to make it look realistic, not perfectly flat
    jitter = random.uniform(-2, 2)

    # Clamp result between 0 and 100 (can't go below 0% or above 100%)
    return min(max(base + jitter, 0), 100.0)


def calculate_memory(users, instances):
    # If somehow there are 0 instances, memory is near full
    if instances == 0:
        return 95.0

    # Memory always starts at 15% (OS and background processes use this)
    # As users increase, memory climbs up to a max of 15+60 = 75%
    # Each instance handles 120 users before memory fills to 75%
    base = 15 + (users / (instances * 120)) * 60

    # Add small random noise (±1.5%) to look realistic
    jitter = random.uniform(-1.5, 1.5)

    # Clamp result between 5% (minimum idle) and 100%
    return min(max(base + jitter, 5), 100.0)
