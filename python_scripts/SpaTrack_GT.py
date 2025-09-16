# Benchmark script for SpatialTrackerV2 vs. Ground Truth
# Tracking Consistency and EPE-3D
# Tracking Consistency: for each frame, project each tracklet onto the image plane and compute the IoU with the GT mask
# EPE-3D: for each video (or frame and then average), compute the distance between the predicted 3D position and the GT 3D position for each object

import numpy as np
from PIL import Image
import os
from glob import glob
import matplotlib.pyplot as plt
import csv
from collections import defaultdict

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
        print(f"DEBUG: Loaded predictions from {pred_path}, shape: {pred_tracks_2d.shape}")
    except FileNotFoundError:
        print(f"ERROR: File 'track2d_pred.npz' not found. Skipping.")
        return None

    # Find ground truth mask files
    gt_mask_files = sorted(glob(os.path.join(video_path, 'gt_masks', 'segmentation_*.png')))
    print(f"DEBUG: Found {len(gt_mask_files)} GT mask files in {os.path.join(video_path, 'gt_masks')}")
    if not gt_mask_files:
        print("ERROR: No ground truth masks found. Skipping.")
        return None

    # --- 2. DETERMINE PARAMETERS ---
    
    num_pred_frames, num_points, _ = pred_tracks_2d.shape
    num_gt_frames = len(gt_mask_files)
    
    # Load the first mask to get original dimensions
    first_gt_mask = np.array(Image.open(gt_mask_files[0]))
    H_orig, W_orig = first_gt_mask.shape[:2] # Handles both (H,W) and (H,W,3)
    print(f"DEBUG: First GT mask shape: {first_gt_mask.shape}")

    # Scaled dimensions used by STv2
    H_scaled, W_scaled = 336, 336
    
    # Calculate stride and scale factor
    # Round to handle small differences (e.g. 120/40 = 3)
    stride = round(num_gt_frames / num_pred_frames) if num_pred_frames > 0 else 1
    scale_x = W_orig / W_scaled
    scale_y = H_orig / H_scaled

    print(f"Info: {num_gt_frames} GT frames, {num_pred_frames} predicted frames. Calculated stride: {stride}")
    print(f"Info: Original (GT) resolution: {W_orig}x{H_orig}, Predicted resolution: {W_scaled}x{H_scaled}")
    print(f"DEBUG: scale_x={scale_x}, scale_y={scale_y}")

    # --- 3. INITIALIZE COUNTERS ---
    total_predicted_points = 0
    consistent_score = 0.0

    # --- NEW: Assign IDs to predicted points in first frame ---
    pred_point_ids = np.zeros(num_points, dtype=int)
    # Use the first GT mask for ID assignment
    for k in range(num_points):
        x_pred, y_pred, confidence = pred_tracks_2d[0, k, :]
        # Rescale coordinates
        x_mapped = int(x_pred * scale_x)
        y_mapped = int(y_pred * scale_y)
        # Check bounds
        if 0 <= x_mapped < W_orig and 0 <= y_mapped < H_orig:
            if first_gt_mask.ndim == 3:
                # RGB mask: use first channel as ID (or custom logic)
                pred_point_ids[k] = first_gt_mask[y_mapped, x_mapped, 0]
            else:
                pred_point_ids[k] = first_gt_mask[y_mapped, x_mapped]
        else:
            pred_point_ids[k] = 0  # background or out of bounds

    # --- Prepare CSV output (one CSV per video) ---
    # We write per-frame rows with columns [video_name, frame, object_id, iou].
    video_name = os.path.basename(video_path)
    csv_path = os.path.join(os.path.dirname(spatrack2_path), "tracking_consistency_spatrack2.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    # --- 4. ITERATE AND CALCULATE CONSISTENCY ---
    # Open CSV once for this video and append rows for each frame
    with open(csv_path, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Header as requested
        if csv_file.tell() == 0:
            csv_writer.writerow(["video_name", "frame_index", "object_id", "iou"])  # iou here is a point-based proxy per object

        for i in range(num_pred_frames):
            # a. Find the corresponding GT frame
            gt_frame_index = i * stride
            print(f"DEBUG: Frame {i}: GT frame index {gt_frame_index}")
            if gt_frame_index >= len(gt_mask_files):
                print(f"Warning: GT index {gt_frame_index} out of bounds. Breaking loop.")
                break
            gt_mask_path = gt_mask_files[gt_frame_index]
            gt_instance_mask = np.array(Image.open(gt_mask_path))
            print(f"DEBUG: Loaded GT mask {gt_mask_path}, shape: {gt_instance_mask.shape}")

            # b. Create "Foreground" mask (True if not background)
            # Handles both ID masks and RGB masks
            if gt_instance_mask.ndim == 3:
                # RGB mask: foreground where any channel is non-zero
                foreground_mask = np.any(gt_instance_mask != 0, axis=2)
            else:
                # Single-channel ID mask: foreground where id != 0
                foreground_mask = gt_instance_mask != 0

            # c. Iterate over points in this frame
            # Collect per-object scores for this frame, then write CSV rows after processing all points of the frame
            frame_obj_scores = defaultdict(list)

            for k in range(num_points):
                x_pred, y_pred, confidence = pred_tracks_2d[i, k, :]
                print(f"DEBUG: Frame {i}, Point {k}: x_pred={x_pred}, y_pred={y_pred}, confidence={confidence}")

                total_predicted_points += 1
                found_score = 0.0

                # i. Off-screen points in predicted (scaled) space
                if not (0 <= x_pred < W_scaled and 0 <= y_pred < H_scaled):
                    print(f"DEBUG: Point {k} is off-screen (predicted coords: {x_pred}, {y_pred}), trying radius search.")
                    # Rescale coordinates for radius search
                    x_mapped = int(x_pred * scale_x)
                    y_mapped = int(y_pred * scale_y)
                    # Radius search logic
                    max_radius = 5
                    score_table = {1: 0.99, 2: 0.9, 3: 0.8, 4: 0.5, 5: 0.30}  # tune these values
                    target_id = pred_point_ids[k]
                    found = False
                    for r in range(1, max_radius + 1):
                        for dx in range(-r, r + 1):
                            for dy in range(-r, r + 1):
                                if dx * dx + dy * dy > r * r:
                                    continue
                                nx = x_mapped + dx
                                ny = y_mapped + dy
                                if 0 <= nx < W_orig and 0 <= ny < H_orig:
                                    if foreground_mask[ny, nx]:
                                        if gt_instance_mask.ndim == 3:
                                            local_id = gt_instance_mask[ny, nx, 0]
                                        else:
                                            local_id = gt_instance_mask[ny, nx]
                                        if local_id == target_id and local_id != 0:
                                            found_score = score_table.get(r, 0.0)
                                            print(f"DEBUG: Off-screen Point {k} found in radius {r} at ({nx},{ny}), score={found_score}")
                                            found = True
                                            break
                            if found:
                                break
                        if found:
                            break
                    if not found:
                        # If still not found, ignore this point (decrement total_predicted_points) and skip CSV aggregation
                        total_predicted_points -= 1
                        print(f"DEBUG: Off-screen Point {k} not found in radius, ignored from total_predicted_points.")
                        continue  # Skip rest of logic for off-screen points
                    else:
                        # Found via radius search, count towards global score and per-object aggregation
                        consistent_score += found_score
                        frame_obj_scores[pred_point_ids[k]].append(float(found_score))
                        continue

                # ii. In-bounds: rescale coordinates
                x_mapped = int(x_pred * scale_x)
                y_mapped = int(y_pred * scale_y)
                print(f"DEBUG: Point {k} mapped to GT coords: ({x_mapped}, {y_mapped})")

                # Ensure mapped coordinates are still within bounds after rounding
                if not (0 <= x_mapped < W_orig and 0 <= y_mapped < H_orig):
                    print(f"DEBUG: Mapped point {k} out of GT bounds, skipping.")
                    continue

                # iii. Check consistency: foreground and ID match
                if foreground_mask[y_mapped, x_mapped]:
                    # Get GT ID at this location
                    if gt_instance_mask.ndim == 3:
                        gt_id = gt_instance_mask[y_mapped, x_mapped, 0]
                    else:
                        gt_id = gt_instance_mask[y_mapped, x_mapped]
                    if gt_id == pred_point_ids[k] and gt_id != 0:
                        found_score = 1.0
                        print(f"DEBUG: Point {k} is consistent (foreground, ID match: {gt_id}).")
                    else:
                        print(f"DEBUG: Point {k} is foreground but ID mismatch (GT: {gt_id}, Pred: {pred_point_ids[k]}).")
                else:
                    print(f"DEBUG: Point {k} is NOT consistent (background).")

                # iv. If not found, search in a circle of radius 5 around mapped location
                if found_score == 0.0:
                    max_radius = 5
                    score_table = {1: 0.99, 2: 0.9, 3: 0.8, 4: 0.5, 5: 0.30}  # tune these values
                    target_id = pred_point_ids[k]
                    found = False
                    for r in range(1, max_radius + 1):
                        for dx in range(-r, r + 1):
                            for dy in range(-r, r + 1):
                                if dx * dx + dy * dy > r * r:
                                    continue
                                nx = x_mapped + dx
                                ny = y_mapped + dy
                                if 0 <= nx < W_orig and 0 <= ny < H_orig:
                                    if foreground_mask[ny, nx]:
                                        if gt_instance_mask.ndim == 3:
                                            local_id = gt_instance_mask[ny, nx, 0]
                                        else:
                                            local_id = gt_instance_mask[ny, nx]
                                        if local_id == target_id and local_id != 0:
                                            found_score = score_table.get(r, 0.0)
                                            print(f"DEBUG: Point {k} found in radius {r} at ({nx},{ny}), score={found_score}")
                                            found = True
                                            break
                        if found:
                            break
                    # no special handling if still 0.0: keep the point with score 0

                # v. Accumulate scores
                consistent_score += found_score
                frame_obj_scores[pred_point_ids[k]].append(float(found_score))

            # d. After processing all points of the frame, write one CSV row per object with the mean score
            # NOTE: "iou" here represents the mean point-consistency score for that object in this frame.
            for obj_id, scores in frame_obj_scores.items():
                obj_iou = float(np.mean(scores)) if len(scores) > 0 else 0.0
                csv_writer.writerow([video_name, gt_frame_index, int(obj_id), obj_iou])


    # --- 5. CALCULATE FINAL RESULT ---
    
    tracking_consistency = (consistent_score / total_predicted_points) * 100 if total_predicted_points > 0 else 0
    print(f"Result: Consistency score {consistent_score:.2f} out of {total_predicted_points} total points.")
    print(f"DEBUG: Tracking consistency = {tracking_consistency:.2f}%")
    return tracking_consistency

# --- MAIN SCRIPT ---

if __name__ == "__main__":
    videos_path = "/scratch2/nico/examples/kubric"
    spatrack2_output_path = os.path.join(videos_path, "results", "SpaTrackV2")
    video_names = [os.path.basename(d) for d in sorted(glob(os.path.join(videos_path, "video_*")))]
    # video_names = ["video_24_more_dynamic_long"] # test su singolo video

    print(f"DEBUG: Found video names: {video_names}")

    results = {}
    for video_name in video_names:
        video_path = os.path.join(videos_path, video_name)
        spatrack2_path = os.path.join(spatrack2_output_path, video_name)
        print(f"DEBUG: Processing video '{video_name}'")
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