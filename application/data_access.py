from pymongo import MongoClient
from bson import ObjectId
from threading import Lock
import logging
import os
import datetime
from utils import Utils

import sys



class DataAccess:
    """
    A class that enables db class to perform database operations
    """     
    __instance = None

    def __init__(self):
        self.__db_client = None
        self.__read_db_client = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            lock = Lock()
            lock.acquire()
            cls.__instance = DataAccess()
            cls.__instance.__db_client = None
            cls.__instance.__read_db_client = None
            lock.release()
        
        return cls.__instance



                
    def get_db_client(self):
        """Returns a DB client with read-write permissions, this is a synchronized method.        
        
        Returns:
            [db_client] -- Mongo database read-write client
        
        Raises:
            Exception -- Raises exception if connection to the db fails
        """         
        try:
            if self.__db_client is None:
                lock = Lock()
                lock.acquire()
                if Utils.read_from_env("MONGO_DB_URI") is None:
                    raise Exception("DB URL not found in the environment. Please set the parameter MONGO_DB_URI")
                
                self.__db_url = Utils.read_from_env("MONGO_DB_URI")
                self.__db_client = MongoClient(self.__db_url)
                self.__db_client = self.__db_client['events']
                
                lock.release()

            return self.__db_client
        except Exception as e:
            message = "Error while getting db client, exception is. Exception {}".format(e)
            logging.error(message,exc_info=True)
            self.__db_client = None
            # logging.critical(message)
            raise Exception(message)

    def get_read_db_client(self):
        """Returns a DB client with read only permissions, this is a synchronized method.
        
        Keyword Arguments:
            read_db_url {String} -- Read DB Url to get DB connection (default: {None})
        
        Returns:
            [read_db_client] -- Mongo database read client
        
        Raises:
            Exception -- Raises exception if connection to the db fails
        """
        
        try:
            if self.__read_db_client is None:
                lock = Lock()
                lock.acquire()
                if Utils.read_from_env("MONGO_DB_READ_URI") is None:
                    raise Exception("DB URL not found in the environment. Please set the parameter MONGO_DB_READ_URI")
                
                self.__read_db_url = Utils.read_from_env("MONGO_DB_READ_URI")
                self.__read_db_client = MongoClient(self.__read_db_url)
                self.__read_db_client = self.__read_db_client['litmus-db']
                #print(self.__read_db_client)
                lock.release()

            return self.__read_db_client
        except Exception as e:
            message = "Error while getting db client, exception is. Exception {}".format(e)
            logging.error(message,exc_info=True)
            self.__read_db_client = None
            # logging.critical(message)
            raise Exception(message)


   
