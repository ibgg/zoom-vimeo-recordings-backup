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

with open("config.json") as json_data_file:
    data = json.load(json_data_file)
zoom_token = data['zoom-token']

# Loading json files
def load_videos_data(filename):
	print('\n::::::::::::::::::::::::::::::Loading meetings files::::::::::::::::::::::::::::::')
	records_list = []
	csvfile = open(filename, 'r')
	fieldnames = ("EMAIL","RECORDID", "MEETINGID","MEETINGUUID", "TOPIC","FILE NAME", "STATUS", "URL","PLAY URL", "START", "END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS")
	reader = csv.DictReader( csvfile, fieldnames)
	for index, row in enumerate(reader):
		if index > 0:
			item = {}
			item['record_id'] = row['RECORDID']
			item['meeting_id'] = row['MEETINGID']
			item['meeting_uuid'] = row['MEETINGUUID']
			item['status']=row['STATUS']
			item['download_url']=row['URL']
			item['play_url']=row['PLAY URL']
			item['topic']=row['TOPIC']
			item['recording_start'] = row['START']
			item['recording_end'] = row['END']
			item['file_path']=row['FILE PATH']
			item['file_name']=row['FILE NAME']
			item['email']=row['EMAIL']
			item['file_size']=row['FILE SIZE']
			item['file_extension'] = row['FILE EXTENSION']
			item['vimeo_status']=row['VIMEO STATUS']
			item['vimeo_uri']=row['VIMEO URI']
			item['vimeo_transcode_status']=row['VIMEO TRANSCODE STATUS']
			records_list.append(item)
	return records_list

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
