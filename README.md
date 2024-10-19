# Le Mans Ultimate Settings Widget

M$ Windows application that will let you create presets/profiles of your LMU settings.
Quickly change between e.g., a performance focused VR setup, or
an eye-candy favoured Replay setup.


### Usage
- Download the <a href="https://github.com/tappi287/lmu_settings_widget/releases">latest installer</a> and start the app
- Choose a preset or click "Graphics Presets", hit the [ + ] button and create a new one
- adjust the settings to your liking, they will be automatically saved and applied to your LMU installation whenever
you change a setting


## Features
##### Preset import/export
Presets will be saved to your MyDocuments dir and can be shared. Drop preset files onto
the app window to import those presets.

##### Replay Manager [ToDo]
Browse through your replay library, sort, filter by race/qualy etc.
and batch delete or watch replays.
Choose a replay specific Graphics Preset if you start 
the replay from within the app.

##### Advanced Settings
Adjust settings not available in the game UI without hacking through json files. 

### Requirements
 - M$ Windows >= 7 (only tested on 11)
 - modern Web Browser (will start with Chrome, fallback to Chromium Edge, fallback to system default web browser)
 - Le Mans Ultimate Steam installation


## Development Setup
If you'd like to contribute to development, these steps may help you to get up and running:
 - clone this repo `git clone https://github.com/tappi287/lmu_settings_widget`
 - install [Node Package Manager](https://nodejs.org/en/download/) `npm`
 - change to front-end dir `cd vue` and install node modules `npm install`


 - make sure you have a Python 3.11.x interpreter on your system [python.org/downloads](https://www.python.org/downloads/)
 - install poetry `https://install.python-poetry.org`
 - create python virtual env `poetry install`

#### Usage
 - in the project root dir *lmu_settings_widget* switch run the Python virtual env by `poetry run python scripts/app.py`
 - build an executable/installer with `poetry run python scripts/build.py`

  ##### Dev Requirements
 - Python 3.11.x
   - latest poetry
 - npm >= 8.3.1
 - Chromium based web browser (Edge, Opera, Chrome) for running in browser app-mode
