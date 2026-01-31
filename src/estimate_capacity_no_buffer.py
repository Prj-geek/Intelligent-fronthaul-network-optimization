import os
import pandas as pd
import numpy as np

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK_TRAFFIC_DIR = os.path.join(BASE_DIR, "output", "link_traffic")
OUT_DIR = os.path.join(BASE_DIR, "output", "capacity")

os.makedirs(OUT_DIR, exist_ok=True)

# PARAMETERS
LOSS_PERCENTILE = 99  # 1% loss allowed

# PROCESS EACH LINK
results = []

for fname in sorted(os.listdir(LINK_TRAFFIC_DIR)):
    if not fname.endswith("_slot_traffic.csv"):
        continue

    link_id = fname.split("_")[1]  # link_1_slot_traffic.csv → "1"
    file_path = os.path.join(LINK_TRAFFIC_DIR, fname)

    print(f"\nProcessing Link {link_id} (no buffer)...")

    df = pd.read_csv(file_path)

    # Ignore zero-traffic slots (no traffic should not affect loss criteria)
    traffic = df["data_rate_gbps"].values

    WINDOW = 20  # slots (~5 ms)

    # Average traffic should ignore idle slots
    avg_capacity = traffic[traffic > 0].mean() if np.any(traffic > 0) else 0.0

    # Capacity estimation must preserve time continuity
    if np.count_nonzero(traffic) == 0:
        required_capacity = 0.0
    elif len(traffic) < WINDOW:
        required_capacity = traffic.max()
    else:
        windowed_traffic = np.convolve(
            traffic,
            np.ones(WINDOW) / WINDOW,
            mode="valid"
        )
        required_capacity = np.percentile(
            windowed_traffic,
            LOSS_PERCENTILE
        )


    results.append({
        "Link": f"Link {link_id}",
        "Avg_Traffic_Gbps": round(avg_capacity, 3),
        "Required_Capacity_No_Buffer_Gbps": round(required_capacity, 3)
    })

    print(f"Avg traffic: {avg_capacity:.3f} Gbps")
    print(f"Required capacity (99th pct): {required_capacity:.3f} Gbps")

# SAVE SUMMARY
summary_df = pd.DataFrame(results)

out_file = os.path.join(
    OUT_DIR, "required_capacity_no_buffer.csv"
)

summary_df.to_csv(out_file, index=False)

print("\n No-buffer capacity estimation complete.")
print(f"Saved summary: {out_file}")
