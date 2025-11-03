#!/usr/bin/env python3
import os
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Imposta qui la directory contenente il file vide_segments.pkl

def show_mask(mask, ax, obj_id=None, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        cmap = plt.get_cmap("tab10")
        cmap_idx = 0 if obj_id is None else obj_id
        color = np.array([*cmap(cmap_idx)[:3], 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def main_2():
    """
    Legge un file .npy in INPUT_DIR (cerca 'masks.npy') e stampa una descrizione della sua "shape".
    Comportamento simile a main(): stampa errori su stderr e termina con sys.exit in caso di problemi.
    """
    # INPUT_DIR = "/scratch2/nico/examples/photos/single_frame/"
    INPUT_DIR = "."
    filenames = ["masks.npy"]
    filepath = None
    for name in filenames:
        candidate = os.path.join(INPUT_DIR, name)
        if os.path.isfile(candidate):
            filepath = candidate
            break

    if filepath is None:
        print(f"Errore: nessun file {filenames} trovato in {INPUT_DIR}", file=sys.stderr)
        sys.exit(2)

    try:
        data = np.load(filepath, allow_pickle=True)
    except Exception as e:
        print(f"Errore durante il caricamento di {filepath}: {e}", file=sys.stderr)
        sys.exit(3)

    shape = describe(data)
    print(shape)
    print(data[0]['segmentation'].shape)

def describe(obj):
    # restituisce una rappresentazione semplice della "shape" dell'oggetto
    if hasattr(obj, "shape"):
        return obj.shape
    if hasattr(obj, "size") and not hasattr(obj, "shape"):
        try:
            return ("size", obj.size)
        except Exception:
            pass
    if isinstance(obj, dict):
        return {k: describe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [describe(v) for v in obj]
    return type(obj).__name__

def main():
    # INPUT_DIR = "/scratch2/nico/examples/photos/tenda_ufficio_sam/"
    INPUT_DIR = "analyze_this"
    filenames = ["video_segments.pkl"]
    # filenames = ["masks.npy"]
    filepath = None
    for name in filenames:
        candidate = os.path.join(INPUT_DIR, name)
        if os.path.isfile(candidate):
            filepath = candidate
            break

    if filepath is None:
        print(f"Errore: nessun file {filenames} trovato in {INPUT_DIR}", file=sys.stderr)
        sys.exit(2)

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
    except Exception as e:
        print(f"Errore durante il caricamento di {filepath}: {e}", file=sys.stderr)
        sys.exit(3)

    shape = describe(data)
    print(shape)
    print(data[0])

def visualize_sam_segments(masks_path, images_dir):
    """
    Visualizza le maschere SAM da un file numpy.
    
    Args:
        masks_path: percorso al file video_segments.npy
        images_dir: directory contenente i frame JPEG/JPG
    """

    data = np.load(masks_path, allow_pickle=True)
    data = data.item()
    
    # Scansiona tutti i frame JPEG nella directory
    frame_names = [
        p for p in os.listdir(images_dir)
        if os.path.splitext(p)[-1].lower() in [".jpg", ".jpeg"]
    ]
    frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
    
    for out_frame_idx in range(len(frame_names)):
        plt.figure(figsize=(6, 4))
        plt.title(f"frame {out_frame_idx}")
        plt.imshow(Image.open(os.path.join(images_dir, frame_names[out_frame_idx])))
        for out_obj_id, out_mask in data[out_frame_idx].items():
            show_mask(out_mask, plt.gca(), obj_id=out_obj_id)
    
    plt.show()

if __name__ == "__main__":
    INPUT_DIR = "analyze_this"
    masks_path = os.path.join(INPUT_DIR, "video_segments.npy")
    visualize_sam_segments(masks_path, INPUT_DIR)
    # main()