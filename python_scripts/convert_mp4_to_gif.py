import sys
import os

import moviepy.editor as mp

def mp4_to_gif(mp4_path, gif_path=None):
    if not os.path.isfile(mp4_path):
        print(f"File not found: {mp4_path}")
        return
    if gif_path is None:
        gif_path = os.path.splitext(mp4_path)[0] + ".gif"
    clip = mp.VideoFileClip(mp4_path)
    clip.write_gif(gif_path)
    print(f"GIF saved to: {gif_path}")

if __name__ == "__main__":
    input_path = "/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/examples/meeting_11_09/video_17_dynamic_short/video_17_dynamic_short_spatrack.mp4"
    output_path = "/Users/nicoloiacobone/Desktop/nico/UNIVERSITA/MAGISTRALE/Tesi/Tommasi/Zurigo/git_clones/examples/meeting_11_09/video_17_dynamic_short/video_17_dynamic_short_spatrack.gif"
    mp4_to_gif(input_path, output_path)