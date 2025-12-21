import os, sys
import subprocess, re
import platform
import time

from pinginstaller.utils import (
    get_conda_key,
    get_mamba_or_conda,
    install_housekeeping,
    conda_env_exists,
    get_verbosity_flags,
)

home_path = os.path.expanduser('~')


def install(conda_key, yml, env_name='ping'):
    """
    Install a new conda environment from yml file.
    """
    try:
        # Install the ping environment from downloaded yml
        print(f"Creating '{env_name}' environment...")
        verbosity = get_verbosity_flags(conda_key)
        if verbosity:
            print(f"Verbosity enabled: {verbosity}")
        subprocess.run('''"{}" {} env create -y --file "{}"'''.format(conda_key, verbosity, yml), shell=True, check=True)

        # Install pysimplegui
        print("Installing PySimpleGUI...")
        subprocess.run([conda_key, 'run', '-n', env_name, 'pip', 'install', '--upgrade', '-i', 'https://PySimpleGUI.net/install', 'PySimpleGUI'], check=True)

        # List the environments
        subprocess.run('conda env list', shell=True)
        print(f"\n'{env_name}' environment created successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during installation: {e}")
        print("Please check the error messages above and try again.")
        raise
    
    return

def update(conda_key, yml, env_name='ping'):
    """
    Update an existing conda environment from yml file.
    """
    try:
        # Update the ping environment from downloaded yml
        print(f"Updating '{env_name}' environment...")
        verbosity = get_verbosity_flags(conda_key)
        if verbosity:
            print(f"Verbosity enabled: {verbosity}")
        subprocess.run('''"{}" {} env update --file "{}" --prune'''.format(conda_key, verbosity, yml), shell=True, check=True)

        # Install pysimplegui
        print("Updating PySimpleGUI...")
        subprocess.run([conda_key, 'run', '-n', env_name, 'pip', 'install', '--upgrade', '-i', 'https://PySimpleGUI.net/install', 'PySimpleGUI'], check=True)

        # List the environments
        subprocess.run('conda env list', shell=True)
        print(f"\n'{env_name}' environment updated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during update: {e}")
        print("Please check the error messages above and try again.")
        raise

    return

def update_pinginstaller():
    '''
    Called from PINGWizard prior to updating the environment
    '''
    print('Updating PINGInstaller...')

    try:
        # Get the conda key
        conda_key = get_conda_key()

        # Update pinginstaller
        subprocess.run([conda_key, 'run', '-n', 'base', 'pip', 'install', 'pinginstaller', '-U'], check=True)
        print('PINGInstaller updated successfully!')
        
    except subprocess.CalledProcessError as e:
        print(f'Warning: Failed to update PINGInstaller: {e}')
        print('Continuing anyway...')


def install_update(yml):
    """
    Main function to install or update conda environment from yml file.
    Automatically detects and uses mamba if available for faster installs.
    """
    subprocess.run('conda env list', shell=True)

    # Get the conda/mamba key (prefer mamba if available)
    conda_key = get_mamba_or_conda()

    ##############
    # Housekeeping
    install_housekeeping(conda_key)

    ##############
    # Download yml

    # Download yml if necessary
    del_yml = False
    if yml.startswith("https:") or yml.startswith("http:"):
        print("Downloading:", yml)

        # Make sure ?raw=true at end
        if not yml.endswith("?raw=true"):
            yml += "?raw=true"
        from pinginstaller.download_yml import get_yml
        yml = get_yml(yml)

        print("Downloaded yml:", yml)
        del_yml = True

    ######################
    # Get environment name
    with open(yml, 'r') as f:
        for line in f:
            if line.startswith('name:'):
                env_name = line.split('name:')[-1].strip()

    ######################################
    # Install or update `ping` environment and time it
    exists = conda_env_exists(conda_key, env_name)
    start = time.perf_counter()
    if exists:
        print(f"Updating '{env_name}' environment ...")
        update(conda_key, yml, env_name)
        op = 'update'
    else:
        print(f"Creating '{env_name}' environment...")
        install(conda_key, yml, env_name)
        op = 'install'

    elapsed = time.perf_counter() - start
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    print(f"\nTime to {op} environment '{env_name}': {mins}m {secs}s ({elapsed:.1f}s)")

    #########
    # Cleanup
    if del_yml:
        try:
            os.remove(yml)
        except Exception:
            pass

    #################
    # Create Shortcut
    if env_name == 'ping':
        try:
            if "Windows" in platform.system():
                ending = '.bat'
            else:
                ending = '.sh'
            shortcut = os.path.join(home_path, 'PINGWizard'+ending)
            print('\n\nCreating PINGWizard shortcut at: {}'.format(shortcut))

            subprocess.run('''"{}" run -n {} python -m pingwizard shortcut'''.format(conda_key, env_name), shell=True, check=True)

            print('\n\nShortcut created:', shortcut)
        except subprocess.CalledProcessError as e:
            print(f'\nWarning: Failed to create shortcut: {e}')
            print('You can create it manually later by running: python -m pingwizard shortcut')


def fix_ghostvision_cpu():
    '''
    Called from PINGWizard after installing or updating the environment
    '''
    print('Fixing ghostvision for CPU...')

    try:
        # Get the conda key
        conda_key = get_conda_key()

        subprocess.run([conda_key, 'install', '-n', 'ghostvision', '-y', 'numpy<2'], check=True)
        print('GhostVision CPU fix applied successfully!')
        
    except subprocess.CalledProcessError as e:
        print(f'Warning: Failed to fix ghostvision: {e}')
        print('You may need to manually install numpy<2 in the ghostvision environment')

    return



    