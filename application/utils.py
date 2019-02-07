import configparser
import boto3
from threading import Lock
import logging
import os
import json
import socket
import time
from bson import ObjectId
from datetime import datetime,date
import requests
from logging.handlers import TimedRotatingFileHandler
import sys

class Utils:
    """Class with utility functions"""
    __config_instance = None
    __queue_client = None
    __queue_url = None
    __carbon_sock = None

    def __init__(self):
        pass
    
    @classmethod
    def read_config(cls,file_path=None):
        """Read the config from config.properties
        
            Class level function to read the config
        """
        
        try:
            if cls.__config_instance is None:
                #print("Reading Configs")
                lock = Lock()   
                lock.acquire()
                cls.__config_instance = configparser.ConfigParser()
                cls.__config_instance.read(file_path)
                #print("Reading Configs Hello {}".format(file_path))
                lock.release()

            return cls.__config_instance
        except Exception as e:
            message = "Error while reading config file {}, file_path {}".format(e,file_path)
            logging.error(message,exc_info=True)
            return cls.__config_instance
        

    

    @classmethod
    def read_from_env(cls,param_name):
        
        """Read Environment variables
        
        
        Arguments:
            param_name {String} -- The paramater name that has to be read
        
        Returns:
            None -- If parameter is not found
            value -- The value of the parameter
        """
        value = None
        try:            
            if os.environ.get(param_name) is not None:
                value = os.environ.get(param_name)
            return value
        except Exception as e:
            message = "Error while getting ENV variable {}. Exception : {}".format(param_name,e)
            logging.error(message,exc_info=True)
            return value

    
    @classmethod
    def setup_logger(cls,config_file_path, componentName):
        """[summary]
        
        This function will setup logger which will send logs to log file and if logstash url is available in config file, 
        then it will also send logs to logstash over http which can be viewed in kibana.

        [description]
        
        Arguments:
            
            config_file_path {file path} -- This will be the config file path.
            componentName {string} -- This will be the name of the component whose logs will be managed.
        """
        try:

            config=cls.read_config(config_file_path)

            get_log_level=config.get("general_settings","log_level")
            get_log_path=config.get("general_settings","log_path")
            # log_to_file = config.get("general_settings", "log_to_file")
            logger=logging.getLogger()
            
            if get_log_level == "debug":
                logger.setLevel(logging.DEBUG)
            elif get_log_level == 'info':
                logger.setLevel(logging.INFO)
            elif get_log_level == "warning":
                logger.setLevel(logging.WARNING)
            elif get_log_level == "critical":
                logger.setLevel(logging.CRITICAL)
            

            formatter=logging.Formatter('[%(asctime)s] [%(levelname)s] [{}] [%(filename)s] [%(funcName)s] %(message)s'.format(componentName))
            log_handler= TimedRotatingFileHandler(get_log_path,when='midnight',interval=1)
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)


        except Exception as e:
            logging.warn("Log path or log level not found in config file. {}".format(e))
                

    @classmethod
    def send_message_to_queue(cls,message):
        """Send message to the SQS queue
        
        [description]
        
        Arguments:
            message {[dict]} -- Message to be sent to the queue
        """
        logging.debug("Sending Message to the queue")
        try:
            queue_name = cls.read_from_env("QUEUE_NAME")
            if queue_name is  None:
                raise Exception("Queue Name could not be fetched from ENV")
                return                
            # Creating your own session
            session = boto3.session.Session()

            __queue_client = session.client('sqs')

            queue_url_resp = __queue_client.get_queue_url(QueueName=queue_name)
            
            if "QueueUrl" in queue_url_resp:
                __queue_url = queue_url_resp["QueueUrl"]

            message_body = json.dumps(message,default=Utils.json_serial)
            response = __queue_client.send_message(QueueUrl=__queue_url,MessageBody=message_body)
            
            logging.debug("SQS response {}".format(response))
            
            if response.get("Failed") and len(response.get("Failed")) > 0:
                ex_message = "Failed to send some of the requests {}".format(response.get("Failed"))
                #logging.error(ex_message)
                raise Exception(ex_message)
            
        except Exception as e:
            message = "Error while sending message to the queue {}".format(e)
            logging.error(message,exc_info=True)
            Utils.notify_exception(message,"customer_notifier_producer.exception.generic")
            raise Exception(message)

    @classmethod
    def json_serial(cls,obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))

    
    @classmethod
    def notify_exception(cls,message,category=None):
        #cls.__notify_via_carbon(category)
        cls.__notify_via_api(message,category)



    @classmethod
    def __notify_via_api(cls,message,category):
        try:
            logging.warn("Calling URl")
            __api_url = Utils.read_config().get("exception_notification_settings","rest_api_url")
            __subject = Utils.read_config().get("exception_notification_settings","email_subject")
            __from = Utils.read_config().get("exception_notification_settings","email_from")
            __to_list_str = Utils.read_config().get("exception_notification_settings","email_to_list")
            __to_list = __to_list_str.split(",")

            params = {
                "subject" : __subject,
                "bodyHTML" :"<html>"+str(message)+"</html>",
                "from" : __from,
                "to" : __to_list
            }
            
            headers = {"Content-Type":"application/json"}
            
            logging.warn("Email Params {}".format(params))

            r = requests.post(__api_url, json=params,headers=headers)
            
            resp = r.json()

            logging.warn("Response from Exception Email {}".format(resp))

        except Exception as e:
            msg = "Exception while calling notify api {}".format(e)            
            logging.exception(msg)
        

    



