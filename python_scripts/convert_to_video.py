import cv2
import os
import glob

# Directory containing jpg frames
frames_dir = '/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/examples/kubric/video_01_static_short'  # Change this to your folder path

# Output video file
output_file = 'output_video.mp4'

# Get list of jpg files sorted by name
images = sorted(glob.glob(os.path.join(frames_dir, '*.jpg')))

if not images:
    print("No .jpg files found in the specified directory.")
    exit(1)

# Read first image to get frame size
frame = cv2.imread(images[0])
height, width, layers = frame.shape

# Define video codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 24  # Change FPS if needed
video = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

for img_path in images:
    img = cv2.imread(img_path)
    if img is None:
        print(f"Warning: Could not read {img_path}, skipping.")
        continue
    video.write(img)

video.release()
print(f"Video saved as {output_file}")