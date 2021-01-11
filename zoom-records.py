import os
import requests
from datetime import date
from datetime import datetime
from time import time
import csv
import json
import wget

with open("config.json") as json_data_file:
    data = json.load(json_data_file)
print(data)
zoom_token = data['zoom-token']

_from_date = '2020-06-01' #raw_input("Please enter start date in format yyyy-mm-dd: ")
_end_date = '2020-08-01' #raw_input("Please enter end date in format yyyy-mm-dd: ")


def get_zoom_users():
	print('::::::::::::::::::::::::::::::Fetching user ids::::::::::::::::::::::::::::::')

	url = "https://api.zoom.us/v2/users"
	query = {"page_size":"30","status":"active"}
	headers = headers = {'authorization': 'Bearer '+zoom_token}

	response = requests.request("GET", url, headers=headers, params=query)
	users = json.loads(response.text)
	return users

def get_zoom_files(users):
	print('::::::::::::::::::::::::::::::Downloading meeting files::::::::::::::::::::::::::::::')

	url = "https://api.zoom.us/v2/users/"
	query = {"trash_type":"meeting_recordings","mc":"false","page_size":"100"}
	headers = {'authorization': 'Bearer '+zoom_token}
	end_date = datetime.strptime(_end_date, '%Y-%m-%d').date()
	records_list = []

	for user in users['users']:
		from_date = datetime.strptime(_from_date, '%Y-%m-%d').date()  #date(2020, 01, 01)
		to_date = from_date.replace(month=from_date.month+1)

		while from_date < end_date:
			query["from"] = str(from_date)
			query["to"] = str(to_date)
			_url = url + user['id']+'/recordings'

			print('::::::::::::::::::::::::::::::'+_url+'::::::::::::::::::::::::::::::')

			response = requests.request("GET", _url, headers=headers, params=query)
			json_response = json.loads(response.content)

			if json_response['total_records'] > 0:
				for meeting in json_response['meetings']:
					if meeting['recording_count'] > 0:
						for recording in meeting['recording_files']:
							if recording['file_extension'] == 'MP4':
								item = {}
								item['username'] = user['first_name']
								item['recording_start'] = recording['recording_start']
								item['recording_end'] = recording['recording_end']
								item['download_url'] = recording['download_url']
								item['topic'] = meeting['topic']
								item['record_id'] = recording['id']
								item['meeting_id'] = meeting['id']
								item['file_type'] = 'mp4'

								print(item['topic'])
								records_list.append(item)

			if to_date.month+1 > 12:
				to_date = to_date.replace(year=to_date.year+1)
				to_date = to_date.replace(month=1)
			else:
				to_date = to_date.replace(month=to_date.month+1)

			if from_date.month+1 > 12:
				from_date = from_date.replace(year=from_date.year+1)
				from_date = from_date.replace(month=1)
			else:
				from_date = from_date.replace(month=from_date.month+1)

	return records_list

def download_zoom_files(records_list):
	for index, record in enumerate(records_list):
		if not os.path.exists('./meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8')):
			os.makedirs('./meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8'))
		filename = './meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8')+'/'+'record-'+str(index)+'.'+record['file_type']
		wget.download(record['download_url'],filename)
		record["status"]="downloaded"
	return records_list

def save_csv(filename, fileobject):
	for index, record in enumerate(fileobject):
		if not os.path.exists('./meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8')):
			os.makedirs('./meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8'))
		filename = './meetings/'+record['username'].encode('utf-8')+'/'+record['topic'].encode('utf-8')+'/'+'record-'+str(index)+'.'+record['file_type']
		wget.download(record['download_url'],filename)
		record["status"]="downloaded"

	mfilename='./records.csv'
	with open(mfilename, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["RECORDID", "MEETINGID", "TOPIC", "STATUS", "URL", "START", "END"])
		for item in fileobject:
			writer.writerow([item['record_id'], item['meeting_id'], item['topic'].encode('utf-8'), item['status'], item['download_url'], item['recording_start'], item['recording_end']])


users = get_zoom_users()
recordings = get_zoom_files(users)
print(recordings)
