from pathlib import Path
from PIL import Image, UnidentifiedImageError
import logging

#!/usr/bin/env python3
# convert_png_to_jpg.py
# Nella variabile INPUT_FOLDER mettere il path della cartella contenente PNG. Nessun input utente.


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

# Cambiare questo valore con la cartella che contiene le PNG
INPUT_FOLDER = "/scratch2/nico/examples/photos/tenda_ufficio_sam"

def convert_png_to_jpg(folder_path: Path):
    if not folder_path.is_dir():
        logging.error("Cartella non trovata: %s", folder_path)
        return

    for p in folder_path.iterdir():
        if not p.is_file() or p.suffix.lower() != ".png":
            continue

        try:
            with Image.open(p) as im:
                # Gestione trasparenza: sfondo bianco
                if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    # se ha canale alpha, usarlo come mask
                    alpha = im.split()[-1] if im.mode != "P" else im.convert("RGBA").split()[-1]
                    bg.paste(im.convert("RGBA"), mask=alpha)
                    rgb = bg
                else:
                    rgb = im.convert("RGB")

                out_path = p.with_suffix(".jpg")
                rgb.save(out_path, "JPEG", quality=95)
                p.unlink()  # elimina l'originale PNG
                logging.info("Convertito: %s -> %s", p.name, out_path.name)

        except UnidentifiedImageError:
            logging.warning("File non valido come immagine: %s", p.name)
        except Exception as e:
            logging.error("Errore convertendo %s: %s", p.name, e)

if __name__ == "__main__":
    convert_png_to_jpg(Path(INPUT_FOLDER))