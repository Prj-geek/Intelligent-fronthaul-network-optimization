import os
import numpy as np
import pandas as pd

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
OUT_DIR = os.path.join(BASE_DIR, "output", "member2")

os.makedirs(OUT_DIR, exist_ok=True)

# PARAMETERS
NUM_CELLS = 24
WINDOW_SIZE = 50   # number of slots per window

# STEP 1: LOAD PACKET LOSS SIGNALS
signals = {}

print("Loading packet loss signals...")

for cell_id in range(1, NUM_CELLS + 1):
    file_path = os.path.join(
        CLEAN_DIR, f"pktloss_slot_cell_{cell_id}.csv"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing file: {file_path}")

    df = pd.read_csv(file_path)

    # IMPORTANT: ignore timestamp, use only loss_ratio
    loss_signal = df["loss_ratio"].values

    signals[cell_id] = loss_signal

    print(f"Cell {cell_id}: {len(loss_signal)} samples")

# STEP 2: TRIM ALL SIGNALS TO SAME LENGTH
print("\nEqualizing signal lengths...")

min_length = min(len(sig) for sig in signals.values())
print(f"Minimum length across cells: {min_length}")

for cell_id in signals:
    signals[cell_id] = signals[cell_id][:min_length]

# STEP 3: WINDOWING (MEAN LOSS PER WINDOW)
print("\nApplying windowing...")

windowed_signals = {}

num_windows = min_length // WINDOW_SIZE
print(f"Total windows per cell: {num_windows}")

for cell_id, sig in signals.items():
    windowed = []

    for i in range(num_windows):
        start = i * WINDOW_SIZE
        end = start + WINDOW_SIZE
        window_mean = np.mean(sig[start:end])
        windowed.append(window_mean)

    windowed_signals[cell_id] = np.array(windowed)

# STEP 4: NORMALIZATION (Z-SCORE)
print("\nNormalizing signals...")

normalized_signals = {}

for cell_id, sig in windowed_signals.items():
    mean = np.mean(sig)
    std = np.std(sig)

    if std == 0:
        norm_sig = np.zeros_like(sig)
    else:
        norm_sig = (sig - mean) / std

    normalized_signals[cell_id] = norm_sig

# STEP 5: BUILD FINAL SIGNAL MATRIX
print("\nBuilding signal matrix...")

cell_ids = sorted(normalized_signals.keys())

signal_matrix = np.vstack(
    [normalized_signals[cell_id] for cell_id in cell_ids]
)

print(f"Final matrix shape: {signal_matrix.shape}")
print("Rows = cells, Columns = time windows")

# STEP 6: SAVE OUTPUT FOR MEMBER-3
np.save(os.path.join(OUT_DIR, "signal_matrix.npy"), signal_matrix)

pd.DataFrame(
    signal_matrix,
    index=[f"cell_{cid}" for cid in cell_ids]
).to_csv(os.path.join(OUT_DIR, "signal_matrix.csv"))

print("\n Member-2 preprocessing complete.")
print("Saved:")
print(" - output/member2/signal_matrix.npy")
print(" - output/member2/signal_matrix.csv")
