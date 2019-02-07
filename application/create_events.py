import requests
import pymongo
from data_access import DataAccess 
import datetime
from pymongo import InsertOne, DeleteOne, ReplaceOne
from pymongo.errors import BulkWriteError
import logging
import configparser 
from utils import Utils
import sys
import os

# url = "https://www.fast2sms.com/api/sms/free"

# querystring = {"authorization":"VEdgCf2b7y0MDZJE1AleOCsorSGMCkl4EMXwd7EpE1k5xqWpmNwhESTxzBfB","sender_id":"FSTSMS","message":"This is test message","language":"english","route":"p","numbers":"9742338006"}

# headers = {
#     'cache-control': "no-cache"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)

# print(response.text)
componentName = "Event Creator"
db_client = ""
current_time = datetime.datetime.now()
config =configparser.ConfigParser()
propertiesFilePath = ""

def init_configs(propertiesFilePath):
	try:
		config.read(propertiesFilePath)

		fb_url = config.get("facebook_settings","url")
	except Exception as e:
		logging.critical("Problem reading config. {}".format(e))

def init_db():
	try:
		global db_client
		db_client = DataAccess.get_instance().get_db_client()
	except Exception as e:
		logging.critical("Problem occured while connecting db. {}".format(e))

def calendar_download():
	try:
		print ('-- Opening calendar URL --')

		# Get your URL from facebook and replace below
		url = 'https://www.facebook.com/events/ical/birthdays/?uid=100000280320487&key=AQAUabHd_2huaF7o'

		#Open downloaded calendar file
		data = requests.get(url)
		#Append all data into a single continuous string
		text_data = data.content
		print ('-- Calendar data fetched successfully from URL --')
		return text_data
	except Exception as e:
		logging.critical('Error occured in calendar_download() - Error Message : '+str(e))

text_data = calendar_download()

def fetch_birthdays(text_data):
	try:
		print (' ')
		print ('-- Creating birthday list --')


		text = text_data.split('BEGIN:VEVENT')
		#Initializing value for id.		
		user_id = 1000
		#This list element is a list of lists and will store all birthdays as individual lists
		birthday_list=[]
		birthday_dict ={}
		#Looping through each birthday

		for i in range(1,len(text)):
			#Fetching each birthday as a element of list
			lines=text[i].split('\r\n')
			#Fetching DTSTART element of calendar file
			dtstart=(lines[1].split(':'))[1]
			#Splitting DTSTART into YYYY MM DD components
			bday_year = dtstart[0:4]
			bday_month = dtstart[4:6]
			bday_date = dtstart[6:8]
			#Fetching SUMMARY element of calendar file
			summary = lines[2].split(':')[1].split("'s birthday")[0]
			name = summary.split(' ')

			#Fetch first, middle, last names and their space(' ') adjustments
			if len(name)==0:
				pass
			elif len(name)==1:
				first_name = name[0]
				middle_name = ''
				last_name = ''
			elif len(name)==2:
				first_name = name[0]
				middle_name = ' '
				last_name = name[1]
			elif len(name)==3:
				first_name = name[0]
				middle_name = ' '+name[1]+' '
				last_name = name[2]
			else:
				first_name = name[0]
				middle_name = ' '+name[1]+' '
				last_name = ''
				for j in range(2,len(name)):
					last_name+=name[j]+' '
				last_name=last_name[0:-1]
			#Fetch uid element from calendar file
			uid = lines[5].split(':')[1].split('@facebook.com')[0]
			profile_id = uid[1:]
			
			#Creating a list for this birthday
			full_name = first_name+middle_name+last_name
			query ={
					"name" : full_name,
					"profile_id" : profile_id,
					"created_date" : current_time,
					"parameters" : {
						"user_id" : user_id,
						"birth_date" : bday_date,
						"birth_month" : bday_month,
						"birth_year" : bday_year,			
					}
			}

			# line_data_list = [user_id+i,bday_year,bday_month,bday_date,profile_id]
			#Adding this list to parent birthday list
			# birthday_list.append(line_data_list)
			birthday_list.append(InsertOne(query))
		# print(birthday_list)
		db_client["event_manager"].bulk_write(birthday_list)	
		logging.warn("{} number events have been inserted to database.".format(len(birthday_list)))
		
	except Exception as e:
		logging.critical('Error occured in fetch_birthdays() - Error Message : {}'.format(e))

def main():
	
	try:
		if len(sys.argv) == 0:
				return

		global propertiesFilePath    
		propertiesFilePath = sys.argv[1]		
		propertiesFilePath = os.path.join(os.getcwd()+"/configs/",propertiesFilePath)
		Utils.setup_logger(propertiesFilePath,componentName)	
		init_db()
		text_data = calendar_download()
		fetch_birthdays(text_data)
	except Exception as e:
		logging.warn("Error in main function. {} ".format(e))
# # print(a)

if __name__ == '__main__':
	main()