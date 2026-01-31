import os
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK_TRAFFIC_DIR = os.path.join(BASE_DIR, "output", "link_traffic")
CAPACITY_DIR = os.path.join(BASE_DIR, "output", "capacity")
OUT_DIR = os.path.join(BASE_DIR, "output", "figures")

os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================
SLOT_TIME_SEC = 500e-6        # 500 microseconds
PLOT_DURATION_SEC = 60        # seconds
MAX_SLOTS = int(PLOT_DURATION_SEC / SLOT_TIME_SEC)

PLOT_STRIDE = 20              # plot every 20th slot (~10 ms)

# ============================================================
# LOAD CAPACITY TABLES
# ============================================================
cap_no_buf = pd.read_csv(
    os.path.join(CAPACITY_DIR, "required_capacity_no_buffer.csv")
).set_index("Link")

cap_buf = pd.read_csv(
    os.path.join(CAPACITY_DIR, "required_capacity_with_buffer.csv")
).set_index("Link")

# ============================================================
# COLOR CONFIGURATION (SPIKE-FRIENDLY)
# ============================================================
FILL_COLOR = "#c77dff"   # light lavender
EDGE_COLOR = "#5a189a"   # dark purple
AVG_COLOR  = "#2e7d32"   # green
CAP_COLOR  = "#d32f2f"   # red
GRID_COLOR = "#bdbdbd"   # light gray

# ============================================================
# PLOT EACH LINK (FIGURE-3 STYLE)
# ============================================================
for fname in sorted(os.listdir(LINK_TRAFFIC_DIR)):
    if not fname.endswith("_slot_traffic.csv"):
        continue

    link_id = fname.split("_")[1]
    link_name = f"Link {link_id}"

    df = pd.read_csv(os.path.join(LINK_TRAFFIC_DIR, fname))

    # Limit to first 60 seconds
    df = df.iloc[:MAX_SLOTS]

    # Downsample for readability
    df_plot = df.iloc[::PLOT_STRIDE].copy()

    # Correct time axis
    time_sec = df_plot["slot_index"].values * SLOT_TIME_SEC
    traffic = df_plot["data_rate_gbps"].values

    # Statistics
    avg = traffic[traffic > 0].mean() if (traffic > 0).any() else 0.0
    cap_b = cap_buf.loc[link_name, "Required_Capacity_With_Buffer_Gbps"]

    # ========================================================
    # PLOTTING
    # ========================================================
    plt.figure(figsize=(14, 5))

    # Aggregated traffic (light fill + dark outline)
    plt.fill_between(
        time_sec,
        traffic,
        color=FILL_COLOR,
        edgecolor=EDGE_COLOR,
        linewidth=0.4,
        alpha=0.85
    )

    # Optional thin line to sharpen spikes
    plt.plot(
        time_sec,
        traffic,
        color=EDGE_COLOR,
        linewidth=0.5
    )

    # Average data rate
    plt.axhline(
        avg,
        color=AVG_COLOR,
        linestyle="--",
        linewidth=2,
        label="Average data rate"
    )

    # Required FH link capacity
    plt.axhline(
        cap_b,
        color=CAP_COLOR,
        linestyle="--",
        linewidth=2,
        label="Required FH link capacity"
    )

    # Axes and styling
    plt.xlabel("Time [s]")
    plt.ylabel("Data rate [Gbps]")
    plt.title(f"Per-Slot Aggregated Traffic — {link_name}")

    plt.xlim(0, PLOT_DURATION_SEC)
    plt.ylim(0, max(traffic.max(), cap_b) * 1.15)

    plt.grid(True, color=GRID_COLOR, alpha=0.4)
    plt.legend(loc="upper right")

    # Save figure
    out_file = os.path.join(
        OUT_DIR,
        f"figure3_{link_name.replace(' ', '_')}.png"
    )

    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    plt.close()

    print(f"Saved: {out_file}")

print("\nFigure-3 style plots generated successfully.")
