# script to organize kubric output files into a structured directory format
# used before fixing kubric output generation issues
import os
import re

current_dir = os.getcwd()
for entry in os.listdir(current_dir):
    if entry.startswith("video_") and os.path.isdir(entry):
        gt_masks_dir = f"/scratch2/nico/examples/kubric/{entry}/gt_masks"
        metadata_path = f"/scratch2/nico/examples/kubric/{entry}/metadata.json"
        frames_dir = f"/scratch2/nico/examples/kubric/{entry}/frames"
        src_metadata = os.path.join(current_dir, entry, "metadata.json")
        if os.path.isfile(src_metadata):
            dst_metadata = os.path.join(metadata_path)
            os.makedirs(os.path.dirname(dst_metadata), exist_ok=True)
            with open(src_metadata, "rb") as src_file, open(dst_metadata, "wb") as dst_file:
                dst_file.write(src_file.read())
        # Copy all files starting with "segmentation_" to gt_masks_dir
        src_masks_dir = os.path.join(current_dir, entry)
        os.makedirs(gt_masks_dir, exist_ok=True)
        for fname in os.listdir(src_masks_dir):
            if fname.startswith("segmentation_"):
                src_mask = os.path.join(src_masks_dir, fname)
                dst_mask = os.path.join(gt_masks_dir, fname)
                with open(src_mask, "rb") as fsrc, open(dst_mask, "wb") as fdst:
                    fdst.write(fsrc.read())
        # Copy all files starting with "[0-9][0-9][0-9][0-9][0-9]" to frames_dir
        src_frames_dir = os.path.join(current_dir, entry)
        os.makedirs(frames_dir, exist_ok=True)
        for fname in os.listdir(src_frames_dir):
            if re.match(r"^\d{5}", fname):
                src_frame = os.path.join(src_frames_dir, fname)
                dst_frame = os.path.join(frames_dir, fname)
                with open(src_frame, "rb") as fsrc, open(dst_frame, "wb") as fdst:
                    fdst.write(fsrc.read())