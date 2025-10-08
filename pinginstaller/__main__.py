
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

    elif arg == 'ghostvision-gpu':
        yml = 'https://github.com/PINGEcosystem/GhostVision/blob/main/ghostvision/conda/ghostvision_install_gpu.yml'
        from pinginstaller.Install_Update import install_update

        install_update(yml)
    elif arg == 'ghostvision':
        yml = 'https://github.com/PINGEcosystem/GhostVision/blob/main/ghostvision/conda/ghostvision_install.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml)

        from pinginstaller.Install_Update import fix_ghostvision_cpu
        fix_ghostvision_cpu()

    elif arg == 'fixghostvision':
        from pinginstaller.Install_Update import fix_ghostvision_cpu
        fix_ghostvision_cpu()

    elif arg == 'pingtile':
        yml = 'https://github.com/PINGEcosystem/PINGTile/blob/main/pingtile/conda/pingtile.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml)

    else:
        print('Env yml:', arg)

        from pinginstaller.Install_Update import install_update
        install_update(arg)

    return

if __name__ == '__main__':
    main(arg)