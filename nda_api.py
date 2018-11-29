
import cherrypy
from database import Database
import json
import os
import random
import string
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SearchQuery(object):
    @cherrypy.expose
    def index(self):
        return "Hello world!"

    def initialiseConnection(self,properties_file_path=ROOT_DIR + '\\NDA\configs\post_gres_properties.json'):
        with open(properties_file_path) as connection_properties:
            self.__postgres_properties = json.load(connection_properties)
        self.__hostname = self.__postgres_properties["HOSTNAME"] if self.__postgres_properties["HOSTNAME"] != '' else None
        self.__port = self.__postgres_properties["PORT"] if self.__postgres_properties["PORT"] != '' else None
        self.__username = self.__postgres_properties["USERNAME"] if self.__postgres_properties["USERNAME"] != '' else None
        self.__password = self.__postgres_properties["PASSWORD"] if self.__postgres_properties["PASSWORD"] != '' else None
        self.__database = self.__postgres_properties["DATABASE"] if self.__postgres_properties["DATABASE"] != '' else None
        self.__schema = self.__postgres_properties["SCHEMA"] if self.__postgres_properties["SCHEMA"] != '' else None
        self.__clientencoding = self.__postgres_properties["CLIENT_ENCODING"] if self.__postgres_properties["CLIENT_ENCODING"] != '' else None
        self.__debug = self.__postgres_properties["DEBUG"] if self.__postgres_properties["DEBUG"] != '' else None
        Database.initialise(host=self.__hostname, port=self.__port, user=self.__username , password=self.__password,dbname=self.__database, client_encoding=self.__clientencoding)

    ''' 
       Raise error with code and message
    '''
    def error(self, code,message):
        # raise an error based on the get query
        raise cherrypy.HTTPError(status=code,message=message)

    '''
        Bulk API request POST search /bulksearch;
    '''
    @cherrypy.expose
    def nda(self):

        self.initialiseConnection()
        request_body = cherrypy.request.body.read()

        try:
            request_body_json = json.loads(request_body)
        except ValueError:
            self.error('400','Request should be in json format')

        response_dict = {}
        for entity in request_body_json:
            single_response = dict()
            id_ = str(entity['id'])
            top_responses = []

            if 'request_parameters' not in entity:
                self.error('406', "Request parameters can't be empty")

            if 'id' not in entity:
                self.error('406',"Id parameter can't be empty")

            if 'name' not in entity and 'address' not in entity:
                self.error('406', "Name and address can't be empty")

            id_ = str(entity['id'])

            '''
            Case when both name and address are present in request body
            '''
            if 'name' and 'address' in entity:
                # single_response = User.load_from_db_by_name_address(entity['name'], entity['address'], entity['response_parameters'])
                single_response['ssot_name'] = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
                single_response['ssot_address'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                single_response['response_parameters'] = {}
                for response_parameter in list(entity['request_parameters']):
                    single_response['response_parameters'][response_parameter] = ''.join(
                        random.choice(string.ascii_lowercase) for i in range(10))

            elif ('name' in entity and 'address' not in entity):
                # single_response = User.load_from_db_by_name_or_address(entity['name'],'', entity['response_parameters'])
                single_response['ssot_name'] = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
                single_response['ssot_address'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                for response_parameter in list(single_response['request_parameters']):
                    single_response['response_parameters'][response_parameter] = ''.join(
                        random.choice(string.ascii_lowercase) for i in range(10))

            elif ('name' not in entity and 'address' in entity):
                # single_response = User.load_from_db_by_name_or_address('',entity['address'], entity['response_parameters'])
                single_response['ssot_name'] = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
                single_response['ssot_address'] = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
                for response_parameter in list(single_response['request_parameters']):
                    single_response['response_parameters'][response_parameter] = ''.join(
                        random.choice(string.ascii_lowercase) for i in range(10))

            elif ('name' not in entity and 'address' not in entity):
                 self.error('406',"Name and address can't be empty")


            top_responses.append(single_response)
            response_dict[id_] = top_responses
        return str(response_dict)

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 9160,'server.thread_pool': 50})
    cherrypy.quickstart(SearchQuery())