#!/bin/bash
#SBATCH --job-name=setup_env        # Nome job (opzionale se lo lanci con sbatch)
#SBATCH --output=setup_env.out      # File di log
#SBATCH --error=setup_env.err       # File di errori
#SBATCH --time=01:00:00             # Tempo massimo
#SBATCH --partition=normal          # Partizione (dipende dal cluster Euler)
#SBATCH --gres=gpu:0                # Non serve GPU qui, quindi 0

# Step 0: pulizia moduli
module purge

# Step 1: carico stack e python
module load stack/2024-06 python/3.11

# Step 2: creo virtualenv
python -m venv myenv

# Step 3: attivo virtualenv
source myenv/bin/activate

# Step 4: upgrade pip
python -m pip install --upgrade pip

# Step 5: installo torch + cuda compatibile
python -m pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124

# Step 6: requirements
python -m pip install -r requirements.txt