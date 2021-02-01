# General description
These script has been designed to download files from a set of Zoom accounts, upload them to Vimeo and remove them from Zoom.
Here the files included in this repo:
* config.json
* utils.py
* vimeo_uploader.py
* zoom_files_downloader.py
* zoom_files_delete.py

All of these python scripts runs by itself, except utils.py (this is an utility script) and the syntaxis is similar for all of them.

## Prerequisites
* python 3.x
* wget (you can get it by: `pip wget`)
* Zoom Pro Account
* Vimeo Pro Account
* Zoom Application
* Vimeo Application

## config.json
This is the config file, in this you must specify this:
* Zoom access token
* Vimeo access token
* Vimeo User Id
* Vimeo Preset Id

## Getting a Zoom Token

You can get your Zoom access token making a JWT Application in Zoom market place (https://marketplace.zoom.us/).
Here you can fin the steps to create a JWT Application: https://marketplace.zoom.us/docs/guides/build/jwt-app
After you create the application, you must copy the JWT Token to your config.json file.

## Getting a Vimeo token


## zoom_files_downloader
This script

The config file needs these fields:
* Zoom access token
* Vimeo access token
* Vimeo User Id
* Vimeo Preset Id

Vimeo User Id
To get your vime user id you must go to your profile in Vimeo. There, you must copy the last part of the url after 'user'. i.e. https://vimeo.com/user123456789, the userid is 123456789

Vimeo preset Id
To get your Vimeo preset Id you should create a preset in Vimeo, then just copy the PresetId from the Url. i.e. https://vimeo.com/settings/videos/embed_presets/987654321, the preset id is 987654321
