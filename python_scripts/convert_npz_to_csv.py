# Open a .npz file containing a 3D numpy array of shape (n, m, 3)
# where n is the number of frames, m is the number of objects, and 3 represents the (x, y, C) coordinates (C is confidence of the predicted x, y).
# # Convert this array into a CSV file where each row corresponds to a frame and contains the (x, y) coordinates of all objects in that frame.
# The (x, y) coordinates should be scaled to fit in a 256x256 image (i.e., multiply x and y by 255/336 and round to the nearest integer).

import os
import numpy as np
import sys
import csv

file_path = "/scratch2/nico/examples/kubric/results/SpaTrackV2/test_track_2d/video_02_static_medium/track2d_pred.npz"

data = np.load(file_path)
# print(list(data.keys()))
csv_file_path = file_path.replace('.npz', '.csv')

arr = data['track2d_pred']  # assuming the array is stored with this key
n, m, _ = arr.shape

with open(csv_file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(n):
        row = []
        for j in range(m):
            x, y = arr[i, j, 0], arr[i, j, 1]
            x_scaled = int(round(x * 255 / 336))
            y_scaled = int(round(y * 255 / 336))
            row.extend([x_scaled, y_scaled])
        writer.writerow(row)