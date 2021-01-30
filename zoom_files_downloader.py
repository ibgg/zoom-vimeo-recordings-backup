# -*- coding: utf-8 -*-
import os
import sys
import requests
import calendar
import csv
import json
import wget
import os.path
import urllib.parse
from os import path
from datetime import date
from time import time
from utils import Utils

def download_zoom_files(records_list, filename):
	print('\n::::::::::::::::::::::::::::::Downloading meetings files::::::::::::::::::::::::::::::')
	file_exists = os.path.isfile(filename)

	if not os.path.exists('./reports'):
		os.makedirs('./reports')

	with open(filename, 'w') as f:
		writer = csv.writer(f)

		if not file_exists:
			writer.writerow(utils.CSV_HEADER)

		for index, record in enumerate(records_list):
			if not os.path.exists(str(record['file_path'])):
				os.makedirs(str(record['file_path']))

			print('\n'+record['file_path']+record['file_name'])

			if (path.exists(record['file_path']+record['file_name'])):
				print('File already downloaded!')
				record["status"]="downloaded"
				writer.writerow(get_record_row(record))
				continue
			try:
				print('Lets download '+ str(record['download_url']))
				wget.download(str(record['download_url']),str(record['file_path']+record['file_name']))
				record["status"]="downloaded"
				writer.writerow(get_record_row(record))
				print('\n...downloaded')
			except Exception as e:
				print(e)
				if record["status"] != "downloaded":
					record["status"]="listed"
					writer.writerow(get_record_row(record))

	return records_list

#UTIL


if __name__ == "__main__":
	#csv_file = './reports/zoom-files-'+start_date.replace('-','')+'-'+end_date.replace('-','')+'.csv'

	utils = Utils()
	files = utils.get_records(sys.argv, 'zoom_files_downloader.py')

	downloaded_files = download_zoom_files(files, utils.output_file)
	utils.save_csv(downloaded_files, utils.output_file)

	print('Script finished!')
