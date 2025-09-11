import os

meeting_folder = "/scratch2/nico/examples/meeting_11_09"
output_kubric = "/scratch2/nico/kubric/output"
videos_folder = "/scratch2/nico/examples/kubric"
output_sam = "/scratch2/nico/examples/kubric/results/sam2"
output_spatrack = "/scratch2/nico/examples/kubric/results/SpaTrackV2"

# For each folder in videos_folder starting with "video_"
for entry in os.listdir(videos_folder):
    video_dir = os.path.join(videos_folder, entry)
    if entry.startswith("video_") and os.path.isdir(video_dir):
        # take the "frames" folder inside it, generate a .gif file, and save it inside a subfolder in meeting_folder with the same name as the video folder
        frames_dir = os.path.join(video_dir, "frames")
        if os.path.isdir(frames_dir):
            # Create a subfolder in meeting_folder with the same name as the video folder
            output_dir = os.path.join(meeting_folder, entry)
            os.makedirs(output_dir, exist_ok=True)
            gif_path = os.path.join(output_dir, f"{entry}.gif")
            try:
                os.system(f"ffmpeg -y -i {frames_dir}/%05d.jpg -vf 'fps=10,scale=320:-1:flags=lanczos' -c:v gif {gif_path}")
            except Exception as e:
                print(f"Failed to create gif for {entry}: {e}")

        # take the "gt_masks" folder inside it, generate a .gif file, and save it inside the same subfolder in meeting_folder
        gt_masks_dir = os.path.join(video_dir, "gt_masks")
        if os.path.isdir(gt_masks_dir):
            gt_gif_path = os.path.join(output_dir, f"{entry}_gt_masks.gif")
            try:
                os.system(f"ffmpeg -y -i {gt_masks_dir}/segmentation_%05d.png -vf 'fps=10,scale=320:-1:flags=lanczos' -c:v gif {gt_gif_path}")
            except Exception as e:
                print(f"Failed to create gt_masks gif for {entry}: {e}")

        # go to the output_sam folder, find the folder with the same name as the video folder, take the "masks" folder inside it, generate a .gif file, and save it inside the same subfolder in meeting_folder
        sam_video_dir = os.path.join(output_sam, entry)
        if os.path.isdir(sam_video_dir):
            sam_masks_dir = os.path.join(sam_video_dir, "masks")
            if os.path.isdir(sam_masks_dir):
                sam_gif_path = os.path.join(output_dir, f"{entry}_sam_masks.gif")
                try:
                    os.system(f"ffmpeg -y -i {sam_masks_dir}/frame_%04d_masks.png -vf 'fps=10,scale=320:-1:flags=lanczos' -c:v gif {sam_gif_path}")
                except Exception as e:
                    print(f"Failed to create sam_masks gif for {entry}: {e}")

        # go to the output_spatrack folder, find the folder with the same name as the video folder, take the "test_pred_track.mp4" file inside it, and copy it to the same subfolder in meeting_folder using the name "{video_folder_name}_spatrack.mp4"
        spatrack_video_dir = os.path.join(output_spatrack, entry)
        if os.path.isdir(spatrack_video_dir):
            spatrack_video_path = os.path.join(spatrack_video_dir, "test_pred_track.mp4")
            if os.path.isfile(spatrack_video_path):
                spatrack_output_path = os.path.join(output_dir, f"{entry}_spatrack.mp4")
                try:
                    os.system(f"cp {spatrack_video_path} {spatrack_output_path}")
                except Exception as e:
                    print(f"Failed to copy spatrack video for {entry}: {e}")

# just one time (to save files produced but not useful for the benchmark)
# from output_kubric, in the folder "video_23_more_dynamic_medium", copy into a subfolder in meeting_folder called "other_outputs" the file "metadata.json" 
other_outputs_dir = os.path.join(meeting_folder, "other_outputs")
os.makedirs(other_outputs_dir, exist_ok=True)
kubric_video_dir = os.path.join(output_kubric, "video_23_more_dynamic_medium")
kubric_metadata_path = os.path.join(kubric_video_dir, "metadata.json")
if os.path.isfile(kubric_metadata_path):
    try:
        os.system(f"cp {kubric_metadata_path} {other_outputs_dir}/metadata_video_23_more_dynamic_medium.json")
    except Exception as e:
        print(f"Failed to copy kubric metadata: {e}")

# For each file pattern, create a gif if files exist in the kubric_video_dir folder, output to other_outputs_dir
gif_patterns = [
    ("backward_flow_%05d.png", "backward_flow.gif"),
    ("forward_flow_%05d.png", "forward_flow.gif"),
    ("normal_%05d.png", "normal.gif"),
    ("object_coordinates_%05d.png", "object_coordinates.gif"),
]

for pattern, gif_name in gif_patterns:
    pattern_path = os.path.join(kubric_video_dir, pattern.replace("%05d", "00000"))
    if os.path.isfile(pattern_path):
        gif_output_path = os.path.join(other_outputs_dir, gif_name)
        try:
            os.system(f"ffmpeg -y -i {os.path.join(kubric_video_dir, pattern)} -vf 'fps=10,scale=320:-1:flags=lanczos' -c:v gif {gif_output_path}")
        except Exception as e:
            print(f"Failed to create gif {gif_name} in other_outputs: {e}")

# # now create a gif from the depth maps in the folder "video_23_more_dynamic_medium" inside output_kubric, files named "depth_%05d.tiff"
# depth_pattern_path = os.path.join(kubric_video_dir, "depth_00000.tiff")
# if os.path.isfile(depth_pattern_path):
#     depth_gif_output_path = os.path.join(other_outputs_dir, "depth.gif")
#     try:
#         os.system(f"ffmpeg -y -i {os.path.join(kubric_video_dir, 'depth_%05d.tiff')} -vf 'fps=10,scale=320:-1:flags=lanczos,format=gray' {depth_gif_output_path}")
#     except Exception as e:
#         print(f"Failed to create depth gif in other_outputs: {e}")