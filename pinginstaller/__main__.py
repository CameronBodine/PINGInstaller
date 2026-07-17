
import os, sys

# Add 'pinginstaller' to the path, may not need after pypi package...
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(PACKAGE_DIR)

"""
Support optional CLI flags:
    python -m pinginstaller [<yml_or_alias>] [mamba|conda] [-v|--verbose|-vv|-vvv|--debug]
Examples:
    python -m pinginstaller conda
    python -m pinginstaller ghostvision conda
This sets PINGINSTALLER_VERBOSITY for detailed solver output.
"""

# Default to highest verbosity unless overridden
if 'PINGINSTALLER_VERBOSITY' not in os.environ:
    os.environ['PINGINSTALLER_VERBOSITY'] = 'debug'

# Parse args: support verbosity anywhere, optional yml/alias, and optional solver
default_yml = "https://raw.githubusercontent.com/CameronBodine/PINGMapper/main/pingmapper/conda/PINGMapper.yml"
arg = None
solver = 'mamba'
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
    if t in ('mamba', 'conda'):
        solver = t
        continue
    # First non-verbosity token is treated as yml/alias
    if arg is None:
        arg = tok

if arg is None:
    arg = default_yml

def main(arg, solver='mamba'):

    if arg == 'check':
        from pinginstaller.check_available_updates import check
        check()

    elif arg == 'ghostvision-gpu':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/GhostVision/main/ghostvision/conda/ghostvision_install_gpu.yml'
        from pinginstaller.Install_Update import install_update

        install_update(yml, solver)
    elif arg == 'ghostvision':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/GhostVision/main/ghostvision/conda/ghostvision_install.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml, solver)

        from pinginstaller.Install_Update import fix_ghostvision_cpu
        fix_ghostvision_cpu()

    elif arg == 'fixghostvision':
        from pinginstaller.Install_Update import fix_ghostvision_cpu
        fix_ghostvision_cpu()

    elif arg == 'pingtile':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/PINGTile/main/pingtile/conda/pingtile.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml, solver)

    elif arg == 'rockmapper':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/RockMapper/main/rockmapper/conda/RockMapper.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml, solver)

    elif arg == 'rf_mapper':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/PINGSeg/main/pingseg/conda/rf_mapper.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml, solver)

    elif arg == 'monsturmapper':
        yml = 'https://raw.githubusercontent.com/PINGEcosystem/MonsturMapper/main/monsturmapper/conda/MonSturMapper.yml'
        from pinginstaller.Install_Update import install_update
        install_update(yml, solver)

    else:
        print('Env yml:', arg)

        from pinginstaller.Install_Update import install_update
        install_update(arg, solver)

    return

if __name__ == '__main__':
    main(arg, solver)