
import os
import subprocess
import re


def get_default_env_prefix(env_name: str) -> str:
    env_dir = os.environ.get('CONDA_PREFIX', '')
    if env_dir:
        base_dir = env_dir.split('envs')[0].rstrip(os.sep)
        if base_dir:
            return os.path.join(base_dir, 'envs', env_name)

    conda_exe = os.environ.get('CONDA_EXE', '')
    if conda_exe:
        scripts_dir = os.path.dirname(conda_exe)
        base_dir = os.path.dirname(scripts_dir)
        return os.path.join(base_dir, 'envs', env_name)

    return os.path.join('envs', env_name)

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

def configure_short_pkgs_dir():
    """
    Windows only, no admin needed. Point conda/mamba's package cache at a short
    path so extraction doesn't hit MAX_PATH (260 chars). The default cache
    nests packages under pkgs\\https\\conda.anaconda.org\\conda-forge\\win-64\\.
    Sets CONDA_PKGS_DIRS for this process and its subprocesses.
    """
    if os.name != 'nt':
        return None
    if os.environ.get('PINGINSTALLER_KEEP_PKGS_DIR'):
        return None

    drive = os.path.splitdrive(os.path.expanduser('~'))[0] or 'C:'
    candidates = [
        os.path.join(drive + os.sep, 'cpkgs'),
        os.path.join(os.path.expanduser('~'), '.cpkgs'),
    ]
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, '.write_test')
            with open(test, 'w') as f:
                f.write('x')
            os.remove(test)
        except OSError:
            continue
        os.environ['CONDA_PKGS_DIRS'] = path
        print(f'Using short package cache: {path}')
        return path
    print('Warning: could not create a short package cache directory.')
    return None

def warn_if_onedrive(*paths):
    """Warn when paths live in OneDrive, whose sync can lock files mid-install."""
    for p in paths:
        if p and 'onedrive' in os.path.abspath(p).lower():
            print(
                f'\nWarning: "{p}" is inside OneDrive. OneDrive sync can lock '
                'files and cause install/download failures. Pause syncing or '
                'use a folder outside OneDrive (e.g. C:\\PINGData).\n'
            )

def long_path(path: str) -> str:
    """Return a \\\\?\\ prefixed absolute path on Windows so Python file calls
    work beyond 260 chars without the LongPathsEnabled registry setting."""
    if os.name != 'nt':
        return path
    path = os.path.abspath(path)
    if path.startswith('\\\\?\\'):
        return path
    if path.startswith('\\\\'):
        return '\\\\?\\UNC\\' + path[2:]
    return '\\\\?\\' + path

def _force_rmtree(path: str, retries: int = 3):
    """Remove a directory tree, tolerating read-only files and transient locks."""
    import shutil, stat, time

    def _onerror(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    for _ in range(retries):
        if not os.path.exists(path):
            return True
        shutil.rmtree(path, onerror=_onerror)
        if not os.path.exists(path):
            return True
        time.sleep(2)

    # Last resort on Windows
    if os.name == 'nt' and os.path.exists(path):
        subprocess.run('rmdir /s /q "{}"'.format(path), shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return not os.path.exists(path)

def purge_package_cache(conda_key: str):
    """
    Delete the conda/mamba package cache (partially extracted packages left
    by a failed transaction). This is only a cache; packages are re-downloaded.
    """
    try:
        subprocess.run('''"{}" clean -y --all'''.format(conda_key), shell=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    bases = set()
    for var in ('CONDA_PREFIX', 'CONDA_EXE'):
        val = os.environ.get(var, '')
        if not val:
            continue
        if var == 'CONDA_PREFIX':
            bases.add(val.split('envs')[0].rstrip(os.sep))
        else:
            bases.add(os.path.dirname(os.path.dirname(val)))

    pkgs_dirs = [os.path.join(base, 'pkgs') for base in bases]
    if os.environ.get('CONDA_PKGS_DIRS'):
        pkgs_dirs.append(os.environ['CONDA_PKGS_DIRS'])

    for pkgs in pkgs_dirs:
        if not os.path.isdir(pkgs):
            continue
        for entry in os.listdir(pkgs):
            full = os.path.join(pkgs, entry)
            # Keep conda's own bookkeeping files; remove package folders
            if os.path.isdir(full) and entry != 'cache':
                if not _force_rmtree(long_path(full)):
                    print(f'Warning: could not fully remove {full}')
        _force_rmtree(long_path(os.path.join(pkgs, 'cache')))

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
    print(f"Debug: Looking for environment '{env_name}'")
    print(f"Debug: conda_key = {conda_key}")
    print(f"Debug: Found environments:")
    for env in envs:
        line = env.strip()
        print(f"  {line}")

        # Skip headers and separators
        if not line or line.startswith(('#', 'Name', '-')):
            continue

        # Split on whitespace; first token may be '*' for active env
        parts = line.split()
        # Example lines:
        # "base                 *   Z:\\miniforge3"
        # "ping                     Z:\\miniforge3\\envs\\ping"
        if not parts:
            continue

        # Remove active marker if present
        name_token = parts[0]
        if name_token == '*':
            if len(parts) >= 2:
                name_token = parts[1]
                path_token = parts[2] if len(parts) >= 3 else ''
            else:
                name_token = ''
                path_token = ''
        else:
            path_token = parts[-1] if len(parts) >= 2 else ''

        # Match by name or by path suffix
        if name_token == env_name:
            print("Debug: Found matching environment by name!")
            return True
        # Normalize separators for comparison
        env_suffix = os.sep + env_name
        if path_token.replace('/', os.sep).endswith(env_suffix):
            print("Debug: Found matching environment by path!")
            return True

    print(f"Debug: Environment '{env_name}' not found")
    return False
