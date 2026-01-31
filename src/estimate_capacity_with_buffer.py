import os
import numpy as np
import pandas as pd

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK_TRAFFIC_DIR = os.path.join(BASE_DIR, "output", "link_traffic")
OUT_DIR = os.path.join(BASE_DIR, "output", "capacity")

os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# CONSTANTS (FROM PROBLEM STATEMENT)
# ============================================================
SLOT_TIME_SEC = 500e-6          # 500 microseconds
BUFFER_TIME_SEC = 143e-6        # 4 symbols = 143 microseconds
LOSS_LIMIT = 0.01               # 1% slots allowed to overflow
MAX_ITER = 30                   # binary search iterations

# ============================================================
# BUFFER SIMULATION FUNCTION
# ============================================================
def loss_ratio_for_capacity(demand_gbps, capacity_gbps):
    """
    Simulate buffer behavior and return slot loss ratio
    """
    capacity_bits = capacity_gbps * 1e9 * SLOT_TIME_SEC
    buffer_bits = capacity_gbps * 1e9 * BUFFER_TIME_SEC

    buffer = 0.0
    loss_slots = 0
    traffic_slots = 0

    for rate in demand_gbps:
        if rate <= 0:
            continue

        traffic_slots += 1
        demand_bits = rate * 1e9 * SLOT_TIME_SEC
        excess = demand_bits - capacity_bits

        if excess > 0:
            buffer += excess
            if buffer > buffer_bits:
                loss_slots += 1
                buffer = buffer_bits
        else:
            buffer = max(0.0, buffer + excess)

    return 0.0 if traffic_slots == 0 else loss_slots / traffic_slots

# ============================================================
# PROCESS EACH LINK
# ============================================================
results = []

for fname in sorted(os.listdir(LINK_TRAFFIC_DIR)):
    if not fname.endswith("_slot_traffic.csv"):
        continue

    link_id = fname.split("_")[1]
    df = pd.read_csv(os.path.join(LINK_TRAFFIC_DIR, fname))

    WINDOW = 20  # same as no-buffer case

    traffic_raw = df["data_rate_gbps"].values

    if len(traffic_raw) >= WINDOW:
        traffic = np.convolve(
            traffic_raw,
            np.ones(WINDOW) / WINDOW,
            mode="valid"
        )
    else:
        traffic = traffic_raw

    # Search bounds
    avg = traffic[traffic > 0].mean() if np.any(traffic > 0) else 0.0
    peak = traffic.max()

    low = avg
    high = peak * 1.2 if peak > 0 else avg

    # Binary search for minimum capacity
    for _ in range(MAX_ITER):
        mid = (low + high) / 2
        loss = loss_ratio_for_capacity(traffic, mid)

        if loss <= LOSS_LIMIT:
            high = mid
        else:
            low = mid

    results.append({
        "Link": f"Link {link_id}",
        "Required_Capacity_With_Buffer_Gbps": round(high, 3)
    })

    print(f"Link {link_id}: {high:.3f} Gbps")

# ============================================================
# SAVE RESULTS
# ============================================================
out_file = os.path.join(
    OUT_DIR, "required_capacity_with_buffer.csv"
)

pd.DataFrame(results).to_csv(out_file, index=False)

print("\nBuffered capacity estimation complete.")
print(f"Saved: {out_file}")
