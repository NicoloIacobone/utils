import os
import sys
from pathlib import Path
from PIL import Image
import pillow_heif

def convert_heic_to_png(folder_path):
    folder = Path(folder_path)
    for heic_file in folder.glob("*.HEIC"):
        png_file = heic_file.with_suffix('.png')
        heif_file = pillow_heif.open_heif(str(heic_file))
        image = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data,
            "raw"
        )
        image.save(png_file)
        print(f"Convertito: {heic_file} -> {png_file}")
        # Elimina il file HEIC originale
        heic_file.unlink()
        print(f"Eliminato: {heic_file}")

if __name__ == "__main__":
    input_folder = "/scratch2/nico/examples/photos/box_ufficio"
    convert_heic_to_png(input_folder)
