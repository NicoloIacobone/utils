# Benchmarking script for SAM2 with Ground Truth - IoU calculation
# I need: SAM2 segmentation masks per object, per frame - examples/kubric/results/sam2/video_name/sam_masks/frame_nnnn_obj_m_mask.png
# I need: Ground Truth segmentation masks, per frame - examples/kubric/video_name/gt_masks/segmentation_nnnnn.png

import os
import numpy as np
import colorsys
import json
from PIL import Image
from glob import glob
import matplotlib.pyplot as plt

# this function is used in kubric to generate color palettes based on the TOTAL numer of objects in the video (not just visible in the first frame)
def hls_palette(n_colors, first_hue=0.01, lightness=.5, saturation=.7):
  """Get a list of colors where the first is black and the rest are evenly spaced in HSL space."""
  hues = np.linspace(0, 1, int(n_colors) + 1)[:-1]
  hues = (hues + first_hue) % 1
  palette = [(0., 0., 0.)] + [colorsys.hls_to_rgb(h_i, lightness, saturation) for h_i in hues]
  return np.round(np.array(palette) * 255).astype(np.uint8)

def calculate_iou(mask1, mask2):
    """Calcola l'IoU tra due maschere binarie (array numpy True/False)."""
    mask1 = mask1.astype(bool)
    mask2 = mask2.astype(bool)
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    if union == 0:
        return 1.0 if intersection == 0 else 0.0
    return intersection / union

def benchmark_frame(gt_mask_path, sam_masks_dir, color_to_id_map):
    """
    Calcola il mIoU per un singolo frame.
    
    Args:
        gt_mask_path (str): Percorso alla maschera GT RGB.
        sam_masks_dir (str): Percorso alla cartella con le maschere predette da SAM.
        color_to_id_map (dict): Dizionario che mappa tuple di colori a ID interi.
        
    Returns:
        float: Il mIoU per questo frame.
    """
    try:
        # print(f"Processing GT mask: {gt_mask_path}")
        # print(f"Looking for SAM masks in: {sam_masks_dir}")

        # 1. Carica la maschera GT RGB
        gt_rgb_mask = np.array(Image.open(gt_mask_path).convert("RGB"))

        unique_colors = np.unique(gt_rgb_mask.reshape(-1, 3), axis=0)
        # print("Colori unici nella maschera GT:", unique_colors)
        
        # 2. Carica tutte le maschere predette da SAM per questo frame
        sam_mask_files = [f for f in glob(f"{sam_masks_dir}*.png") if os.path.basename(f).startswith(os.path.basename(sam_masks_dir))]
        # print(f"SAM mask files: {sam_mask_files}")
        if not sam_mask_files:
            # Se SAM non ha prodotto maschere, e ci sono oggetti nel GT, l'IoU è 0.
            return 0.0 if color_to_id_map else 1.0
        
    except FileNotFoundError:
        print(f"Warning: File non trovato per {gt_mask_path} o {sam_masks_dir}, skipping frame.")
        return None

    best_ious_for_each_gt_instance = []

    # 3. Itera su ogni oggetto reale (dal GT)
    for color_tuple, gt_id in color_to_id_map.items():
        # print(f"Processing GT object ID: {gt_id}, Color: {color_tuple}")
        # print(f"Color to id map items: {list(color_to_id_map.items())}")
        # 3a. Isola la maschera GT binaria per l'oggetto corrente
        color_array = np.array(color_tuple)
        gt_binary_mask = np.all(gt_rgb_mask == color_array, axis=-1)

        # print(f"GT object ID: {gt_id}, Color: {color_tuple}")
        # print(f"Color array for comparison: {color_array}")

        # Se l'oggetto non è effettivamente presente nel frame, saltalo
        if gt_binary_mask.sum() == 0:
            continue

        # 3b. Confronta direttamente la maschera predetta corrispondente
        pred_mask_path = sam_masks_dir + f"{gt_id}_mask.png"
        if not os.path.exists(pred_mask_path):
            # print(f"Predicted mask not found: {pred_mask_path}")
            best_ious_for_each_gt_instance.append(0.0)
            continue
        pred_mask = np.array(Image.open(pred_mask_path)) > 0

        # # Mostra a schermo la maschera GT binaria per l'oggetto corrente
        # plt.figure(figsize=(8, 4))
        # plt.subplot(1, 2, 1)
        # plt.imshow(gt_binary_mask, cmap='gray')
        # plt.title(f"GT mask for object ID {gt_id}")
        # plt.axis('off')

        # # Mostra a schermo la maschera predetta per l'oggetto corrente
        # plt.subplot(1, 2, 2)
        # plt.imshow(pred_mask, cmap='gray')
        # plt.title(f"Pred mask for object ID {gt_id}")
        # plt.axis('off')

        # plt.show()

        iou = calculate_iou(gt_binary_mask, pred_mask)
        print(f"IoU for GT object ID {gt_id}: {iou}")
        best_ious_for_each_gt_instance.append(iou)

    # 4. Calcola il mIoU per il frame
    if not best_ious_for_each_gt_instance:
        # Nessun oggetto del GT trovato nel frame, quindi non c'è nulla da valutare
        return 1.0 # O None, a seconda di come vuoi gestirlo

    frame_miou = sum(best_ious_for_each_gt_instance) / len(best_ious_for_each_gt_instance)
    print(f"Frame {frame_idx:05d}: mIoU = {frame_miou:.4f}")
    return frame_miou

