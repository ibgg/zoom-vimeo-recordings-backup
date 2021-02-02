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

### config.json
This is the config file, in this you must specify this:
* Zoom access token
* Vimeo access token
* Vimeo User Id
* Vimeo Preset Id

### Getting a Zoom Token
You can get your Zoom access token making a JWT Application in Zoom market place (https://marketplace.zoom.us/). You can fin the steps to create a JWT Application here https://marketplace.zoom.us/docs/guides/build/jwt-app. After you create the application, you must copy the JWT Token to your config.json file.

### Getting a Vimeo token
You can get your Vimeo Token creating a Vimeo application  https://developer.vimeo.com/apps, after you create your application, it's necessary to generate an Access Token, you can do in the same page. Please, go to this url for more information. https://developer.vimeo.com/api/guides/start. When your application and Access Token be ready, copy the Access Token in your config.json file.

### Vimeo User Id
To get your vime user id you must go to your profile in Vimeo. There, copy the last part of the url after 'user'. i.e. https://vimeo.com/user123456789, the userid is 123456789

### Vimeo preset Id
To get your Vimeo preset Id you should create a preset in Vimeo, then just copy the PresetId from the Url. i.e. https://vimeo.com/settings/videos/embed_presets/987654321, the preset id is 987654321

## Downloading files with zoom_files_downloader
This script gets all users in your Zoom account and download files from these in your local machine.
All the scripts runs in input file mode and date range mode.

### Using file input mode
`python zoom_files_downloader.py --inputfile inputfile.csv  --outputfile outputfile.csv`

This mode needs a CSV file; records in the file are defined in utils.CSV_HEADER. At the beginning would be difficult to create this file, and that's why you should use this method just then this file has been generated by zoom_files_downloader, zoom_files_delete or vimeo_uploader in date range mode.

You can see this behavior in this diagram: ![Download files using an input file](diagrams/download_files.jpg?raw=true "Download files using an input file")

### Using date range mode
`python zoom_files_downloader.py --daterange YYYY-mm-dd YYYY-mm-dd  --outputfile outputfile.csv`

You can download files between two dates. i.e.
`python zoom_files_downloader.py --daterange 2020-01-01 2020-05-03  --outputfile outputfile.csv`

This mode gets files from Zoom accounts and saves them in local storage.

You can see this behavior in this diagram: ![Download files using an input file](diagrams/download_zoom.jpg?raw=true "Download files using an input file")
