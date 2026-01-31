import os
import pandas as pd
import numpy as np

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THROUGHPUT_DIR = os.path.join(BASE_DIR, "data", "throughput")
PKTSTATS_DIR = os.path.join(BASE_DIR, "data", "pkt-stats")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "cleaned")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CONSTANTS
# ============================================================
SYMBOLS_PER_SLOT = 14
SLOT_DURATION_SEC = 500e-6  # 500 microseconds

# ============================================================
# THROUGHPUT PREPROCESSING (FINAL)
# ============================================================
def process_throughput(cell_id):
    file_path = os.path.join(
        THROUGHPUT_DIR, f"throughput-cell-{cell_id}.dat"
    )

    if not os.path.exists(file_path):
        print(f"[SKIP] Throughput file missing for cell {cell_id}")
        return

    df = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=["timestamp", "kbits"],
        engine="python"
    )

    # Sort by time
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Remove extreme glitches (instrumentation artifacts)
    upper = df["kbits"].quantile(0.999)
    df.loc[df["kbits"] > upper, "kbits"] = 0.0

    # Convert kbits → bits per symbol
    df["bits"] = df["kbits"] * 1000.0

    # Aggregate 14 symbols → 1 slot
    df["slot_index"] = df.index // SYMBOLS_PER_SLOT

    slot_df = df.groupby("slot_index").agg(
        timestamp_slot=("timestamp", "first"),
        bits_per_slot=("bits", "sum")
    ).reset_index(drop=True)

    # Convert payload per slot → Gbps
    slot_df["data_rate_gbps"] = (
        slot_df["bits_per_slot"] / SLOT_DURATION_SEC / 1e9
    )

    slot_df[["timestamp_slot", "data_rate_gbps"]].to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"throughput_slot_cell_{cell_id}.csv"
        ),
        index=False
    )

    print(f"[OK] Throughput processed for cell {cell_id}")

# ============================================================
# PACKET STATS PREPROCESSING (UNCHANGED)
# ============================================================
def process_pktstats(cell_id):
    file_path = os.path.join(
        PKTSTATS_DIR, f"pkt-stats-cell-{cell_id}.dat"
    )

    if not os.path.exists(file_path):
        print(f"[SKIP] Packet-stats file missing for cell {cell_id}")
        return

    pkt = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=["timestamp", "tx", "rx", "too_late"],
        engine="python"
    )

    for col in ["tx", "rx", "too_late"]:
        pkt[col] = pd.to_numeric(pkt[col], errors="coerce")

    pkt[["tx", "rx", "too_late"]] = pkt[
        ["tx", "rx", "too_late"]
    ].fillna(0)

    pkt["loss"] = pkt["tx"] - pkt["rx"] + pkt["too_late"]
    pkt["loss_ratio"] = np.where(
        pkt["tx"] > 0,
        pkt["loss"] / pkt["tx"],
        0.0
    )

    pkt_clean = pkt[["timestamp", "loss_ratio"]]
    pkt_clean.columns = ["timestamp_slot", "loss_ratio"]

    pkt_clean.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"pktloss_slot_cell_{cell_id}.csv"
        ),
        index=False
    )

    print(f"[OK] Packet-stats processed for cell {cell_id}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":

    print("\nStarting preprocessing for all cells...\n")

    for cell_id in range(1, 25):
        process_throughput(cell_id)
        process_pktstats(cell_id)

    print("\nPreprocessing complete.")
