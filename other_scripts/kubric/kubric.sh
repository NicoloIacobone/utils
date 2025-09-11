#!/bin/bash

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_01_static_short \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=4 \
    --max_num_static_objects=10 \
    --min_num_dynamic_objects=0 \
    --max_num_dynamic_objects=0 \
    --max_camera_movement=8.0 \
    --frame_end=72

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_02_static_medium \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=4 \
    --max_num_static_objects=10 \
    --min_num_dynamic_objects=0 \
    --max_num_dynamic_objects=0 \
    --max_camera_movement=8.0 \
    --frame_end=120

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_03_static_long \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=4 \
    --max_num_static_objects=10 \
    --min_num_dynamic_objects=0 \
    --max_num_dynamic_objects=0 \
    --max_camera_movement=8.0 \
    --frame_end=240

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_04_static_long \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=4 \
    --max_num_static_objects=10 \
    --min_num_dynamic_objects=0 \
    --max_num_dynamic_objects=0 \
    --max_camera_movement=30.0 \
    --frame_end=240

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_05_dynamic_short \
    --camera=fixed_random \
    --min_num_static_objects=0 \
    --max_num_static_objects=0 \
    --min_num_dynamic_objects=3 \
    --max_num_dynamic_objects=3 \
    --frame_end=72

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_06_dynamic_medium \
    --camera=fixed_random \
    --min_num_static_objects=0 \
    --max_num_static_objects=0 \
    --min_num_dynamic_objects=3 \
    --max_num_dynamic_objects=3 \
    --frame_end=120

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_07_dynamic_occlusion_short \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=2 \
    --max_num_dynamic_objects=2 \
    --max_camera_movement=10.0 \
    --frame_end=72

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_08_dynamic_occlusion_medium \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=2 \
    --max_num_dynamic_objects=2 \
    --max_camera_movement=18.0 \
    --frame_end=120

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_09_dynamic_occlusion_long \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=2 \
    --max_num_dynamic_objects=2 \
    --max_camera_movement=25.0 \
    --frame_end=240

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_10_more_dynamic_short \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=5 \
    --max_num_dynamic_objects=5 \
    --max_camera_movement=10.0 \
    --frame_end=72

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_11_more_dynamic_medium \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=5 \
    --max_num_dynamic_objects=5 \
    --max_camera_movement=18.0 \
    --frame_end=120

podman run --rm --interactive \
    --volume "$(pwd):/kubric" \
    kubricdockerhub/kubruntu /usr/bin/python3 \
    challenges/movi/movi_def_worker.py \
    --job-dir=output/video_12_more_dynamic_long \
    --camera=linear_movement_linear_lookat \
    --min_num_static_objects=5 \
    --max_num_static_objects=5 \
    --min_num_dynamic_objects=5 \
    --max_num_dynamic_objects=5 \
    --max_camera_movement=25.0 \
    --frame_end=240