import os, sys
import subprocess, re

def install_housekeeping():
    conda_key = os.environ.get('CONDA_EXE', 'conda')
    print(f"conda_key: {conda_key}")

    subprocess.run('''"{}" update -y conda'''.format(conda_key), shell=True)
    subprocess.run('''"{}" clean -y --all'''.format(conda_key), shell=True)
    subprocess.run('''python -m pip install --upgrade pip''', shell=True)

def conda_env_exists(env_name):
    conda_key = os.environ.get('CONDA_EXE', 'conda')
    print(f"conda_key: {conda_key}")

    result = subprocess.run('''"{}" env list'''.format(conda_key), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    envs = result.stdout.splitlines()
    for env in envs:
        if re.search(rf'^{env_name}\s', env):
            return True
    return False

def install(yml):
    conda_key = os.environ.get('CONDA_EXE', 'conda')
    print(f"conda_key: {conda_key}")

    subprocess.run('''"{}" env create --file {}'''.format(conda_key, yml), shell=True)

    subprocess.run('conda env list', shell=True)

    return

def update(yml):
    conda_key = os.environ.get('CONDA_EXE', 'conda')
    print(f"conda_key: {conda_key}")

    subprocess.run('''"{}" env update --file {}'''.format(conda_key, yml), shell=True)

    subprocess.run('conda env list', shell=True)

    return


# def install_update(conda_base, conda_key):
def install_update(yml):

    env_name = 'ping'

    subprocess.run('conda env list', shell=True)

    install_housekeeping()

    if conda_env_exists(env_name):
        print(f"Updating '{env_name}' environment ...")
        # subprocess.run([os.path.join(directory, "Update.bat"), conda_base, conda_key, yml], shell=True)
        update(yml)
        
    else:
        print(f"Creating '{env_name}' environment...")
        # subprocess.run([os.path.join(directory, "Install.bat"), conda_base, conda_key, yml], shell=True)
        install(yml)

    