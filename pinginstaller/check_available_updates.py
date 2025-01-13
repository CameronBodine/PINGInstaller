

import subprocess
import sys
import json
import requests

def check():

    # Check if connected to the internet
    
    url = "https://www.google.com"
    try:
        response = requests.get(url)
        response = response.status_code
    except:
        response = 0

    if response == 200:

        latest_pip = (subprocess.run([sys.executable, '-m', 'pip', 'list', '-o', '--format=json'], capture_output=True, text=True)).stdout
        latest_pip = json.loads(latest_pip)

        ping_packages = []
        for i in latest_pip:
            if 'ping' in i['name']:
                ping_packages.append(i)

        if len(ping_packages) > 0:

            print('\n\n\n', 'UPDATES AVAILABLE')
            print("____________________________________________________________________")
            print("{:<20s} | {:<20s} | {:<20s} |".format("Package", "Version", "Latest Version"))
            print("____________________________________________________________________")
            for i in ping_packages:
                package = i['name']
                version = i['version']
                latest_version = i['latest_version']

                print("{:<20s} | {:<20s} | {:<20s} |".format(str(package), str(version), str(latest_version)))

            print('\n\nPLEASE UPDATE!\n\n')

        else:
            print('\n\nNO UPDATES AVAILABLE!\n\n')

    else:
        print('\n\nNO INTERNET CONNECTION! Unable to check for updates...\n\n')