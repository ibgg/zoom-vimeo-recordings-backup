# -*- coding: utf-8 -*-
#This script get videos from Zoom and makes the backup into a vimeo account using pull approach

import os
import requests
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

#constants
START_WAIT = 7
VIDEO_DESCRIPTION = 'Video de sesión de: {topic}, al {start_date}'
CSV_HEADER = ["EMAIL","RECORD ID", "MEETING ID","MEETING UUID", "TOPIC","FILE NAME", "STATUS", "DOWNLOAD URL","PLAY URL", "RECORDING START", "RECORDING END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO ID", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS"]
# Getting vimeo token
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
vimeo_token = data['vimeo-token']

def fibo(n):
	if n <= 1:
		return n
	else:
		return(fibo(n-1) + fibo(n-2))

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

## TODO:
def upload_local_videos(records):
	print('\n::::::::::::::::::::::::::::::Backup video files from zoom::::::::::::::::::::::::::::::')
	for record in records:
		print('\n::::::::::::::::::::::::::::::uploading %s::::::::::::::::::::::::::::::'%record["file_name"]	)

## TODO:
def set_embeded_settings(records):
	print('\n::::::::::::::::::::::::::::::Setting embedded settings::::::::::::::::::::::::::::::')

def get_record_row(record):
	row = []
	for record_name in CSV_HEADER:
		row.append(record[record_name.lower().replace(' ','_')])
	return row

def check_upload_videos(records):
	global START_WAIT
	unavailablecount = 0
	print('\n::::::::::::::::::::::::::::::Checking video status from Vimeo::::::::::::::::::::::::::::::')
	headers = headers = {'authorization': 'Bearer '+vimeo_token}

	with open('./records.csv', mode='w') as f:
		writer = csv.writer(f)
		writer.writerow(CSV_HEADER)

		for record in records:
			if record['vimeo_status']!='available' and record['vimeo_status']!='error' and record['vimeo_uri'] !='':
				url = "https://api.vimeo.com/me/"+record['vimeo_uri']
				print('\n::::::::::::::::::::::::::::::checking %s::::::::::::::::::::::::::::::'%record['file_name'])
				response = requests.get(url, headers=headers)
				json_response = json.loads(response.text)

				record['vimeo_status'] = json_response['status']
				if record['vimeo_status'] == 'available' or record['vimeo_status'] == 'transcoding':
					#print(json_response)
					if record['vimeo_status'] == 'available':
						print ('Available %s video!' %record['file_name'])
					else:
						print ('Transcoding video %s... almost ready' %record['file_name'])
				elif record['vimeo_status'] != 'error':
					print('Not yet available video ' + record['file_name']+' lets try in ' +str(fibo(START_WAIT))+' seconds')
					unavailablecount += 1
				else:
					print('Error status for video %s' %record['file_name'] )

			writer.writerow(get_record_row(record))

		if unavailablecount > 0:
			sleep(fibo(START_WAIT))
			START_WAIT +=1
			check_upload_videos(records)
			#threading.Thread(target=check_upload_videos, args=[records]).start()

	return records

def upload_zoom_videos(records):
	print('\n::::::::::::::::::::::::::::::Backup video files from zoom::::::::::::::::::::::::::::::')
	url = "https://api.vimeo.com/me/videos"
	headers = headers = {'authorization': 'Bearer '+vimeo_token}

	for record in records:
		if record['vimeo_status'] != 'available' and record['vimeo_status'] != 'transcoding' and record['vimeo_status'] != 'transcode_starting':
			print('\n::::::::::::::::::::::::::::::uploading %s::::::::::::::::::::::::::::::'%record['file_name'])
			body = {}
			body['name']=record['file_name']
			body['description']=VIDEO_DESCRIPTION.format(topic=record['topic'],start_date=record['recording_start'])

			privacy= {}
			privacy['view']='unlisted'
			privacy['embed']='public'
			privacy['comments']='nobody'
			privacy['download']='false'

			upload = {}
			upload['approach']='pull'
			upload['size'] = record['file_size']
			upload['link']=record['download_url']

			body['upload']=upload
			body['privacy']=privacy

			response = requests.post(url, headers=headers, json=body)

			if response.status_code == 201:
				json_response = json.loads(response.content)
				print(json_response)
				record['vimeo_uri'] = json_response['uri']
				record['vimeo_status'] = json_response['upload']['status']
				record['vimeo_transcode_status'] = json_response['transcode']['status']
				record['vimeo_id']= record['vimeo_uri'][8:len(record['vimeo_uri'])]
		else:
			print('\n::::::::::::::::::::::::::::::record %s already or almost uploaded!::::::::::::::::::::::::::::::'%record['file_name'])

	return records

records = load_videos_data('records.csv')
#records = check_upload_videos(records)
#records = upload_zoom_videos(records)
#records = check_upload_videos(records)
#print(records)
