
from setuptools import setup, find_packages
from pathlib import Path

DESCRIPTION = 'Light-weight interface for running PING ecosystem (PINGMapper, etc.)'
LONG_DESCRIPTION = Path('README.md').read_text()

exec(open('pinginstaller/version.py').read())

setup(
    name="pinginstaller",
    version=__version__,
    author="Cameron Bodine",
    author_email="bodine.cs@gmail.email",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    # data_files=[("pingmapper_config", ["pinginstaller/PINGMapper.yml"])],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Oceanography",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Hydrology"
        ],
    keywords=[
        "pingmapper",
        "sonar",
        "ecology",
        "remotesensing",
        "sidescan",
        "sidescan-sonar",
        "aquatic",
        "humminbird",
        "lowrance",
        "gis",
        "oceanography",
        "limnology",],
    python_requires=">3",
    install_requires=[],
    project_urls={
        "Issues": "https://github.com/CameronBodine/PINGInstaller/issues",
        "GitHub":"https://github.com/CameronBodine/PINGInstaller",
        "Homepage":"https://cameronbodine.github.io/PINGMapper/",
    },
)