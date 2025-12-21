# PINGInstaller

[![PyPI - Version](https://img.shields.io/pypi/v/pinginstaller?style=flat-square&label=Latest%20Version%20(PyPi))](https://pypi.org/project/pinginstaller/)

Light-weight application for installing [PINGMapper](https://github.com/CameronBodine/PINGMapper) and associated packages. `PINGInstaller` is designed to install a `conda` environment from a yml specified as a URL or localy hosted yml.

Example yml file structure:

```bash
name: ping
channels:
  - conda-forge
dependencies:
  - python<3.13
  - gdal
  - numpy
  - git
  - pandas
  - geopandas
  - pyproj<3.7.1
  - scikit-image
  - joblib
  - matplotlib
  - rasterio
  - h5py
  - opencv
  - pip
  - pip:
      - pingverter
      - pingmapper
      - pingwizard
      - pinginstaller
      - doodleverse_utils
      - psutil
      - tensorflow
      - tf-keras
      - transformers
      - rsa
```

The special thing about `PINGInstaller` is that it will install the `conda` environment based on the `conda` prompt it is launched from. This enables end-users with multiple `conda` installations to choose the flavor of `conda` as needed. 

Supported prompts include (but may not be limited to):

- [Miniforge](https://conda-forge.org/download/)
- [Miniconda](https://docs.anaconda.com/miniconda/install/)
- [Anaconda](https://www.anaconda.com/download)
- [ArcGIS Python Command Prompt](https://pro.arcgis.com/en/pro-app/3.3/arcpy/get-started/installing-python-for-arcgis-pro.htm)

`PINGInstaller` is also compatible with projects in the [Doodlevers](https://github.com/settings/organizations).

## Installation & Usage

### Step 1

Open (download, if not already available) the `conda` prompt you want to use (ex: On Windows 11 - Start --> All --> Anaconda (miniconda3) --> Anaconda Powershell Prompt).

### Step 2

Install `PINGInstaller` in the `base` environment with:

```bash
pip install pinginstaller
```

### Step 3

Then install the environment from a web or locally hosted yml with:

```bash
python -m pinginstaller https://github.com/CameronBodine/PINGMapper/blob/main/conda/PINGMapper.yml
```

That's it! Your environment is now ready to use.

If you want to update the environment, simply re-run the environment installation script with:

```bash
python -m pinginstaller https://github.com/CameronBodine/PINGMapper/blob/main/conda/PINGMapper.yml
```

Ta-ta for now!

## Troubleshooting

### "Access is denied" When Updating from Wizard

**Problem**: When updating via PINGWizard, you see:
```
remove_all: Access is denied.
```

**Cause**: In rare cases, file locking can prevent updates when the wizard is running from the environment being updated.

**Solution**: PINGWizard (v1.0.12+) automatically runs updates from the base environment to avoid this. If you still see this error:
1. Update PINGWizard: `pip install pingwizard -U`
2. Or manually run from base: `conda activate base && python -m pingwizard`

### "Non-conda folder exists at prefix" Error

**Problem**: When creating an environment, you see:
```
error    libmamba Non-conda folder exists at prefix - aborting.
critical libmamba Non-conda folder exists at prefix - aborting.
```

**Cause**: A leftover directory exists at the environment location (e.g., `Z:\miniforge3\envs\ping`) that's not a valid conda environment. This can happen after an incomplete removal or failed installation.

**Solution**: Manually remove the directory and try again:
```powershell
# Windows PowerShell
Remove-Item -Recurse -Force "Z:\miniforge3\envs\ping"

# Then retry installation
python -m pinginstaller
```

```bash
# Linux/Mac
rm -rf ~/miniforge3/envs/ping

# Then retry installation
python -m pinginstaller
```

### Slow Environment Solving

**Problem**: Environment creation takes a very long time (>10 minutes).

**Solutions**:
1. **Use mamba** (much faster): Install mamba in your base environment:
   ```bash
   conda install -n base mamba -y
   ```
   PINGInstaller automatically detects and uses mamba when available.

2. **Check your network connection**: Slow downloads can cause delays.

3. **Clear conda cache**:
   ```bash
   conda clean --all -y
   ```

### "Package Not Found" or Solver Errors

**Problem**: Conda/mamba cannot find required packages or conflicts prevent solving.

**Solutions**:
1. **Update conda/mamba**:
   ```bash
   conda update -n base conda -y
   # or if using mamba
   mamba update -n base mamba -y
   ```

2. **Check channel configuration**: Ensure conda-forge is available:
   ```bash
   conda config --show channels
   # Should include conda-forge
   ```

3. **Update all packages in base**:
   ```bash
   conda update --all -y
   ```

### Installation Hangs During Housekeeping

**Problem**: Installation appears stuck during the "Updating conda/mamba" step.

**Solution**: Press `Ctrl+C` to cancel, then run with quiet mode to skip housekeeping updates:
```bash
python -m pinginstaller <yml_url> -q
```

Or skip housekeeping by commenting out the `install_housekeeping()` call temporarily.

### Wrong Conda Installation Being Used

**Problem**: PINGInstaller is using a different conda installation than expected.

**Solution**:
1. **Verify which conda is active**:
   ```bash
   which conda  # Linux/Mac
   where conda  # Windows
   ```

2. **Check CONDA_PREFIX**:
   ```bash
   echo $CONDA_PREFIX  # Linux/Mac/PowerShell
   echo %CONDA_PREFIX%  # Windows CMD
   ```

3. **Activate the correct conda first**, then run pinginstaller from that environment.

### Mamba Not Being Detected

**Problem**: PINGInstaller uses conda even though mamba is installed.

**Solution**:
1. **Verify mamba is in base environment**:
   ```bash
   conda activate base
   mamba --version
   ```

2. **Reinstall mamba if needed**:
   ```bash
   conda install -n base mamba -y
   ```

3. **Check output**: PINGInstaller will print "Using mamba for faster installation" if detected.

### Permission Denied Errors

**Problem**: Cannot write to conda directories.

**Solutions**:
- **Windows**: Run PowerShell or Command Prompt as Administrator
- **Linux/Mac**: Check directory ownership, or reinstall conda in user directory (not system-wide)

### Import Errors After Installation

**Problem**: Packages installed but cannot be imported.

**Solutions**:
1. **Activate the environment first**:
   ```bash
   conda activate ping
   python -c "import pingmapper"
   ```

2. **Verify environment location**:
   ```bash
   conda env list
   # Ensure 'ping' environment is listed
   ```

3. **Check package installation**:
   ```bash
   conda list | grep pingmapper
   ```

## Getting Help

If you encounter issues not covered here:
1. Check the [GitHub Issues](https://github.com/CameronBodine/PINGInstaller/issues)
2. Enable debug mode for detailed output: `python -m pinginstaller <yml> --debug`
3. Open a new issue with the full error output and your system details
