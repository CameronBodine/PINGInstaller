# How PINGInstaller Works

## Overview

PINGInstaller is a lightweight conda environment installer designed for the PING ecosystem. It automatically detects the active conda installation (Miniforge, Miniconda, Anaconda, ArcGIS Python), provides optional verbosity control for detailed solver feedback including a quiet mode, and measures installation duration.

## Architecture

```
__main__.py           Entry point, CLI parsing
    ↓
main(arg)            Route to specific installer or generic install_update()
    ↓
install_update(yml)  Main orchestration function
    ↓
install() / update() Environment creation/update
    ↓
utils.py            Helper functions (conda detection, mamba detection, etc.)
```

## Detailed Workflow

### 1. Entry Point: `__main__.py`

**Purpose**: Parse command-line arguments and set verbosity level

**Sequence**:
```python
# Parse CLI arguments
for tok in sys.argv[1:]:
    - Check for verbosity flags: -v, -vv, -vvv, --debug
    - Set PINGINSTALLER_VERBOSITY environment variable
    - Capture yml path or alias

# Route to appropriate handler
main(arg)
```

**Key Functions**:
- Sets `PINGINSTALLER_VERBOSITY` env var for downstream functions
- Supports special aliases: 'check', 'ghostvision', 'ghostvision-gpu', 'pingtile', 'rockmapper'
- Defaults to highest verbosity (`debug`) unless `-q/--quiet` is provided
- Defaults to PINGMapper yml if no argument provided

---

### 2. Main Router: `main(arg)` in `__main__.py`

**Purpose**: Route to specific installer based on argument

**Sequence**:
```python
if arg == 'check':
    check_available_updates.check()
elif arg == 'ghostvision-gpu':
    install_update(ghostvision_gpu_yml)
elif arg == 'ghostvision':
    install_update(ghostvision_yml)
    fix_ghostvision_cpu()
# ... other special cases ...
else:
    install_update(arg)  # Generic yml or URL
```

**Key Decisions**:
- Special aliases trigger predefined yml URLs
- Generic arguments treated as yml paths or URLs
- Some aliases include post-install fixes (e.g., ghostvision CPU)

---

### 3. Main Orchestrator: `install_update(yml)` in `Install_Update.py`

**Purpose**: Coordinate the entire installation/update process

**Sequence**:

#### Step 1: Environment Discovery
```python
subprocess.run('conda env list', shell=True)
conda_key = get_mamba_or_conda()  # Prefer mamba for speed
```

#### Step 2: Housekeeping
```python
install_housekeeping(conda_key)
```
- Updates conda/mamba and all packages
- Cleans package cache
- Upgrades pip
- Handles errors gracefully (continues on failure)

#### Step 3: Download YML (if URL)
```python
if yml.startswith("https:") or yml.startswith("http:"):
    yml += "?raw=true" if not yml.endswith("?raw=true")
    yml = get_yml(yml)  # Download to temp file
    del_yml = True
```

#### Step 4: Parse Environment Name
```python
with open(yml, 'r') as f:
    for line in f:
        if line.startswith('name:'):
            env_name = line.split('name:')[-1].strip()
```

#### Step 5: Install or Update (Timed)
```python
exists = conda_env_exists(conda_key, env_name)
start = time.perf_counter()

if exists:
    update(conda_key, yml, env_name)
    op = 'update'
else:
    install(conda_key, yml, env_name)
    op = 'install'

elapsed = time.perf_counter() - start
print(f"Time to {op} environment: {mins}m {secs}s ({elapsed:.1f}s)")
```

#### Step 7: Cleanup
```python
if del_yml:
    os.remove(yml)           # Remove downloaded yml
```

#### Step 8: Create Shortcut (ping environment only)
```python
if env_name == 'ping':
    if Windows:
        shortcut = ~/PINGWizard.bat
    else:
        shortcut = ~/PINGWizard.sh
    
    conda_key run -n ping python -m pingwizard shortcut
```

