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
9. ENJOY
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
<!-- 8. pre-commit install -->

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

## Esecuzione con rerun (anycam) - NOT WORKING
Terminale 1: rerun --serve-web --> prima riga dell'INFO dice a che indirizzo collegarsi dallo script, seconda riga a che indirizzo hosta\
Terminale 2: ssh -L 9090:localhost:9090 -L 9876:localhost:9876 niacobone@euler.ethz.ch --> la prima porta (9090) la prendi dalla seconda riga dell'INFO, la seconda (9876) la prendi dalla prima riga dell'INFO\
Terminale 3: srun ... ++rerun_mode=connect ++rerun_address=localhost:9876 --> la porta (9876) la prendi dalla prima riga dell'INFO

---
## Passi per provare a installare il venv di SpaTrack2
### Non funzionante
1. module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy
2. python -m venv --system-site-packages myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt
7. ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.

### Seconda prova (senza system-site-packages) - LENTISSIMO - ~
0. module purge
1. module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy code-server/4.89.1
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. pip install -r requirements.txt
6. ERROR: Cannot import the C++ backend pycolmap._core

### Terza prova (senza system-site-packages) - LENTISSIMO - ~
0. module purge
1. module load stack/2024-06 python_cuda/3.11.6 code-server/4.89.1
2. python -m venv myenv_cuda
3. source myenv_cuda/bin/activate
4. pip install --upgrade pip
5. pip install -r requirements.txt
6. ERROR: Cannot import the C++ backend pycolmap._core

### Quarta prova (con system-site-packages) ~
0. module purge
1. module load stack/2024-06 python_cuda/3.11.6 code-server/4.89.1
2. python -m venv --system-site-packages myenv_cuda_stack
3. source myenv_cuda_stack/bin/activate
4. pip install --upgrade pip
5. pip install -r requirements.txt

### Quinta prova (con system-site-packages) ~
0. module purge
1. module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy
2. python -m venv --system-site-packages myenv5
3. source myenv5/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt

### Sesta prova (senza system-site-packages) ~
0. module purge
1. module load stack/2024-06 python/3.11 cuda/12.4 eth_proxy
2. python -m venv myenv6
3. source myenv6/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt

### Settima prova (con system-site-packages)
0. module purge
1. module load stack/2024-06 python/3.11
2. python -m venv --system-site-packages myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt

### Ottava prova (senza system-site-packages)
0. module purge
1. module load stack/2024-06 python/3.11
2. python -m venv myenv2
3. source myenv2/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. pip install -r requirements.txt
7. ERROR: Cannot import the C++ backend pycolmap._core ... Make sure that you successfully install the package with $ python -m pip install pycolmap
8. pip uninstall pycolmap
9. pip cache purge
10. pip install --no-cache-dir --force-reinstall --verbose pycolmap
11. python -c "import pycolmap" --> error
12. ERROR: pip's dependency resolver does not currently take into account all the packages that are installed ... requires numpy<2.3.0
13. pip install "numpy<2.3.0"
14. pip list | grep numpy --> check that it is listed a version of numpy < 2.3.0
15. python -c "import pycolmap" --> no error
16. ENJOY

### Ottava prova (**senza** system-site-packages)
0. module purge
1. module load stack/2024-06 python/3.11
2. python -m venv myenv
3. source myenv/bin/activate
4. pip install --upgrade pip
5. python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
6. python -m pip install -r requirements.txt
7. python -m pip install pyceres==2.4
7. ERROR: Cannot import the C++ backend pycolmap._core ... Make sure that you successfully install the package with $ python -m pip install pycolmap
8. pip uninstall pycolmap
9. pip cache purge
10. pip install --no-cache-dir --force-reinstall --verbose pycolmap==0.6.1
11. python -c "import pycolmap" --> error
12. ERROR: pip's dependency resolver does not currently take into account all the packages that are installed ... requires numpy<2.3.0
13. pip install "numpy<2.3.0"
14. pip list | grep numpy --> check that it is listed a version of numpy < 2.3.0
15. python -c "import pycolmap" --> no error
16. ENJOY
---