
import os, sys

# Add 'pingwizard' to the path, may not need after pypi package...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PACKAGE_DIR)

# Get yml
if len(sys.argv) == 1:
    yml = "https://github.com/CameronBodine/PINGMapper/blob/dev_v4/pingmapper/conda/PINGMapper.yml"
else:
    yml = sys.argv[1]

def main(yml):

    print('Env yml:', yml)

    from pinginstaller.Install_Update_PINGMapper import install_update
    install_update(yml)

    return

if __name__ == '__main__':
    main(yml)