---

### 4. Environment Creation: `install(conda_key, yml, env_name)` in `Install_Update.py`

**Purpose**: Create new conda environment from yml

**Sequence**:

#### Step 1: Create Conda Environment
```python
verbosity = get_verbosity_flags(conda_key)
if verbosity:
    print(f"Verbosity enabled: {verbosity}")

subprocess.run(f'"{conda_key}" {verbosity} env create -y --file "{yml}"')
```
**Key**: Uses full yml with conda and pip dependencies together for faster solving with constrained versions

#### Step 2: Install PySimpleGUI
```python
print("Installing PySimpleGUI...")
subprocess.run([conda_key, 'run', '-n', env_name, 'pip', 'install', '--upgrade', 
                '-i', 'https://PySimpleGUI.net/install', 'PySimpleGUI'])
```
**Special**: Uses PySimpleGUI's private index

#### Step 3: Confirm Success
```python
subprocess.run('conda env list', shell=True)
print(f"\n'{env_name}' environment created successfully!")
```

**Error Handling**:
- All subprocess calls use `check=True`
- Exceptions caught and re-raised with helpful context
- User directed to check error messages

---

### 5. Environment Update: `update(conda_key, yml, env_name)` in `Install_Update.py`

**Purpose**: Update existing conda environment

**Sequence**: Same as `install()` but:
- Uses `env update --prune` instead of `env create`
- Otherwise identical pip handling

---

## Utility Functions in `utils.py`

### `get_conda_key()`
**Purpose**: Find conda executable path

**Logic**:
```python
env_dir = os.environ['CONDA_PREFIX']
env_dir = env_dir.split('envs')[0]  # Get base, not env
conda_key = os.path.join(env_dir, 'Scripts', 'conda.exe')

if not os.path.exists(conda_key):
    conda_key = os.environ.get('CONDA_EXE', 'conda')  # Fallback for ArcGIS
```

**Returns**: Absolute path to conda.exe or 'conda' command

---

### `get_mamba_or_conda()`
**Purpose**: Prefer mamba over conda for speed

**Logic** (checks in order):
```python
# 1. Try mamba command in PATH
try:
    subprocess.run(['mamba', '--version'], timeout=2)
    return 'mamba'
except:
    pass

# 2. Check for mamba.bat in condabin (miniforge/miniconda)
env_dir = os.environ.get('CONDA_PREFIX', '')
base_dir = env_dir.split('envs')[0].rstrip(os.sep)
mamba_bat = os.path.join(base_dir, 'condabin', 'mamba.bat')
if os.path.exists(mamba_bat):
    return mamba_bat

# 3. Check for mamba.exe in Scripts
mamba_exe = os.path.join(base_dir, 'Scripts', 'mamba.exe')
if os.path.exists(mamba_exe):
    return mamba_exe

# 4. Fallback to conda
return get_conda_key()
```

**Returns**: Path to mamba (command, batch, or exe) or conda executable

**Why multiple checks?**: Different conda distributions place mamba in different locations. Miniforge uses `condabin/mamba.bat`, while other installs may use `Scripts/mamba.exe`.

---

### `get_verbosity_flags(conda_key)`
**Purpose**: Map verbosity level to appropriate flags for conda/mamba

**Logic**:
```python
lvl = os.environ.get('PINGINSTALLER_VERBOSITY', '').strip().lower()

# Default to highest verbosity unless explicitly quiet
if not lvl:
    lvl = 'debug'
if lvl in ('quiet', 'q'):
    return ''

is_mamba = 'mamba' in os.path.basename(conda_key).lower()

if lvl in ('debug', 'vvv'):
    return '--debug' if is_mamba else '-vvv'
if lvl in ('vv',):
    return '-vv'
if lvl in ('v', 'verbose'):
    return '-v'

# Fallback to a single -v if unknown non-empty value
return '-v'
```

