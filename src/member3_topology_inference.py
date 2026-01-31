import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform

# PATHS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_DIR = os.path.join(BASE_DIR, "output", "member2")
OUT_DIR = os.path.join(BASE_DIR, "output", "member3")

os.makedirs(OUT_DIR, exist_ok=True)

# STEP 1: LOAD SIGNAL MATRIX
print("Loading signal matrix...")

signal_matrix = np.load(os.path.join(IN_DIR, "signal_matrix.npy"))
num_cells = signal_matrix.shape[0]

cell_labels = [f"Cell {i+1}" for i in range(num_cells)]

print(f"Loaded matrix shape: {signal_matrix.shape}")

# STEP 2: COMPUTE CORRELATION MATRIX
print("Computing correlation matrix...")

correlation_matrix = np.corrcoef(signal_matrix)

corr_df = pd.DataFrame(
    correlation_matrix,
    index=cell_labels,
    columns=cell_labels
)

# Save correlation matrix
corr_df.to_csv(os.path.join(OUT_DIR, "correlation_matrix.csv"))

# STEP 3: VISUALIZE CORRELATION HEATMAP
print("Creating correlation heatmap...")

plt.figure(figsize=(12, 10))
sns.heatmap(
    corr_df,
    cmap="coolwarm",
    center=0,
    square=True,
    cbar_kws={"label": "Correlation"}
)
plt.title("Cell-to-Cell Correlation Heatmap")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "correlation_heatmap.png"))
plt.close()

# STEP 4: HIERARCHICAL CLUSTERING
print("Clustering cells into fronthaul links...")

# Convert correlation → distance
distance_matrix = 1 - correlation_matrix

# Condensed distance for linkage
condensed_dist = squareform(distance_matrix, checks=False)

# Hierarchical clustering
Z = linkage(condensed_dist, method="average")

# Number of links
NUM_LINKS = 3

cluster_labels = fcluster(Z, NUM_LINKS, criterion="maxclust")

# STEP 5: SAVE CLUSTER ASSIGNMENTS
cluster_df = pd.DataFrame({
    "Cell": cell_labels,
    "Link_ID": cluster_labels
})

cluster_df.to_csv(
    os.path.join(OUT_DIR, "cell_to_link_mapping.csv"),
    index=False
)

# STEP 6: CREATE GROUP-WISE LINK TABLE
print("\nGroup-wise Fronthaul Topology:")

grouped_links = {}

for _, row in cluster_df.iterrows():
    link_id = row["Link_ID"]
    cell = row["Cell"]

    if link_id not in grouped_links:
        grouped_links[link_id] = []

    grouped_links[link_id].append(cell)

# Print nicely
for link_id in sorted(grouped_links.keys()):
    cells = ", ".join(grouped_links[link_id])
    print(f"Link {link_id}: {cells}")

# Save group-wise table
groupwise_df = pd.DataFrame([
    {"Link_ID": f"Link {link_id}", "Cells": ", ".join(cells)}
    for link_id, cells in grouped_links.items()
])

groupwise_df.to_csv(
    os.path.join(OUT_DIR, "link_groupwise_table.csv"),
    index=False
)


print("\nInferred Fronthaul Topology:")
print(cluster_df.sort_values("Link_ID"))

# DONE
print("\n Member-3 topology inference complete.")
print("Outputs saved to: output/member3/")
