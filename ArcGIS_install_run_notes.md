
Installing and running PINGMapper using
Python bundled with ArcGIS
---------------------------------------

Go to "Start" > "All" > "ArcGIS" > "Python Command Prompt"

Then run the commands below in the prompt.

1) `pip install pinginstaller`
2) `python -m pinginstaller`

There will be an error that says:
ERROR conda.cli.main_run:execute(125): `conda run python -m pingwizard shortcut` failed. (See above for error)

That's ok, proceeding...

3) `activate ping`

Installation of PySimpleGUI likely unsuccessful, so:

4) `pip install --upgrade -i https://PySimpleGUI.net/install PySimpleGUI`

Then run the test:

5) `python -m pingmapper test`

If you recieve an error about the projection, try reinstalling pyproj with:

6) `pip install pyproj --force`

PINGMapper should be ready to go! When you want to us PM:

1) Go to "Start" > "All" > "ArcGIS" > "Python Command Prompt"
2) `activate ping`
3) `python -m pingwizard`