**Returns**: Verbosity flag string (or empty string)

**Supported Values**:
- `v`, `verbose` → minimal verbosity
- `vv` → medium verbosity
- `vvv`, `debug` → maximum verbosity
- `quiet`, `q` → no extra verbosity

---

### `install_housekeeping(conda_key)`
**Purpose**: Update conda/mamba and clean cache before install

**Logic**:
```python
try:
    subprocess.run(f'"{conda_key}" update -y --all')
    subprocess.run(f'"{conda_key}" clean -y --all')
    subprocess.run('python -m pip install --upgrade pip')
except CalledProcessError as e:
    print(f'Warning: Housekeeping failed: {e}')
    print('Continuing with installation...')
```

**Error Handling**: Non-fatal - continues even if housekeeping fails

---

### `conda_env_exists(conda_key, env_name)`
**Purpose**: Check if environment already exists

**Logic**:
```python
result = subprocess.run(f'"{conda_key}" env list', capture_output=True)
envs = result.stdout.splitlines()

for env in envs:
    if re.search(rf'^{env_name}\s', env):
        return True
return False
```

**Returns**: Boolean

---

## Key Optimizations

### 1. Mamba Detection
**Problem**: Conda solver is slow

**Solution**:
- Automatically detect and use mamba if available
- Mamba's libsolv-based solver is 10-50x faster than classic conda
- Graceful fallback to conda if mamba not found

### 2. Version Constraints
**Problem**: Unconstrained versions lead to long solves

**Solution**:
- Pin Python to specific minor version (3.12)
- Add pragmatic upper bounds to geospatial packages
- Allow patch-level updates within constraints
- Example: `gdal>=3.8,<3.9`, `numpy<2`

### 3. Verbosity Control
**Problem**: Long solves with no feedback leave users uncertain

**Solution**:
- Optional `-v`, `-vv`, `--debug` flags
- Shows solver progress and decisions
- Maps to appropriate flags for conda vs mamba

### 4. Installation Timing
**Problem**: Users don't know if solve is progressing or stuck

**Solution**:
- Use `time.perf_counter()` to measure duration
- Display formatted time: "12m 34s (754.3s)"
- Helps users gauge if performance is normal

---

## Execution Flow Summary

```
User runs: python -m pinginstaller <yml> --debug
    ↓
__main__.py parses args, sets PINGINSTALLER_VERBOSITY=debug
    ↓
main(arg) routes to install_update(yml)
    ↓
install_update() orchestrates:
    1. get_mamba_or_conda() → mamba.exe
    2. install_housekeeping() → update, clean, pip upgrade
    3. Download yml if URL
    4. Parse env name from yml
    5. conda_env_exists() → False (new install)
    6. start timer
    7. install(mamba.exe, yml, 'ping'):
        a. get_verbosity_flags() → '--debug'
        b. mamba --debug env create -y --file yml
        c. mamba run -n ping pip install PySimpleGUI
    8. end timer, print duration
    9. Clean up downloaded yml if needed
    10. Create PINGWizard shortcut
    ↓
Success! Environment ready
```

---

## Error Handling Strategy

### Fatal Errors (raise exception):
- Environment creation/update fails
- Pip package installation fails
- PySimpleGUI installation fails

### Non-Fatal Errors (warn and continue):
- Housekeeping update fails
- YML parsing issues (fallback to original yml)
- Shortcut creation fails
- Temporary file cleanup fails

### User Guidance:
- Clear error messages with context
- Suggests next steps on failure
- Points to log output for debugging

---

## Command-Line Interface

### Basic Usage
```bash
python -m pinginstaller                    # Use default PINGMapper yml
python -m pinginstaller <path/to/env.yml>  # Use local yml
python -m pinginstaller <github-url>       # Download and use yml
```

