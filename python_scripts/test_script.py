import numpy as np
from PIL import Image
import os
from glob import glob

videos_path = "/scratch2/nico/examples/kubric"
spatrack2_output_path = os.path.join(videos_path, "results", "SpaTrackV2")
video_names = [os.path.basename(d) for d in sorted(glob(os.path.join(videos_path, "video_*")))]

video_path = os.path.join(videos_path, video_names[0])
gt_mask_path = os.path.join(video_path, 'gt_masks', 'segmentation_00019.png')

print(f"Opening image: {gt_mask_path}")

gt_instance_mask = np.array(Image.open(gt_mask_path))
print(gt_instance_mask[88, 144])
# print(gt_instance_mask.shape)
# print(np.unique(gt_instance_mask))


gt_instance_mask = np.array(Image.open(gt_mask_path).convert("RGB"))
print(gt_instance_mask[88, 144])
# print(gt_instance_mask.shape)
# print(np.unique(gt_instance_mask))

img = Image.open(gt_mask_path)
palette = img.getpalette()  # [R0,G0,B0, R1,G1,B1, ...]
gt_instance_mask = np.array(img)  # <-- maschera a 1 canale
index = int(gt_instance_mask[88, 144])  # assicurati che sia uno scalare int
color = palette[index*3:index*3+3]
print(f"Indice: {index}, Colore RGB: {color}")
