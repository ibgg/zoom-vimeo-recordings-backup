# -*- coding: utf-8 -*-
#This script get videos from Zoom and makes the backup into a vimeo account using pull approach

import os
import requests
import urllib
import calendar
import csv
import json
import wget
import os.path
import time
import threading
from os import path
from datetime import date
from datetime import datetime
from datetime import timedelta
from time import time
from time import sleep

CSV_HEADER = ["EMAIL","RECORD ID", "MEETING ID","MEETING UUID", "TOPIC","FILE NAME", "STATUS", "DOWNLOAD URL","PLAY URL", "RECORDING START", "RECORDING END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO ID", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS", "VIMEO EMBEDDED"]

with open("config.json") as json_data_file:
    data = json.load(json_data_file)
zoom_token = data['zoom-token']

# Loading json files
def load_videos_data(filename):
	print('\n::::::::::::::::::::::::::::::Loading meetings files::::::::::::::::::::::::::::::')
	records = []
	csvfile = open(filename, 'r')
	reader = csv.DictReader( csvfile, CSV_HEADER)
	for index, row in enumerate(reader):
		if index > 0 and row['FILE EXTENSION'] == 'MP4':
			item = {}
			for record_name in CSV_HEADER:
				item[record_name.lower().replace(' ','_')] = row[record_name]
			records.append(item)
	return records

def delete_zoom_files(records):

	query = {"action":"trash"}
	headers = {'authorization': 'Bearer '+zoom_token}

	for record in records:
		url = "https://api.zoom.us/v2/meetings/{meeting_id}/recordings/{record_id}"
		url=url.format( meeting_id=urllib.quote_plus(record['meeting_uuid']),record_id=urllib.quote_plus(record['record_id']) )
		print(url)

		if record['status']=='downloaded' or record['vimeo_status']=='available':
			print('::::::::::::::::::::::::::::::Deleting file {recordid} in meeting {meetingid}::::::::::::::::::::::::::::::'.format(recordid=record['record_id'], meetingid=record['meeting_id']) )
			response = requests.request("DELETE", url, headers=headers, params=query)
			print(response)
			if response.status_code != 204:
				json_response = json.loads(response.content)
				print(json_response)

	return records

records = load_videos_data('records_zoom.csv')
#print (records)
records = delete_zoom_files(records)