### Verbosity Options
By default, if no verbosity flag is provided, PINGInstaller runs with maximum verbosity (`debug`). Use `-q/--quiet` to suppress extra solver output.
```bash
python -m pinginstaller -v                 # Minimal verbosity
python -m pinginstaller -vv                # Medium verbosity
python -m pinginstaller --debug            # Maximum verbosity (mamba --debug)
python -m pinginstaller -q                 # Quiet (no extra verbosity)
```

---

## Wizard Integration

When triggered from PINGWizard’s Update action, the wizard first attempts to update `pinginstaller` in the base environment via `update_pinginstaller()` to ensure the latest installer is used, then runs the environment update for the main `ping` environment. This prevents nested environments and keeps the installer current.

### Special Aliases
```bash
python -m pinginstaller check              # Check for updates
python -m pinginstaller ghostvision        # Install GhostVision CPU
python -m pinginstaller ghostvision-gpu    # Install GhostVision GPU
python -m pinginstaller pingtile           # Install PINGTile
python -m pinginstaller rockmapper         # Install RockMapper
```

---

## Future Enhancements

### Potential Improvements
1. **Conda-lock support**: Generate and use lock files for deterministic installs
2. **Parallel pip installs**: Use `pip install --no-deps` with dependency pre-resolution
3. **Progress indicators**: Show % complete during solve
4. **Rollback on failure**: Restore previous environment state if install fails
5. **Config file**: Allow users to set default verbosity, timeout, etc.
6. **Quiet mode**: Suppress non-essential output with `--quiet` flag
7. **Timeout guard**: Warn user if solve exceeds N minutes (suggest conda-lock approach)

---

## Dependencies

### Runtime Requirements
- Python 3.6+ (in base environment)
- conda or mamba installed
- Internet connection (for downloading ymls and packages)

### No External Python Packages
- Uses only Python stdlib: `os`, `sys`, `subprocess`, `re`, `time`, `platform`
- Keeps base environment clean and portable

---

## Platform Support

### Tested Platforms
- **Windows**: Miniforge3, Miniconda3, Anaconda, ArcGIS Python
- **Linux/macOS**: Should work (uses os.path abstractions)

### Platform-Specific Code
- Conda executable detection (Scripts/conda.exe on Windows)
- Shortcut creation (.bat on Windows, .sh on Unix)
- Path handling (uses os.path.join, os.sep)

---

## Performance Metrics

### Typical Solve Times (with optimizations)
- **Mamba + constrained versions**: 2-5 minutes
- **Conda + constrained versions**: 10-20 minutes
- **Old approach (unconstrained)**: 60-120 minutes

### Breakdown
- Housekeeping: 1-2 minutes
- Conda/mamba solve: 1-3 minutes (with constraints)
- Package download + extract: 2-5 minutes
- PySimpleGUI install: 30 seconds
- Total: 4-10 minutes (typical with mamba)

---

## Troubleshooting

### Slow Solves
1. Check verbosity to see what's being evaluated
2. Ensure mamba is being used (see "Using mamba" message)
3. Consider tightening version constraints in yml
4. Use conda-lock for deterministic installs

### Import Errors
1. Ensure all functions are at module scope (not nested)
2. Check for circular imports
3. Verify utils.py exports all needed functions

### Dependency Conflicts
1. Check pip install order (yml packages before PySimpleGUI)
2. Review version constraints in yml
3. Try `--debug` to see detailed dependency resolution

### Environment Already Exists
- Use `conda env remove -n <name>` to delete first
- Or let update() handle incremental updates

---

## Version History

### Current (December 2025)
- Simplified to single-pass install with conda and pip together
- Verified that version constraints (not yml splitting) are key to performance
- Mamba + constrained versions: 3-5 minute solves
- Removed unnecessary `split_conda_pip_yml()` function
- Added verbosity control (`-v`, `-vv`, `--debug`)
- Added installation timing
- Improved error handling with check=True

### Previous Approach (reverted)
- Attempted conda/pip separation to speed solves
- Tested and worked, but added complexity
- Version constraints alone proved sufficient
