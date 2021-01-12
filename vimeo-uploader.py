#This script get videos from Zoom and makes the backup into vimeo account

import os
import requests
import calendar
import csv
import json
import wget
import os.path
from os import path
from datetime import date
from datetime import datetime
from datetime import timedelta
from time import time

# Getting vimeo token
with open("config.json") as json_data_file:
    data = json.load(json_data_file)
vimeo_token = data['vimeo-token']

# Loading json files
def load_videos():
	records_list = []
	csvfile = open('records.csv', 'r')
	fieldnames = ("EMAIL","RECORDID", "MEETINGID", "TOPIC","FILENAME", "STATUS", "URL","PLAY URL", "START", "END","FILE PATH", "FILE SIZE", "FILE EXTENSION")
	reader = csv.DictReader( csvfile, fieldnames)
	for index, row in enumerate(reader):
		if index > 0:
			item = {}
			item['record_id'] = row['RECORDID']
			item['meeting_id'] = row['MEETINGID']
			item['status']=row['STATUS']
			item['download_url']=row['URL']
			item['play_url']=row['PLAY URL']
			item['topic']=row['TOPIC']
			item['recording_start'] = row['START']
			item['recording_end'] = row['END']
			item['filepath']=row['FILE PATH']
			item['filename']=row['FILENAME']
			item['email']=row['EMAIL']
			item['file_size']=row['FILE SIZE']
			item['file_extension'] = row['FILE EXTENSION']
			records_list.append(item)
	return records_list
	
records = load_videos()
print(records)
#print(records_list)
