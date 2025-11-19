import os
import torch
import cv2
import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler
from PIL import Image
import matplotlib.pyplot as plt

# ===========================================
# CONFIG
# ===========================================
# EMBEDDINGS_PATH = "/scratch2/nico/distillation/hdbscan_test/transformer_features/transformer_features.pt"
# EMBEDDINGS_PATH = "/scratch2/nico/distillation/hdbscan_test/dino_features/dino_features.pt"
EMBEDDINGS_PATH = "/scratch2/nico/distillation/hdbscan_test/concatenated_features/concatenated_embeddings.pt"
# EMBEDDINGS_PATH = "/scratch2/nico/distillation/dataset/coco2017/features/val2017/000000003553.pt"
# ENCODER_FEATURES = "/scratch2/nico/distillation/hdbscan_test/dino_features/dino_features.pt"
# DECODER_FEATURES = "/scratch2/nico/distillation/hdbscan_test/transformer_features/transformer_features.pt"
# EMBEDDINGS_PATH = "/scratch2/nico/distillation/output/distillation_3/visualizations/student/24.pt"   # percorso del file
MIN_SAMPLES = 20                              # parametro HDBSCAN
MIN_CLUSTER_SIZE = 50                         # parametro HDBSCAN
NORMALIZE = True                              # normalizzazione opzionale
PLOT = True                                   # mostrare il risultato
# REFERENCE_IMG_PATH = "/scratch2/nico/distillation/dataset/coco2017/images/val2017/000000003661.jpg"
REFERENCE_IMG_PATH = "/scratch2/nico/distillation/dataset/coco2017/images/val2017/000000003553.jpg"
OUTPUT_PNG_PATH = os.path.dirname(EMBEDDINGS_PATH)
# ===========================================

