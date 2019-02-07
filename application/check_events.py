import pymongo
import requests
import logging
import configparser 
from utils import Utils
import sys
import os
from data_access import DataAccess 
import datetime
from send_sms import send_message


componentName = "Notifier"
db_client = ""
current_time = datetime.datetime.now()
current_day = datetime.date.today()
config =configparser.ConfigParser()
propertiesFilePath = ""
api_key =""
url =""
phone_number =""

def init_configs(propertiesFilePath):
	global api_key
	global url
	global phone_number
	try:
		config.read(propertiesFilePath)
		api_key = config.get('api_settings',"api_key")
		url = config.get("api_settings","url")
		phone_number = config.get("general_settings","phone_number")
	except Exception as e:
		logging.critical("Problem reading config. {}".format(e))

def init_db():
	try:
		global db_client
		db_client = DataAccess.get_instance().get_db_client()
	except Exception as e:
		logging.critical("Problem occured while connecting db. {}".format(e))


def check_event():
	try:
		name_list = []
		date_now = str(current_day.day) 
		month_now =str(current_day.month) 
		year_now = str(current_day.year)

		if len(date_now) ==1:
			date_now = "0"+date_now
		if len(month_now) == 1:
			month_now = "0"+month_now 

		query = {"parameters.birth_month" : date_now, "parameters.birth_date" : month_now, "parameters.birth_year" : year_now}
		db_data = list(db_client["event_manager"].find(query))
		
		for doc in db_data:
			name_list.append(doc["name"])

		all_names = ", ".join(name_list)
		print(url)
		message_response = send_message(url,api_key,phone_number,all_names)
		logging.warn("Message response is : {}".format(message_response))
		

	except Exception as e:
		logging.critical("Problem occured while checking events. {}".format(e))

def main():
	try:
		if len(sys.argv) == 0:
				return

		global propertiesFilePath    
		propertiesFilePath = sys.argv[1]		
		propertiesFilePath = os.path.join(os.getcwd()+"/configs/",propertiesFilePath)
		Utils.setup_logger(propertiesFilePath,componentName)
		init_db()
		init_configs(propertiesFilePath)
		check_event()
	except Exception as e:
		logging.critical("Problem occured in main function. {}".format(e))

if __name__ == '__main__':
	main()