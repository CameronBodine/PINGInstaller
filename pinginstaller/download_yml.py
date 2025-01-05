import os, sys
import urllib.request

from pathlib import Path
home_path = os.path.join(Path.home())

def get_yml(url):

    # Get yml data from github
    with urllib.request.urlopen(url) as f:
        yml_data = f.read().decode('utf-8')

        # Make a temporary file
        temp_file = os.path.join(home_path, 'pinginstaller_conda_file.yml')
        
        # Write yml data to temporary file
        with open(temp_file, 'w') as t:
            t.write(yml_data)

    return temp_file