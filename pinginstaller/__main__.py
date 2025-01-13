
import os, sys

# Add 'pingwizard' to the path, may not need after pypi package...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PACKAGE_DIR)

# Get yml
if len(sys.argv) == 1:
    arg = "https://github.com/CameronBodine/PINGMapper/blob/main/pingmapper/conda/PINGMapper.yml"
else:
    arg = sys.argv[1]

def main(arg):

    if arg == 'check':
        from pinginstaller.check_available_updates import check
        check()
    else:
        print('Env yml:', arg)

        from pinginstaller.Install_Update_PINGMapper import install_update
        install_update(arg)

    return

if __name__ == '__main__':
    main(arg)