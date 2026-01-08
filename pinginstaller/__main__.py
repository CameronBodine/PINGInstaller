
import os, sys

# Add 'pinginstaller' to the path, may not need after pypi package...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PACKAGE_DIR)

"""
Support an optional verbosity flag via CLI:
  python -m pinginstaller <yml_or_alias> [-v|--verbose|-vv|-vvv|--debug]
This sets PINGINSTALLER_VERBOSITY for detailed solver output.
"""

# Default to highest verbosity unless overridden
if 'PINGINSTALLER_VERBOSITY' not in os.environ:
    os.environ['PINGINSTALLER_VERBOSITY'] = 'debug'

# Parse args: support verbosity anywhere and optional yml/alias
default_yml = "https://raw.githubusercontent.com/CameronBodine/PINGMapper/main/pingmapper/conda/PINGMapper.yml"
arg = None
for tok in sys.argv[1:]:
    t = tok.strip().lower()
    if t in ('-v', '--verbose'):
        os.environ['PINGINSTALLER_VERBOSITY'] = 'v'
        continue
    if t in ('-vv',):
        os.environ['PINGINSTALLER_VERBOSITY'] = 'vv'
        continue
    if t in ('-vvv', '--debug'):
        os.environ['PINGINSTALLER_VERBOSITY'] = 'debug'
        continue
    if t in ('-q', '--quiet'):
        os.environ['PINGINSTALLER_VERBOSITY'] = 'quiet'
        continue
    # First non-verbosity token is treated as yml/alias
    if arg is None:
        arg = tok

if arg is None:
    arg = default_yml

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

    elif arg == 'rockmapper':
        yml = 'https://github.com/PINGEcosystem/RockMapper/blob/main/rockmapper/conda/RockMapper.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml)

    else:
        print('Env yml:', arg)

        from pinginstaller.Install_Update import install_update
        install_update(arg)

    return

if __name__ == '__main__':
    main(arg)