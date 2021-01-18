# -*- coding: utf-8 -*-
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

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

zoom_token = data['zoom-token']

start_date = '2021-01-01' #raw_input("Please let me know the start date in format yyyy-mm-dd: ")
end_date = '2021-01-16' #raw_input("Please let me know the end date in format yyyy-mm-dd: ")

def get_zoom_users():
	print('::::::::::::::::::::::::::::::Fetching user ids::::::::::::::::::::::::::::::')

	url = "https://api.zoom.us/v2/users"
	query = {"page_size":"30","status":"active"}
	headers = headers = {'authorization': 'Bearer '+zoom_token}

	response = requests.request("GET", url, headers=headers, params=query)
	users = json.loads(response.text)
	return users

def get_zoom_files(users):
	#print(users)
	print('\n::::::::::::::::::::::::::::::Downloading meetings list::::::::::::::::::::::::::::::')

	url = "https://api.zoom.us/v2/users/"
	query = {"trash_type":"meeting_recordings","mc":"false","page_size":"100"}
	headers = {'authorization': 'Bearer '+zoom_token}
	global end_date
	end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
	records_list = []

	for user in users['users']:
		_url = url + user['id']+'/recordings'
		from_date = datetime.strptime(start_date, '%Y-%m-%d').date()  #date(2020, 01, 01)
		to_date = from_date + timedelta(days=30)
		if to_date > end_date:
			to_date = end_date

		print('\n::::::::::::::::::::::::::::::'+user['email']+'::::::::::::::::::::::::::::::')
		while to_date < end_date+timedelta(days=1):
			query["from"] = str(from_date)
			query["to"] = str(to_date)

			print(':::::::::::::::::::::::::::::: ['+str(from_date)+'] - ['+str(to_date)+'] ::::::::::::::::::::::::::::::')

			response = requests.request("GET", _url, headers=headers, params=query)
			json_response = json.loads(response.content)

			if json_response['total_records'] > 0:
				for meeting in json_response['meetings']:
					if meeting['recording_count'] > 0:
						for recording in meeting['recording_files']:
							item = {}
							item['username'] = user['first_name'].encode('utf-8')
							item['email'] = user['email']
							item['recording_start'] = recording['recording_start']
							item['recording_end'] = recording['recording_end']
							item['download_url'] = recording['download_url'].encode('utf-8')
							item['play_url'] = recording['play_url'].encode('utf-8')
							item['topic'] = meeting['topic'].encode('utf-8')
							item['record_id'] = recording['id']
							item['meeting_id'] = meeting['id']
							item['meeting_uuid']=recording['meeting_id']
							item['status'] = 'listed'
							item['file_size'] = recording['file_size']
							item['file_extension'] = recording['file_extension'].encode('utf-8')
							item['vimeo_uri']=''
							item['vimeo_status']='pending'
							item['vimeo_transcode_status']='pending'

							records_list.append(item)
			from_date = to_date + timedelta(days=1)
			to_date = to_date + timedelta(days=30)

			if (to_date > end_date) and ((to_date - timedelta(days=30)) != end_date):
				to_date = end_date

	return records_list

def download_zoom_files(records_list, filename):
	print('\n::::::::::::::::::::::::::::::Downloading meetings files::::::::::::::::::::::::::::::')
	file_exists = os.path.isfile(filename)

	with open(filename, 'a') as f:
		writer = csv.writer(f)

		if not file_exists:
			writer.writerow(["EMAIL","RECORDID", "MEETINGID","MEETINGUUID", "TOPIC","FILE NAME", "STATUS", "URL","PLAY URL", "START", "END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS"])

		for index, record in enumerate(records_list):
			if not os.path.exists('./meetings/'+record['username']+'/'+record['topic']):
				os.makedirs('./meetings/'+record['username']+'/'+record['topic'])

			filepath= './meetings/'+record['username']+'/'+record['topic']+'/'
			filename = datetime.strptime(record['recording_start'], '%Y-%m-%dT%H:%M:%SZ').strftime("GMT%Y%m%d-%H%M%S")+str(index) +'.'+record['file_extension']
			record['file_path']=filepath
			record['file_name']=filename

			print('\n'+filepath+filename)

			if (path.exists(filepath+filename)):
				print('File already downloaded!')
				record["status"]="downloaded"
				writer.writerow([record['email'],record['record_id'], record['meeting_id'], record['meeting_uuid'], record['topic'], record['file_name'], record['status'], record['download_url'], record['play_url'], record['recording_start'], record['recording_end'], record['file_path'], record['file_size'], record['file_extension'], record['vimeo_status'], record['vimeo_uri'], record['vimeo_transcode_status']])
				continue
			try:
				wget.download(record['download_url'],filepath+filename)
				record["status"]="downloaded"
				writer.writerow([record['email'],record['record_id'], record['meeting_id'], record['meeting_uuid'], record['topic'], record['file_name'], record['status'], record['download_url'], record['play_url'], record['recording_start'], record['recording_end'], record['file_path'], record['file_size'], record['file_extension'], record['vimeo_status'], record['vimeo_uri'], record['vimeo_transcode_status']])
			except Exception as e:
				print(e)
				if record["status"] != "downloaded":
					record["status"]="listed"
					writer.writerow([record['email'],record['record_id'], record['meeting_id'], record['meeting_uuid'], record['topic'], record['file_name'], record['status'], record['download_url'], record['play_url'], record['recording_start'], record['recording_end'], record['file_path'], record['file_size'], record['file_extension'], record['vimeo_status'], record['vimeo_uri'], record['vimeo_transcode_status']])

	return records_list

def save_csv(fileobject, filename):
	print('\n::::::::::::::::::::::::::::::Saving downloaded report ' + filename +'::::::::::::::::::::::::::::::')
	#Checking if file exists
	file_exists = os.path.isfile(filename)
	with open(filename, 'a') as f:
		writer = csv.writer(f)
		if not file_exists:
			writer.writerow(["EMAIL","RECORDID", "MEETINGID","MEETINGUUID", "TOPIC","FILE NAME", "STATUS", "URL","PLAY URL", "START", "END","FILE PATH", "FILE SIZE", "FILE EXTENSION", "VIMEO STATUS", "VIMEO URI", "VIMEO TRANSCODE STATUS"])
		for record in fileobject:
			writer.writerow([record['email'],record['record_id'], record['meeting_id'], record['meeting_uuid'], record['topic'], record['file_name'], record['status'], record['download_url'], record['play_url'], record['recording_start'], record['recording_end'], record['file_path'], record['file_size'], record['file_extension'], record['vimeo_status'], record['vimeo_uri'], record['vimeo_transcode_status']])


csv_file = './records-'+str(time())+'.csv'
users = get_zoom_users()
recordings = get_zoom_files(users)
downloaded_records = download_zoom_files(recordings, './records.csv')

save_csv(downloaded_records, csv_file)
#save_csv('./records.csv',downloaded_records)

print('Script finished!')
