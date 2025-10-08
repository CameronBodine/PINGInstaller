
import os
import subprocess
import re

def get_conda_key():

    ####################
    # Make the conda key
    ## This is the 'base' of the currently used conda prompt
    ## Tested with miniconda and miniforge.
    ## Assume works for Anaconda.
    env_dir = os.environ['CONDA_PREFIX']

    conda_key = os.path.join(env_dir, 'Scripts', 'conda.exe')

    # Above doesn't work for ArcGIS conda installs
    ## Make sure conda exists, if not, change to CONDA
    if not os.path.exists(conda_key):
        conda_key = os.environ.get('CONDA_EXE', 'conda')

    print('conda_key:', conda_key)

    return conda_key

def install_housekeeping(conda_key):

    subprocess.run('''"{}" update -y conda'''.format(conda_key), shell=True)
    subprocess.run('''"{}" clean -y --all'''.format(conda_key), shell=True)
    subprocess.run('''python -m pip install --upgrade pip''', shell=True)

def conda_env_exists(conda_key, env_name):

    result = subprocess.run('''"{}" env list'''.format(conda_key), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    envs = result.stdout.splitlines()
    for env in envs:
        if re.search(rf'^{env_name}\s', env):
            return True
    return False
