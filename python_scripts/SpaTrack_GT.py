# Benchmark script for SpatialTrackerV2 vs. Ground Truth
# Tracking Consistency and EPE-3D
# Tracking Consistency: for each frame, project each tracklet onto the image plane and compute the IoU with the GT mask
# EPE-3D: for each video (or frame and then average), compute the distance between the predicted 3D position and the GT 3D position for each object