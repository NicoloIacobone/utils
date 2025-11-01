#!/usr/bin/env python3
import os
import sys
import pickle
import numpy as np

# Imposta qui la directory contenente il file vide_segments.pkl

def main_2():
    """
    Legge un file .npy in INPUT_DIR (cerca 'masks.npy') e stampa una descrizione della sua "shape".
    Comportamento simile a main(): stampa errori su stderr e termina con sys.exit in caso di problemi.
    """
    INPUT_DIR = "/scratch2/nico/examples/photos/single_frame/"
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
    INPUT_DIR = "/scratch2/nico/examples/photos/tenda_ufficio_sam/"
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

if __name__ == "__main__":
    main()
    main_2()
