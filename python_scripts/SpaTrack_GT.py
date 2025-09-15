# Benchmark script for SpatialTrackerV2 vs. Ground Truth
# Tracking Consistency and EPE-3D
# Tracking Consistency: for each frame, project each tracklet onto the image plane and compute the IoU with the GT mask
# EPE-3D: for each video (or frame and then average), compute the distance between the predicted 3D position and the GT 3D position for each object

import numpy as np
from PIL import Image
import os
from glob import glob

def calculate_tracking_consistency(video_path, spatrack2_path):
    """
    Calculates Tracking Consistency for a single video.
    """
    print(f"\n--- Evaluating Video: {os.path.basename(video_path)} ---")

    # --- 1. LOAD DATA ---
    
    # Load SpatialTrackerV2 predictions
    pred_path = os.path.join(spatrack2_path, 'track2d_pred.npz')
    try:
        stv2_results = np.load(pred_path)
        # Assume the key is the first in the file
        pred_tracks_2d = stv2_results[list(stv2_results.keys())[0]] # Shape (T_pred, N, 3)
    except FileNotFoundError:
        print(f"ERROR: File 'track2d_pred.npz' not found. Skipping.")
        return None

    # Find ground truth mask files
    gt_mask_files = sorted(glob(os.path.join(video_path, 'gt_masks', 'segmentation_*.png')))
    if not gt_mask_files:
        print("ERROR: No ground truth masks found. Skipping.")
        return None

    # --- 2. DETERMINE PARAMETERS ---
    
    num_pred_frames, num_points, _ = pred_tracks_2d.shape
    num_gt_frames = len(gt_mask_files)
    
    # Load the first mask to get original dimensions
    first_gt_mask = np.array(Image.open(gt_mask_files[0]))
    H_orig, W_orig = first_gt_mask.shape[:2] # Handles both (H,W) and (H,W,3)

    # Scaled dimensions used by STv2
    H_scaled, W_scaled = 336, 336
    
    # Calculate stride and scale factor
    # Round to handle small differences (e.g. 120/40 = 3)
    stride = round(num_gt_frames / num_pred_frames) if num_pred_frames > 0 else 1
    scale_x = W_orig / W_scaled
    scale_y = H_orig / H_scaled

    print(f"Info: {num_gt_frames} GT frames, {num_pred_frames} predicted frames. Calculated stride: {stride}")
    print(f"Info: Original (GT) resolution: {W_orig}x{H_orig}, Predicted resolution: {W_scaled}x{H_scaled}")

    # --- 3. INITIALIZE COUNTERS ---
    
    total_predicted_points = 0
    consistent_points = 0

    # --- 4. ITERATE AND CALCULATE CONSISTENCY ---
    
    for i in range(num_pred_frames):
        # a. Find the corresponding GT frame
        gt_frame_index = i * stride
        if gt_frame_index >= len(gt_mask_files):
            print(f"Warning: GT index {gt_frame_index} out of bounds. Breaking loop.")
            break
            
        gt_mask_path = gt_mask_files[gt_frame_index]
        gt_instance_mask = np.array(Image.open(gt_mask_path))

        # b. Create "Foreground" mask (True if not background)
        # Handles both ID masks and RGB masks
        if gt_instance_mask.ndim == 3: # RGB mask
            background_mask = np.all(gt_instance_mask == [0,0,0], axis=-1)
        else: # ID mask
            background_mask = (gt_instance_mask == 0)
        foreground_mask = ~background_mask

        # c. Iterate over points in this frame
        for k in range(num_points):
            total_predicted_points += 1
            x_pred, y_pred, confidence = pred_tracks_2d[i, k, :]
            
            # i. Filter out off-screen points
            if not (0 <= x_pred < W_scaled and 0 <= y_pred < H_scaled):
                continue # Point is off-screen, so not consistent
                
            # iii. Rescale coordinates
            x_mapped = int(x_pred * scale_x)
            y_mapped = int(y_pred * scale_y)
            
            # Ensure mapped coordinates are still within bounds after rounding
            if not (0 <= x_mapped < W_orig and 0 <= y_mapped < H_orig):
                continue

            # iv. Check consistency
            if foreground_mask[y_mapped, x_mapped]:
                consistent_points += 1

    # --- 5. CALCULATE FINAL RESULT ---
    
    tracking_consistency = (consistent_points / total_predicted_points) * 100 if total_predicted_points > 0 else 0
    print(f"Result: {consistent_points} consistent points out of {total_predicted_points} total points.")
    
    return tracking_consistency

# --- MAIN SCRIPT ---

if __name__ == "__main__":
    videos_path = "/scratch2/nico/examples/kubric"
    spatrack2_output_path = os.path.join(videos_path, "results", "SpaTrackV2")
    video_names = [os.path.basename(d) for d in sorted(glob(os.path.join(videos_path, "video_*")))]

    results = {}
    for video_name in video_names:
        video_path = os.path.join(videos_path, video_name)
        spatrack2_path = os.path.join(spatrack2_output_path, video_name)
        consistency = calculate_tracking_consistency(video_path, spatrack2_path)
        if consistency is not None:
            results[video_name] = consistency
            
    print("\n\n===== FINAL BENCHMARK RESULTS =====")
    if results:
        for video_name, consistency in results.items():
            print(f"Video '{video_name}': Tracking Consistency = {consistency:.2f}%")
        
        total_avg_consistency = sum(results.values()) / len(results)
        print(f"\nOverall Average Consistency: {total_avg_consistency:.2f}%")
    print("===================================")