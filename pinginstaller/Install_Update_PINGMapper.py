import os, sys
import subprocess, re
import platform

from pathlib import Path
home_path = os.path.join(Path.home())

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

def install(conda_key, yml):

    subprocess.run('''"{}" env create --file "{}"'''.format(conda_key, yml), shell=True)

    subprocess.run('conda env list', shell=True)

    return

def update(conda_key, yml):

    subprocess.run('''"{}" env update --file "{}" --prune'''.format(conda_key, yml), shell=True)

    subprocess.run('conda env list', shell=True)

    return


# def install_update(conda_base, conda_key):
def install_update(yml):

    subprocess.run('conda env list', shell=True)

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
        update(conda_key, yml)
        
    else:
        print(f"Creating '{env_name}' environment...")
        # subprocess.run([os.path.join(directory, "Install.bat"), conda_base, conda_key, yml], shell=True)
        install(conda_key, yml)

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
        shortcut = os.path.join(home_path, 'Desktop', 'PINGWizard'+ending)
        print('\n\nCreating PINGWizard shortcut at: {}'.format(shortcut))

        subprocess.run('''"{}" run -n {} python -m pingwizard shortcut'''.format(conda_key, env_name), shell=True)



    