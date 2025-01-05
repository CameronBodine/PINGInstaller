# PINGInstaller

[![PyPI - Version](https://img.shields.io/pypi/v/pinginstaller?style=flat-square&label=Latest%20Version%20(PyPi))](https://pypi.org/project/pinginstaller/)

Light-weight application for installing [PINGMapper](https://github.com/CameronBodine/PINGMapper) and associated packages. `PINGInstaller` is designed to install a `conda` environment from a yml specified as a URL or localy hosted yml.

Example yml file structure:

```bash
name: ping
channels:
  - conda-forge
  - defaults
dependencies:
  - python < 3.13
  - gdal
  - numpy
  - git
  - pandas
  - geopandas
  - pyproj
  - scikit-image
  - joblib
  - matplotlib
  - rasterio
  - h5py
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
      - pysimplegui == 5.0.*
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