video_name = "video_01_static_short" # Change it according to the video to process -- TODO iterate over all videos in a folder
# Define paths
sam_masks_dir = f"/scratch2/nico/examples/kubric/results/sam2/{video_name}/sam_masks"
gt_masks_dir = f"/scratch2/nico/examples/kubric/{video_name}/gt_masks"
metadata_path = f"/scratch2/nico/examples/kubric/{video_name}/metadata.json"

# DEBUG FOLDERS
# gt_masks_dir = f"/scratch2/nico/examples/kubric/results/sam2/{video_name}/gt_masks"
# metadata_path = f"/scratch2/nico/examples/kubric/results/sam2/{video_name}/metadata.json"

# Obtain the total number of objects in the video from len(metadata.json["instances"])
with open(metadata_path, "r") as f:
    metadata = json.load(f)
n_objects = len(metadata["instances"])
# print(f"Total number of objects in the video: {n_objects}")

# Obtain the total number of frames in the video from metadata.json["metadata"]["num_frames"]
frames = int(metadata["metadata"]["num_frames"])
# print(f"Total number of frames in the video: {frames}")

# Generate the color palette for that number of objects with hls_palette(n_objects)
palette = hls_palette(n_objects + 1) # +1 for background
# print(f"Generated color palette with {len(palette)} colors (the first is background).")
# print("Colori nella palette:", palette)

# Extract the object IDs tracked by SAM in the first frame
# and create a color_to_id_map for those objects only (will be used to retrieve the GT masks)
sam_object_ids = set()
color_to_id_map = {}
for file_name in os.listdir(sam_masks_dir):
    if file_name.startswith("frame_0000_obj_") and file_name.endswith("_mask.png"):
        obj_id = int(file_name.split("_")[3])
        sam_object_ids.add(obj_id)
        if obj_id < len(palette):
            color_tuple = tuple(palette[obj_id])
            color_to_id_map[color_tuple] = obj_id
# print(f"SAM tracked {len(sam_object_ids)} objects in the first frame.")
# print(f"SAM object IDs: {sam_object_ids}")
# print(f"Color to ID map for SAM-tracked objects: {color_to_id_map}")

# for each frame, load the complete GT mask and extrapolate the masks for the objects tracked by sam
miou_values = []
for frame_idx in range(frames):
    gt_mask_path = os.path.join(gt_masks_dir, f"segmentation_{frame_idx:05d}.png")
    frame_sam_masks_dir = os.path.join(sam_masks_dir, f"frame_{frame_idx:04d}_obj_")
    frame_miou = benchmark_frame(gt_mask_path, frame_sam_masks_dir, color_to_id_map)
    if frame_miou is not None:
        miou_values.append(frame_miou)
    else:
        print(f"Frame {frame_idx:05d}: skipped due to missing data.")

# Calculate overall mIoU
if miou_values:
    overall_miou = sum(miou_values) / len(miou_values)
    print(f"Overall mIoU for video {video_name}: {overall_miou:.4f}")
else:
    print("No valid frames processed, overall mIoU cannot be calculated.")
