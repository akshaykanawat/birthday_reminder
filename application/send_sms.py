import requests
import logging


def send_message(url,api_key,phone_number,names):
	# url = "https://www.fast2sms.com/dev/bulk"
	try:
		message = "Good morning champ!, {} are having birthday today.".format(names)
		
		querystring = {"authorization":api_key,"sender_id":"FSTSMS","message":message,"language":"english","route":"p","numbers":phone_number}

		headers = {
		    'cache-control': "no-cache"
		}

		response = requests.request("GET", url, headers=headers, params=querystring)

		logging.warn("Request response is {}".format(response.text))
	except Exception as e:
		logging.critical("Problem occurred while sending message. {}".format(e))
