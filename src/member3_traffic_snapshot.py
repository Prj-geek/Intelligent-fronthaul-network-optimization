import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
OUT_DIR = os.path.join(BASE_DIR, "output", "member3")

os.makedirs(OUT_DIR, exist_ok=True)

# CONFIGURATION (ADJUST IF NEEDED)
CELLS_TO_PLOT = [2, 3, 10]   # cells inferred to share same link
START_SLOT = 1000            # starting slot index
NUM_SLOTS = 300              # number of slots to visualize

LOSS_THRESHOLD = 0.01        # 1% loss allowed (per problem statement)

# State encoding
NO_TRAFFIC = 0
TRAFFIC_NO_LOSS = 1
TRAFFIC_WITH_LOSS = 2

# BUILD TRAFFIC STATE MATRIX
state_matrix = []

print("Generating traffic snapshot...")

for cell_id in CELLS_TO_PLOT:
    pkt_file = os.path.join(
        CLEAN_DIR, f"pktloss_slot_cell_{cell_id}.csv"
    )
    thr_file = os.path.join(
        CLEAN_DIR, f"throughput_slot_cell_{cell_id}.csv"
    )

    if not os.path.exists(pkt_file) or not os.path.exists(thr_file):
        raise FileNotFoundError(f"Missing data for Cell {cell_id}")

    pkt_df = pd.read_csv(pkt_file)
    thr_df = pd.read_csv(thr_file)

    # Slice time window
    pkt_window = pkt_df.iloc[START_SLOT:START_SLOT + NUM_SLOTS]
    thr_window = thr_df.iloc[START_SLOT:START_SLOT + NUM_SLOTS]

    cell_states = []

    for loss, rate in zip(
        pkt_window["loss_ratio"],
        thr_window["data_rate_gbps"]
    ):
        if rate <= 0:
            cell_states.append(NO_TRAFFIC)
        elif loss <= LOSS_THRESHOLD:
            cell_states.append(TRAFFIC_NO_LOSS)
        else:
            cell_states.append(TRAFFIC_WITH_LOSS)

    state_matrix.append(cell_states)

state_matrix = np.array(state_matrix)

# PLOT FIGURE-1 STYLE SNAPSHOT
cmap = ListedColormap([
    "white",       # no traffic
    "lightgreen",  # traffic without loss
    "red"          # traffic with loss
])

plt.figure(figsize=(14, 3 + len(CELLS_TO_PLOT)))
plt.imshow(state_matrix, aspect="auto", cmap=cmap)

plt.yticks(
    ticks=range(len(CELLS_TO_PLOT)),
    labels=[f"Cell {c}" for c in CELLS_TO_PLOT]
)

plt.xlabel("Time (slots)")
plt.ylabel("Cells")
plt.title("Traffic Pattern Snapshot for Cells Sharing Same Fronthaul Link")

cbar = plt.colorbar(
    ticks=[0, 1, 2]
)
cbar.ax.set_yticklabels([
    "No traffic",
    "Traffic without loss",
    "Traffic with loss"
])
cbar.set_label("Traffic State")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "traffic_snapshot.png"))
plt.close()

print(" Corrected traffic snapshot generated:")
print("output/member3/traffic_snapshot.png")
