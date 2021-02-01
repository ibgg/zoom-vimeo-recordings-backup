# -*- coding: utf-8 -*-
#This script get videos from Zoom and makes the backup into a vimeo account using pull approach

import os
import sys
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
from time import time
from time import sleep
from utils import Utils

#constants
START_WAIT = 7
VIDEO_DESCRIPTION = 'Video de sesión de: {topic}, al {start_date}'

def fibo(n):
	if n <= 1:
		return n
	else:
		return(fibo(n-1) + fibo(n-2))

def create_vimeo_folder(foldername):
	print('\n::::::::::::::::::::::::::::::Create Vimeo Folder {foldername}::::::::::::::::::::::::::::::'.format(foldername=foldername))
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/users/{user_id}/projects'.format(user_id=utils.vimeo_userid)
	body = {}
	body['name']=foldername

	response = requests.post(url, headers=headers, json=body)
	folder = {}
	# json_response = {}
	# json_response['uri']='/users/112233/projects/12345'
	# folder[foldername] = json_response['uri'][json_response['uri'].rindex('/')+1:len(json_response['uri'])]

	if response.status_code == 201:
		json_response = json.loads(response.content)
		print('Folder {foldername} created!'.format(foldername=foldername))
		folder[foldername] = json_response['uri'][json_response['uri'].rindex('/')+1:len(json_response['uri'])]

	return folder

def get_vimeo_folders():
	print('\n::::::::::::::::::::::::::::::Getting video folders::::::::::::::::::::::::::::::')
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/users/{user_id}/projects'.format(user_id=utils.vimeo_userid)
	folders = {}
	folders_counter = 0
	counter = 1

	while True:
		query = {'per_page':100, 'page':counter}

		response = requests.get(url, headers=headers, params=query)
		json_response = json.loads(response.content)

		if (json_response['total'] > 0):
			for record in json_response['data']:
				folders[record['name']] = record['uri'][record['uri'].rindex('/')+1:len(record['uri'])]

		folders_counter += len(json_response['data'])
		counter += 1

		if (folders_counter >=  json_response['total']):
			break

	return folders

def request_move_videos_to_folder(videos_list, record, folder_id):
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url='https://api.vimeo.com/users/{user_id}/projects/{project_id}/videos'

	videos_str = ','.join(videos_list[record])
	query = {'uris':videos_str}
	url = url.format(user_id=utils.vimeo_userid, project_id=folder_id)
	response = requests.put(url, headers=headers, params=query)

	if response.status_code != 204:
		print('Error trying to move videos videos {videos} to folder {folder}'.format(videos=videos_str, folder=record))
	else:
		print('Moved videos {videos} to folder {folder}'.format(videos=videos_list[record], folder=record))


def move_videos_to_folder(records):
	print('\n::::::::::::::::::::::::::::::moving videos to folder::::::::::::::::::::::::::::::')

	folders = get_vimeo_folders()
	videos_list = {}

	for record in records:
		if record['file_extension'] == 'MP4':
			if record['vimeo_folder'] not in videos_list:
				videos_list[record['vimeo_folder'].rstrip()] = []
			videos_list[record['vimeo_folder'].rstrip()].append(record['vimeo_uri'])

	# Looking for the specified folder in vimeo
	for record in videos_list:
		if record not in folders:
			print (record + ' NOT FOUND in vimeo folders, lets create the folder')
			new_folder = create_vimeo_folder(record)
			if len(new_folder) == 0:
				print('Not created folder')
			else:
				folders[record] = new_folder[record]
				request_move_videos_to_folder(videos_list, record, folders[record])
		else:
			request_move_videos_to_folder(videos_list, record, folders[record])


def set_embeded_presets(record):
	print('\n::::::::::::::::::::::::::::::Setting embedded settings::::::::::::::::::::::::::::::')
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}
	url = 'https://api.vimeo.com/videos/{video_id}/presets/{preset_id}'.format(video_id=record['vimeo_id'], preset_id=utils.vimeo_preset_id)

	response = requests.put(url, headers=headers)
	if response.status_code == 204:
		record['vimeo_embedded'] = True

	return record


def check_upload_videos(records, filename):
	print('\n::::::::::::::::::::::::::::::Checking video status from Vimeo::::::::::::::::::::::::::::::')
	global START_WAIT
	unavailablecount = 0
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}

	if not os.path.exists('./reports'):
		os.makedirs(str('./reports'))

	with open(filename, mode='w') as f:
		writer = csv.writer(f)
		writer.writerow(utils.CSV_HEADER)

		for record in records:
			if record['file_extension'] == 'MP4':
				if record['vimeo_status']!='available' and record['vimeo_status']!='error' and record['vimeo_uri'] !='':
					url = "https://api.vimeo.com/me/"+record['vimeo_uri']
					print('\n::::::::::::::::::::::::::::::checking %s::::::::::::::::::::::::::::::'%record['file_name'])
					response = requests.get(url, headers=headers)
					json_response = json.loads(response.text)

					record['vimeo_status'] = json_response['status']
					if record['vimeo_status'] == 'available' or record['vimeo_status'] == 'transcoding':
						#print(json_response)
						if record['vimeo_embedded'] == 'False':
							record = set_embeded_presets(record)

						if record['vimeo_status'] == 'available':
							print ('Available %s video!' %record['file_name'])
						else:
							print ('Transcoding video %s... almost ready' %record['file_name'])

					elif record['vimeo_status'] != 'error':
						if record['vimeo_embedded'] == 'False':
							record = set_embeded_presets(record)

						print('Not yet available video ' + record['file_name']+' lets try in ' +str(fibo(START_WAIT))+' seconds')
						unavailablecount += 1
					else:
						print('Error status for video %s' %record['file_name'] )
			writer.writerow(utils.get_record_row(record))

		if unavailablecount > 0:
			sleep(fibo(START_WAIT))
			START_WAIT +=1
			check_upload_videos(records, filename)
			#threading.Thread(target=check_upload_videos, args=[records]).start()

	return records

def upload_zoom_videos(records):
	print('\n::::::::::::::::::::::::::::::Backup video files from zoom::::::::::::::::::::::::::::::')
	url = "https://api.vimeo.com/me/videos"
	headers = headers = {'authorization': 'Bearer '+utils.vimeo_token}

	for record in records:
		if record['file_extension'] == 'MP4':
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
					#print(json_response)
					record['vimeo_uri'] = json_response['uri']
					record['vimeo_status'] = json_response['upload']['status']
					record['vimeo_transcode_status'] = json_response['transcode']['status']
					record['vimeo_id']= record['vimeo_uri'][8:len(record['vimeo_uri'])]
			else:
				print('\n::::::::::::::::::::::::::::::record %s already or almost uploaded!::::::::::::::::::::::::::::::'%record['file_name'])

	return records

if __name__ == "__main__":
	utils = Utils()
	files = utils.get_records(sys.argv, 'vimeo_uploader.py')

	# if utils.input_type == 1:
	# 	files = check_upload_videos(files, utils.input_file)
	#
	# files = upload_zoom_videos(files)
	# files = check_upload_videos(files, utils.output_file)
	# move_videos_to_folder(files)
