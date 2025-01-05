
import os, sys

# Add 'pingwizard' to the path, may not need after pypi package...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PACKAGE_DIR)

env_dir = os.environ['CONDA_PREFIX']
pingmapper_yml_name = "PINGMapper.yml"
yml = os.path.join(env_dir, 'pingmapper_config', pingmapper_yml_name)

print('Env yml:', yml)

def main(yml):

    from pinginstaller.Install_Update_PINGMapper import install_update
    install_update(yml)

    return

if __name__ == '__main__':
    main(yml)