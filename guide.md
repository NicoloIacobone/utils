# SAM3
0. module purge
0. git clone https://github.com/NicoloIacobone/sam3.git
0. cd sam3
1. module load stack/2024-06 python/3.12.8 cuda/12.8.0 eth_proxy
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip wheel setuptools
5. pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
6. pip install -e .
7. pip install -e ".[notebooks]"
8. pip install -e ".[train,dev]"
9. pip install einops ninja && pip install flash-attn-3 --no-deps --index-url https://download.pytorch.org/whl/cu128
10. srun --time=00:30:00 --ntasks=1 --cpus-per-task=1 --mem-per-cpu=8G --gpus=rtx_4090:1 --pty bash
11. /cluster/scratch/niacobone/sam3
12. module load stack/2024-06 python/3.12.8 cuda/12.8.0 eth_proxy
13. source myenv/bin/activate
14. pip install --no-build-isolation git+https://github.com/ronghanghu/cc_torch.git
<!-- 10. hf auth login -->
11. hf download facebook/sam3.1

# VGGT-omega
0. module purge
0. git clone https://github.com/NicoloIacobone/vggt-omega.git
0. cd vggt-omega
1. module load stack/2024-06 python/3.12 cuda/12.4
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip wheel setuptools
5. pip install -r requirements.txt
6. pip install -e .
7. pip install -r requirements_demo.txt
<!-- 10. hf auth login -->
8. hf download facebook/VGGT-Omega

# MapAnything
0. module purge
0. git clone https://github.com/NicoloIacobone/map-anything.git
0. cd map-anything
1. module load stack/2024-06 python/3.12 cuda/12.4
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip wheel setuptools
5. pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
6. pip install -e .
7. pip install -e ".[all]"
8. rm -rf /cluster/scratch/niacobone/.cache/torch/hub/facebookresearch_dinov2_main
9. rm -rf /cluster/scratch/niacobone/.cache/torch/hub/checkpoints
<!-- 8. pre-commit install -->

## SAM2
module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy\
source myenv/bin/activate

### (senza --system-site-packages)
0. git clone https://github.com/NicoloIacobone/sam2.git
0. cd sam2
0. module purge
1. module load stack/2024-06 python/3.11 cuda/12.4
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip wheel setuptools
5. pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -e .
7. pip install -e .[notebooks]
8. cd checkpoints && ./download_ckpts.sh && cd ..
9. pip install seaborn wandb
10. ENJOY

## Connessione
ssh niacobone@euler.ethz.ch

## Cartelle
/cluster/home/niacobone --> 50GB con backup\
/cluster/work/igp_psr/niacobone --> 150TB shared con tutto il lab --> **lavora qui**\
/cluster/scratch/niacobone --> 2TB cancellata ogni 2 settimane

## Regole per eseguire
1. Le cartelle con codice (git clone) sono su home
2. I risultati e i dataset sono su work
3. Per l'esecuzione degli script si lavora su scratch

## Caricamento dei moduli
module load stack/2024-06\
module load python/X.Y.Z\
module load cuda/X.Y.Z\
module load eth_proxy <-- da usare se bisogna collegarsi ad un servizio esterno (es. wandb, huggingface, aws)\
code-server/4.89.1

## Creazione env
python -m venv --system-site-packages myenv\
source myenv/bin/activate\
pip install --upgrade pip\
pip install -r requirements.txt
---
## DUSt3R
module load stack/2024-06 python/3.11 cuda/12.1 eth_proxy\
source myenv/bin/activate
---
## AnyCam
module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy\
source myenv/bin/activate

### (senza --system-site-packages)
0. module purge
1. module load stack/2024-06 python/3.11 cuda/12.4
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt
7. ./download_checkpoints.sh anycam_seq8

## Esecuzione **FUNZIONANTE** anycam
Euler: eseguire lo script anycam_demo_nico_1.py --> passare i 6 file sul PC Lab\
PC Lab: eseguire lo script anycam_demo_visualize.py
---
## SpatialTrackerV2
module load stack/2024-06 python/3.11 eth_proxy\
source myenv/bin/activate\
python tapip3d_viz.py nome/file --> visualizzare risultato

### FUNZIONANTE (senza --system-site-packages)
0. module purge
0. git clone https://github.com/NicoloIacobone/SpaTrackerV2.git
<!-- 0. git submodule update --init --recursive -->
1. module load stack/2024-06 python/3.11
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. python -m pip install -r requirements.txt (controlla che nei requirement.txt ci sia pyceres==2.4)
7. ENJOY
---

# wai_processing
0. module purge
0. cd map-anything
1. module load stack/2024-06 python/3.12 cuda/12.4 eth_proxy
2. python -m venv wai_processing
3. source wai_processing/bin/activate
4. pip install --upgrade pip wheel setuptools
5. pip install --no-deps .
6. cd data_processing/wai_processing/
7. pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
8. srun --cpus-per-task=1 --mem-per-cpu=4096 --gpus=rtx_4090:1 --time=01:00:00 --pty bash
9. cd map-anything/data_processing/wai_processing/
10. source ../../wai_processing/bin/activate
11. pip install -e .[all] --no-build-isolation

---
### Usare VS Code (code-server su Euler)
1. nano ~/.config/euler/jupyterhub/config_vs_code e aggiungere le seguenti due righe
2. module load stack/2024-06 python/3.11 eth_proxy code-server/4.89.1
3. source /cluster/work/igp_psr/niacobone/SpaTrackerV2/myenv2/bin/activate

## Comandi utili
git submodule update --init --recursive --> inizializza e aggiorna i sottogruppi git (a volte non viene detto esplicitamente di farlo)\
pwd --> mostra il percorso della cartella corrente\
lquota --> mostra lo spazio utilizzato e disponibile\
nvidia-smi --> mostra informazioni sulla GPU\
module spider nome_modulo --> mostra i moduli disponibili\
module load nome_modulo --> carica il modulo\
module list --> mostra i moduli caricati\
module unload nome_modulo --> rimuove il modulo\
module purge --> rimuove tutti i moduli caricati\
rm -rf cartella --> rimuove la cartella e tutto il suo contenuto\
tar -czf myenv.tar.gz myenv --> crea un archivio compresso della cartella\
tar -xzf myenv.tar.gz --> estrae il contenuto dell'archivio compresso\
tar -tzf myenv.tar.gz > /dev/null --> testare se l'archivio è valido\
mv cartella_origine/ cartella_destinazione/ --> sposta la cartella di origine nella cartella di destinazione\
cp -r cartella_origine/ cartella_destinazione/ --> copia la cartella di origine nella cartella di destinazione\
du -sh nome_cartella --> mostra l'uso del disco della cartella

## Collegare la repo ufficiale al mio fork
1. git remote -v
2. git remote remove origin
3. git remote add origin [link del mio fork]
4. git remote -v
5. git pull --> errore
6. git checkout main
7. git branch --set-upstream-to=origin/main main
8. git pull

## Comandi SLURM
squeue --all --> mostra i job in coda\
srun python script.py --> esegue uno script in coda\
sbatch job.sh --> invia un job in coda\
scancel job_id --> cancella un job in coda\
nano ~/.config/euler/jupyterhub/config_vs_code --> configurazione al lancio di code-server