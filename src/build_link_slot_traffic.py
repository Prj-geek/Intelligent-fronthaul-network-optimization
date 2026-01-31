import os
import pandas as pd
import numpy as np

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "output", "cleaned")
TOPO_DIR = os.path.join(BASE_DIR, "output", "member3")
OUT_DIR = os.path.join(BASE_DIR, "output", "link_traffic")

os.makedirs(OUT_DIR, exist_ok=True)

# LOAD CELL → LINK MAPPING
mapping_file = os.path.join(TOPO_DIR, "cell_to_link_mapping.csv")

if not os.path.exists(mapping_file):
    raise FileNotFoundError(mapping_file)

mapping_df = pd.read_csv(mapping_file)

# Convert "Cell 3" → 3
mapping_df["cell_id"] = (
    mapping_df["Cell"].str.extract(r"(\d+)").astype(int)
)

# Group cells by link
link_groups = (
    mapping_df.groupby("Link_ID")["cell_id"]
    .apply(list)
    .to_dict()
)

print("\nCell → Link mapping:")
for link, cells in link_groups.items():
    print(f"Link {link}: Cells {cells}")

# AGGREGATE PER-SLOT TRAFFIC (TIME-ALIGNED)
for link_id, cells in link_groups.items():

    print(f"\nProcessing Link {link_id}...")

    merged = None

    for cell_id in cells:
        file_path = os.path.join(
            CLEAN_DIR, f"throughput_slot_cell_{cell_id}.csv"
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        df = pd.read_csv(file_path)

        # Keep only timestamp + rate
        df = df[["timestamp_slot", "data_rate_gbps"]].copy()
        df.rename(
            columns={"data_rate_gbps": f"cell_{cell_id}_gbps"},
            inplace=True
        )

        if merged is None:
            merged = df
        else:
            # Load per-cell traffic
            cell_traces = []

            for cell_id in cells:
                df = pd.read_csv(
                    os.path.join(
                        CLEAN_DIR,
                        f"throughput_slot_cell_{cell_id}.csv"
                    )
                )

                cell_traces.append(df["data_rate_gbps"].values)

            # Trim all cells to same length
            min_len = min(len(x) for x in cell_traces)
            cell_traces = [x[:min_len] for x in cell_traces]

            # Sum slot-wise
            link_traffic = np.sum(cell_traces, axis=0)

            out_df = pd.DataFrame({
                "slot_index": np.arange(min_len),
                "data_rate_gbps": link_traffic
            })

            out_df.to_csv(
                os.path.join(
                    OUT_DIR,
                    f"link_{link_id}_slot_traffic.csv"
                ),
                index=False
            )

        # Fill missing cell values with 0 (no traffic)
        cell_cols = [c for c in merged.columns if c.endswith("_gbps")]
        merged[cell_cols] = merged[cell_cols].fillna(0.0)


    if merged is None or merged.empty:
        print(f"[WARN] No aligned data for Link {link_id}, skipping.")
        continue

    # Sum Gbps across aligned cells
    cell_cols = [c for c in merged.columns if c.endswith("_gbps")]
    merged["data_rate_gbps"] = merged[cell_cols].sum(axis=1)

    # Create slot index AFTER alignment
    merged = merged.reset_index(drop=True)
    merged.insert(0, "slot_index", range(len(merged)))

    # Save output
    out_file = os.path.join(
        OUT_DIR, f"link_{link_id}_slot_traffic.csv"
    )

    merged[["slot_index", "data_rate_gbps"]].to_csv(
        out_file, index=False
    )

    print(f"Saved: {out_file}")

print("\nAggregated per-slot link traffic generation complete.")
