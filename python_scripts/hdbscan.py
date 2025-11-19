import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ===========================================
# CONFIG
# ===========================================
EMBEDDINGS_PATH = "student_embeddings.npy"   # percorso del file
MIN_SAMPLES = 20                              # parametro HDBSCAN
MIN_CLUSTER_SIZE = 50                         # parametro HDBSCAN
NORMALIZE = True                              # normalizzazione opzionale
PLOT = True                                   # mostrare il risultato
# ===========================================


def main():

    # ---------------------------------------------------------
    # 1. Load embeddings
    # expected shape: (H, W, D) or (D, H, W)
    # ---------------------------------------------------------
    emb = np.load(EMBEDDINGS_PATH)

    if emb.ndim != 3:
        raise ValueError(f"Expected embedding map with 3 dims, got shape {emb.shape}")

    # make sure shape is (H, W, D)
    if emb.shape[0] < emb.shape[-1] and emb.shape[0] == emb.shape[-1]:
        # ambiguous case, ignore
        pass

    # if shape is (D, H, W) → transpose
    if emb.shape[0] < 32:  # heuristica: D tipicamente è 64-256, H e W molto più grandi
        print("Transposing embeddings from (D, H, W) to (H, W, D)")
        emb = emb.transpose(1, 2, 0)

    H, W, D = emb.shape
    print(f"Loaded embeddings: {emb.shape}")

    # ---------------------------------------------------------
    # 2. Flatten pixel embeddings → (H*W, D)
    # ---------------------------------------------------------
    flat = emb.reshape(-1, D)

    # ---------------------------------------------------------
    # 3. Optional: normalize embedding dims
    # ---------------------------------------------------------
    if NORMALIZE:
        print("Normalizing embeddings...")
        flat = StandardScaler().fit_transform(flat)

    # ---------------------------------------------------------
    # 4. HDBSCAN clustering
    # ---------------------------------------------------------
    print("Running HDBSCAN clustering...")
    clusterer = hdbscan.HDBSCAN(
        min_samples=MIN_SAMPLES,
        min_cluster_size=MIN_CLUSTER_SIZE,
        cluster_selection_method="leaf"
    ).fit(flat)

    labels = clusterer.labels_
    print(f"Clusters found: {len(np.unique(labels))} (label -1 = noise)")

    # ---------------------------------------------------------
    # 5. Reshape to (H, W)
    # ---------------------------------------------------------
    seg = labels.reshape(H, W)

    # ---------------------------------------------------------
    # 6. Plot segmentation
    # ---------------------------------------------------------
    if PLOT:
        plt.figure(figsize=(6,6))
        plt.imshow(seg, cmap="tab20")
        plt.title("HDBSCAN Segmentation")
        plt.axis("off")
        plt.show()

    # ---------------------------------------------------------
    # 7. Save segmentation mask
    # ---------------------------------------------------------
    np.save("segmentation_hdbscan.npy", seg)
    print("Saved segmentation_hdbscan.npy")


if __name__ == "__main__":
    main()