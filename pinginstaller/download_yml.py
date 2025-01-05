import os, sys
import tempfile
import urllib.request

def get_yml(url):

    # Get yml data from github
    with urllib.request.urlopen(url) as f:
        yml_data = f.read().decode('utf-8')

        # Make a temporary file
        with tempfile.TemporaryDirectory(delete=False) as tempdir:

            temp_file = os.path.join(tempdir, 'conda.yml')
            
            # Write yml data to temporary file
            with open(temp_file, 'w') as t:
                t.write(yml_data)        

    return temp_file