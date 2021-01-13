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
VIDEO_DESCRIPTION = 'Video de sesión de {topic} al {start_date}'

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
def load_videos():
	print('\n::::::::::::::::::::::::::::::Loading meetings files::::::::::::::::::::::::::::::')
	records_list = []
	csvfile = open('records.csv', 'r')
	fieldnames = ("EMAIL","RECORDID", "MEETINGID", "TOPIC","FILE NAME", "STATUS", "URL","PLAY URL", "START", "END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS")
	reader = csv.DictReader( csvfile, fieldnames)
	for index, row in enumerate(reader):
		if index > 0 and row['FILE EXTENSION'] == 'MP4':
			item = {}
			item['record_id'] = row['RECORDID']
			item['meeting_id'] = row['MEETINGID']
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

def upload_local_videos(records):
	print('\n::::::::::::::::::::::::::::::Backup video files from zoom::::::::::::::::::::::::::::::')
	for record in records:
		print('\n::::::::::::::::::::::::::::::uploading %s::::::::::::::::::::::::::::::'%record["file_name"]	)

def check_upload_videos(records):
	global START_WAIT
	unavailablecount = 0
	print('\n::::::::::::::::::::::::::::::Checking video status from Vimeo::::::::::::::::::::::::::::::')
	headers = headers = {'authorization': 'Bearer '+vimeo_token}

	for record in records:
		print('\n::::::::::::::::::::::::::::::checking %s::::::::::::::::::::::::::::::'%record['file_name'])
		url = "https://api.vimeo.com/me/"+record['vimeo_uri']
		if record['vimeo_status']!='transcoding' and record['vimeo_status']!='error' and record['vimeo_uri'] !='':
			response = requests.get(url, headers=headers)
			json_response = json.loads(response.text)
			print(json_response['status'])

			record['vimeo_status'] = json_response['status']
			if record['status'] == 'available' or record['status'] == 'transcoding':
				if record['status'] == 'available':
					print ('Available %s video!',%record['filename'])
				else:
					print ('Transcoding video %s... almost ready' %record['file_name'])
			elif json_response['vimeo_status'] != 'error':
				print('Not yet avaiable video ' + record['file_name']+' lets try in ' +str(fibo(START_WAIT))+' seconds')
				unavailablecount += 1
			else:
				print('Error status for file %s' %record['file_name'] )

	if unavailablecount > 0:
		sleep(fibo(START_WAIT))
		START_WAIT +=1
		check_upload_videos(records)
		#threading.Thread(target=check_upload_videos, args=[records]).start()

	return records

def upload_zoom_videos(records):
	print('\n::::::::::::::::::::::::::::::Backup video files from zoom::::::::::::::::::::::::::::::')
	url = "https://api.vimeo.com/me/videos"
	#query = {"page_size":"30","status":"active"}
	headers = headers = {'authorization': 'Bearer '+vimeo_token}

	for record in records:
		print('\n::::::::::::::::::::::::::::::uploading %s::::::::::::::::::::::::::::::'%record['file_name'])
		if record['vimeo_status'] != 'avaiable':
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
		else:
			print('\n::::::::::::::::::::::::::::::record %s already uploaded!::::::::::::::::::::::::::::::'%record['file_name'])

	return records

records = load_videos()
#records[0]['vimeo_uri']='/videos/499840153'
#records[0]['vimeo_status']='in_progress'
records = check_upload_videos(records)
records = upload_zoom_videos(records)
records = check_upload_videos(records)
print(records)
#upload_local_videos(records)
#upload_zoom_videos(records)
#print(records)
#print(records_list)
