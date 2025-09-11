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