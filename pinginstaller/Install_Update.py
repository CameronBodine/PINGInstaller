import os, sys
import subprocess, re
import platform

from pinginstaller.utils import get_conda_key, install_housekeeping, conda_env_exists

home_path = os.path.expanduser('~')


def install(conda_key, yml, env_name='ping'):

    # Install the ping environment from downloaded yml
    subprocess.run('''"{}" env create -y --file "{}"'''.format(conda_key, yml), shell=True)

    # Install pysimplegui
    subprocess.run([conda_key, 'run', '-n', env_name, 'pip', 'install', '--upgrade', '-i', 'https://PySimpleGUI.net/install', 'PySimpleGUI'])

    # List the environments
    subprocess.run('conda env list', shell=True)

    return

def update(conda_key, yml, env_name='ping'):

    # Update the ping environment from downloaded yml
    subprocess.run('''"{}" env update --file "{}" --prune'''.format(conda_key, yml), shell=True)

    # Install pysimplegui
    subprocess.run([conda_key, 'run', '-n', env_name, 'pip', 'install', '--upgrade', '-i', 'https://PySimpleGUI.net/install', 'PySimpleGUI'])

    # List the environments
    subprocess.run('conda env list', shell=True)

    return

def update_pinginstaller():
    '''
    Called from PINGWizard prior to updating the environment
    '''
    print('Updating PINGInstaller...')

    # Get the conda key
    conda_key = get_conda_key()

    # Update pinginstaller
    # subprocess.run([conda_key, 'run', '-n', 'ping', 'pip', 'install', 'pinginstaller', '-U'])
    subprocess.run([conda_key, 'run', '-n', 'base', 'pip', 'install', 'pinginstaller', '-U'])


# def install_update(conda_base, conda_key):
def install_update(yml):

    subprocess.run('conda env list', shell=True)

    # Get the conda key
    conda_key = get_conda_key()

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
    # Install or update `ping` environment
    if conda_env_exists(conda_key, env_name):
        print(f"Updating '{env_name}' environment ...")
        # subprocess.run([os.path.join(directory, "Update.bat"), conda_base, conda_key, yml], shell=True)
        update(conda_key, yml, env_name)
        
    else:
        print(f"Creating '{env_name}' environment...")
        # subprocess.run([os.path.join(directory, "Install.bat"), conda_base, conda_key, yml], shell=True)
        install(conda_key, yml, env_name)

    #########
    # Cleanup
    if del_yml:
        os.remove(yml)

    #################
    # Create Shortcut
    if env_name == 'ping':
        if "Windows" in platform.system():
            ending = '.bat'
        else:
            ending = '.sh'
        shortcut = os.path.join(home_path, 'PINGWizard'+ending)
        print('\n\nCreating PINGWizard shortcut at: {}'.format(shortcut))

        subprocess.run('''"{}" run -n {} python -m pingwizard shortcut'''.format(conda_key, env_name), shell=True)

        print('\n\nShortcut created:', shortcut)


def fix_ghostvision_cpu():
    '''
    Called from PINGWizard after installing or updating the environment
    '''
    print('Fixing ghostvision for CPU...')

    # Get the conda key
    conda_key = get_conda_key()

    # # # Update ghostvision to CPU version
    # # subprocess.run([conda_key, 'run', '-n', 'ping', 'pip', 'install', 'ghostvision-cpu', '-U'])

    # # Uninstall pytorch etc
    # subprocess.run([conda_key, 'run', '-n', 'ghostvision', 'pip', 'uninstall', '-y', 'torch', 'torchvision'])

    # # Reinstall pytorch etc with conda
    # # subprocess.run([conda_key, 'install', '-n', 'ghostvision', 'pytorch', 'torchvision', 'torchaudio', 'cpuonly', '-c', 'pytorch', '-y'])
    # subprocess.run([conda_key, 'run', '-n', 'ghostvision', 'pip', 'install', 'torch<2.4', 'torchvision<0.19'])

    # # subprocess.run([conda_key, 'run', '-n', 'ghostvision', 'pip', 'install', 'tf-keras', '-U'])
    
    subprocess.run([conda_key, 'install', '-n', 'ghostvision', '-y', 'numpy<2'], check=True)

    return



    