def load_embeddings(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".npy":
        return np.load(path)
    if ext in [".pt", ".pth"]:
        obj = torch.load(path, map_location="cpu", weights_only=False)
        if isinstance(obj, torch.Tensor):
            return obj.cpu().numpy()
        if isinstance(obj, np.ndarray):
            # Accept raw numpy saved via torch.save
            return obj
        if isinstance(obj, dict):
            for k in ["embeddings", "embedding", "features", "feat", "data"]:
                v = obj.get(k, None)
                if isinstance(v, torch.Tensor):
                    return v.cpu().numpy()
                if isinstance(v, np.ndarray):
                    return v
            for v in obj.values():
                if isinstance(v, torch.Tensor):
                    return v.cpu().numpy()
                if isinstance(v, np.ndarray):
                    return v
            raise ValueError("No array/tensor found in .pt dict")
        raise ValueError(f"Unsupported .pt content type: {type(obj)}")
    raise ValueError(f"Unsupported file extension: {ext}")

def concatenate_embeddings(encoder_path, decoder_path):
    feat1 = torch.load(encoder_path)   # es: [1, 1024, 24, 37]
    feat2 = torch.load(decoder_path)   # es: [1, 768, 24, 37]

    # --------------------------------------------------------
    # 2. FLATTEN 2D → TOKEN FORMAT
    #    [B, C, H, W] → [B, T, C]
    # --------------------------------------------------------

    def flatten_features(f):
        B, C, H, W = f.shape
        tokens = f.flatten(2)          # [B, C, H*W]
        tokens = tokens.permute(0, 2, 1)  # [B, T, C]
        return tokens, H, W

    tokens1, H, W = flatten_features(feat1)
    tokens2, _, _ = flatten_features(feat2)

    # --------------------------------------------------------
    # 3. CONCAT FEATURES
    #    [B, T, C1] + [B, T, C2] → [B, T, C_total]
    # --------------------------------------------------------

    tokens_cat = torch.cat([tokens1, tokens2], dim=-1)

    # --------------------------------------------------------
    # 4. RESTORE SPATIAL MAP
    #    [B, T, C_total] → [B, C_total, H, W]
    # --------------------------------------------------------

    def tokens_to_spatial(tokens, H, W):
        B, T, C = tokens.shape
        assert T == H * W, f"Token count mismatch: T={T}, H*W={H*W}"
        x = tokens.reshape(B, H, W, C)     # [B, H, W, C]
        x = x.permute(0, 3, 1, 2)          # [B, C, H, W]
        return x

    feat2d_cat = tokens_to_spatial(tokens_cat, H, W)

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    print("Encoder shape:", feat1.shape)
    print("Decoder shape:", feat2.shape)
    print("Flattened & concatenated tokens:", tokens_cat.shape)
    print("Reconstructed 2D feature map:", feat2d_cat.shape)

    # Ensure we save a torch.Tensor (not numpy)
    if isinstance(feat2d_cat, np.ndarray):
        feat2d_cat = torch.from_numpy(feat2d_cat)
    save_path = os.path.join(os.path.dirname(encoder_path), "concatenated_embeddings.pt")
    torch.save(feat2d_cat, save_path)
    print(f"Saved concatenated embeddings to {save_path}")

    # Example:
    # Encoder shape: [1, 1024, 24, 37]
    # Decoder shape: [1, 768, 24, 37]
    # Flattened & concatenated tokens: [1, 888, 1792]
    # Reconstructed 2D feature map: [1, 1792, 24, 37]
    raise Exception
    return feat2d_cat  # remove batch dim

def main():
    # concatenate_embeddings(ENCODER_FEATURES, DECODER_FEATURES)
    # ---------------------------------------------------------
    # 1. Load embeddings
    # expected shape: (H, W, D) or (D, H, W) or possibly with a leading batch dim
    # ---------------------------------------------------------
    emb = load_embeddings(EMBEDDINGS_PATH)

    # Accept common shapes and convert to (H, W, D)
    # - (1, D, H, W) or (N, D, H, W) with N==1 → squeeze batch
    # - (D, H, W) → transpose to (H, W, D)
    # - (H, W, D) → keep
    if emb.ndim == 4:
        # Prefer squeezing a singleton batch/channel dimension when present
        if emb.shape[0] == 1:
            print(f"Squeezing batch dimension from shape {emb.shape} → {emb[0].shape}")
            emb = emb[0]
        elif emb.shape[-1] == 1:
            print(f"Squeezing trailing channel dimension from shape {emb.shape} → {emb[...,0].shape}")
            emb = emb[..., 0]
        else:
            raise ValueError(f"Unsupported 4D embeddings shape {emb.shape}: expected (1, D, H, W) or (H, W, D, 1)")

    if emb.ndim != 3:
        raise ValueError(f"Expected embedding map with 3 dims after conversion, got shape {emb.shape}")

    # Ensure shape is (H, W, D). If first dim looks like channels (largest), transpose.
    if emb.shape[0] > emb.shape[1] and emb.shape[0] > emb.shape[2]:
        # Likely (D, H, W)
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
    # 5. Reshape to (H, W) and resize to reference image if needed
    # ---------------------------------------------------------
    # Load reference image to get its shape
    ref_img = Image.open(REFERENCE_IMG_PATH).convert("RGB")
    ref_img_np = np.array(ref_img)
    ref_H, ref_W = ref_img_np.shape[:2]

    # Reshape clusters to match embedding shape
    seg = labels.reshape(H, W)

    # If embedding shape differs from reference image, resize segmentation
    if (H, W) != (ref_H, ref_W):
        print(f"Resizing segmentation from ({H}, {W}) to ({ref_H}, {ref_W})")
        seg_resized = cv2.resize(seg.astype(np.float32), (ref_W, ref_H), interpolation=cv2.INTER_NEAREST)
        seg_resized = seg_resized.astype(int)
    else:
        seg_resized = seg

    # ---------------------------------------------------------
    # 6. Plot segmentation and reference image side by side
    # ---------------------------------------------------------
    if PLOT:
        plt.figure(figsize=(18, 6))
        # Reference image
        plt.subplot(1, 3, 1)
        plt.imshow(ref_img_np)
        plt.title("Reference Image")
        plt.axis("off")

        # Segmentation
        plt.subplot(1, 3, 2)
        plt.imshow(seg_resized, cmap="tab20")
        plt.title("HDBSCAN Segmentation")
        plt.axis("off")

        # Overlay: original + clusters (with alpha)
        plt.subplot(1, 3, 3)
        plt.imshow(ref_img_np)
        plt.imshow(seg_resized, cmap="tab20", alpha=0.5)
        plt.title("Overlay")
        plt.axis("off")

        plt.tight_layout()

        # Save the figure as PNG
        out_path = os.path.join(OUTPUT_PNG_PATH, "hdbscan_segmentation.png")
        plt.savefig(out_path, bbox_inches="tight")
        print(f"Saved segmentation plot to {out_path}")

        plt.show()

if __name__ == "__main__":
    main()