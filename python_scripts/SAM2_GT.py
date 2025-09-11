# Benchmarking script for SAM2 with Ground Truth - IoU calculation
# I need: SAM2 segmentation masks per object, per frame - examples/kubric/results/sam2/video_name/sam_masks/frame_nnnn_obj_m_mask.png
# I need: Ground Truth segmentation masks, per frame - examples/kubric/video_name/gt_masks/segmentation_nnnnn.png

import os
import numpy as np
import colorsys
import json
from PIL import Image
from glob import glob
import csv
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

def benchmark_frame(gt_mask_path, sam_masks_dir, color_to_id_map, video_name, frame_idx):
    """
    Calculates the mIoU for a single frame and saves the IoU for each object in the CSV.

    Args:
        gt_mask_path (str): Path to the GT RGB mask.
        sam_masks_dir (str): Path to the folder with masks predicted by SAM.
        color_to_id_map (dict): Dictionary mapping color tuples to integer IDs.
        video_name (str): Name of the video.
        frame_idx (int): Frame index.

    Returns:
        float: The mIoU for this frame.
    """
    try:
        # Load the ground truth RGB mask as a numpy array
        gt_rgb_mask = np.array(Image.open(gt_mask_path).convert("RGB"))
        # Find all unique colors in the GT mask (each color corresponds to an object)
        unique_colors = np.unique(gt_rgb_mask.reshape(-1, 3), axis=0)
        # Find all SAM mask files for this frame
        sam_mask_files = [f for f in glob(f"{sam_masks_dir}*.png") if os.path.basename(f).startswith(os.path.basename(sam_masks_dir))]
        if not sam_mask_files:
            # If SAM did not produce any masks and there are objects in GT, IoU is 0 for all
            for color_tuple, gt_id in color_to_id_map.items():
                csv_writer.writerow([video_name, frame_idx, gt_id, 0.0])
            return 0.0 if color_to_id_map else 1.0
    except FileNotFoundError:
        # If the GT mask or SAM mask directory is missing, skip this frame
        print(f"Warning: File not found for {gt_mask_path} or {sam_masks_dir}, skipping frame.")
        return None

    best_ious_for_each_gt_instance = []

    # For each object tracked by SAM (using color_to_id_map)
    for color_tuple, gt_id in color_to_id_map.items():
        color_array = np.array(color_tuple)
        # Create a binary mask for the current object in the GT mask
        gt_binary_mask = np.all(gt_rgb_mask == color_array, axis=-1)
        if gt_binary_mask.sum() == 0:
            # If the object is not present in the GT mask for this frame, skip it
            continue
        # Build the path to the predicted mask for this object
        pred_mask_path = sam_masks_dir + f"{gt_id}_mask.png"
        if not os.path.exists(pred_mask_path):
            # If the predicted mask is missing, IoU is 0
            print(f"Predicted mask not found: {pred_mask_path}")
            iou = 0.0
            best_ious_for_each_gt_instance.append(iou)
            csv_writer.writerow([video_name, frame_idx, gt_id, iou])
            continue
        # Load the predicted mask and binarize it
        pred_mask = np.array(Image.open(pred_mask_path)) > 0
        # Calculate IoU between GT and predicted mask
        iou = calculate_iou(gt_binary_mask, pred_mask)
        best_ious_for_each_gt_instance.append(iou)
        # Write the IoU result to the CSV file
        csv_writer.writerow([video_name, frame_idx, gt_id, iou])

    if not best_ious_for_each_gt_instance:
        # If there are no objects to evaluate, return perfect score
        return 1.0

    # Compute the mean IoU for this frame
    frame_miou = sum(best_ious_for_each_gt_instance) / len(best_ious_for_each_gt_instance)
    return frame_miou

# Prepare CSV file for writing IoU results
csv_output_path = "iou_results.csv"
csv_file = open(csv_output_path, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["video_name", "frame", "object_id", "iou"])

# video_names contains all the video in base_dir starting with "video_"
base_dir = "/scratch2/nico/examples/kubric"
video_names = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("video_")]

for video_name in video_names:
    print(f"Processing video: {video_name}")

    # Define paths
    sam_masks_dir = f"{base_dir}/results/sam2/{video_name}/sam_masks"
    gt_masks_dir = f"{base_dir}/{video_name}/gt_masks"
    metadata_path = f"{base_dir}/{video_name}/metadata.json"

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
        frame_miou = benchmark_frame(gt_mask_path, frame_sam_masks_dir, color_to_id_map, video_name, frame_idx)
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
