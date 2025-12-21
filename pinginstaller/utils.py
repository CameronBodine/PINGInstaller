
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

    # If in an environment, go back to base
    env_dir = env_dir.split('envs')[0].rstrip(os.sep)

    conda_key = os.path.join(env_dir, 'Scripts', 'conda.exe')

    # Above doesn't work for ArcGIS conda installs
    ## Make sure conda exists, if not, change to CONDA
    if not os.path.exists(conda_key):
        conda_key = os.environ.get('CONDA_EXE', 'conda')

    print('conda_key:', conda_key)

    return conda_key

def get_mamba_or_conda():
    """
    Detect if mamba is available and return the appropriate command.
    Mamba is preferred over conda for faster environment solving.
    Checks: 1) mamba command in PATH, 2) mamba.bat in condabin, 3) mamba.exe in Scripts, 4) fallback to conda
    """
    # Try mamba command directly first (should work if in PATH)
    try:
        result = subprocess.run(['mamba', '--version'], capture_output=True, text=True, timeout=2, shell=False)
        if result.returncode == 0:
            print('Using mamba for faster installation')
            return 'mamba'
    except Exception:
        pass
    
    # Try mamba.bat from condabin (common in miniforge/minicondan)
    env_dir = os.environ.get('CONDA_PREFIX', '')
    if env_dir:
        base_dir = env_dir.split('envs')[0].rstrip(os.sep)
        mamba_bat = os.path.join(base_dir, 'condabin', 'mamba.bat')
        if os.path.exists(mamba_bat):
            print('Using mamba for faster installation')
            return mamba_bat
    
    # Try to find mamba.exe in Scripts
    if env_dir:
        base_dir = env_dir.split('envs')[0].rstrip(os.sep)
        mamba_key = os.path.join(base_dir, 'Scripts', 'mamba.exe')
        if os.path.exists(mamba_key):
            print('Using mamba for faster installation')
            return mamba_key
    
    # Fall back to conda
    return get_conda_key()

def install_housekeeping(conda_key):
    """
    Update conda/mamba and clean package cache.
    """
    try:
        print('Updating conda/mamba...')
        subprocess.run('''"{}" update -y --all'''.format(conda_key), shell=True, check=True)
        print('Cleaning package cache...')
        subprocess.run('''"{}" clean -y --all'''.format(conda_key), shell=True, check=True)
        print('Upgrading pip...')
        subprocess.run('''python -m pip install --upgrade pip''', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Warning: Housekeeping step failed: {e}')
        print('Continuing with installation...')

def _is_mamba_key(conda_key: str) -> bool:
    name = os.path.basename(str(conda_key)).lower()
    return 'mamba' in name

def get_verbosity_flags(conda_key: str) -> str:
    """
    Return appropriate verbosity flags for mamba/conda based on
    PINGINSTALLER_VERBOSITY env var. Defaults to highest verbosity.

    Supported values:
    - "v", "verbose" -> minimal verbosity
    - "vv" -> medium verbosity
    - "vvv", "debug" -> maximum verbosity
    - "quiet", "q" -> no extra verbosity
    Default: "" (no extra verbosity)
    """
    lvl = os.environ.get('PINGINSTALLER_VERBOSITY', '').strip().lower()

    # Default to highest verbosity unless explicitly quiet
    if not lvl:
        lvl = 'debug'
    if lvl in ('quiet', 'q'):
        return ''

    is_mamba = _is_mamba_key(conda_key)

    if lvl in ('debug', 'vvv'):
        # mamba supports --debug, conda uses -vvv
        return '--debug' if is_mamba else '-vvv'
    if lvl in ('vv',):
        return '-vv'
    if lvl in ('v', 'verbose'):
        return '-v'

    # Fallback to a single -v if an unknown non-empty value was provided
    return '-v'

def conda_env_exists(conda_key, env_name):

    result = subprocess.run('''"{}" env list'''.format(conda_key), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    envs = result.stdout.splitlines()
    for env in envs:
        if re.search(rf'^{env_name}\s', env):
            return True
    return False
