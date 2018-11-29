import psycopg2
from database import CursorConnectionFromPool
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import sys

class User:
    def __init__(self,response_list):
        self.response_list_main=response_list

    def __repr__(self):
        return "<User {}>".format(self.id)

    @classmethod
    def load_from_db_by_name_or_address(cls,name,address,response_parameters):
        with CursorConnectionFromPool() as cursor:
                #cursor.execute('SELECT * FROM users WHERE email=%s',(email,))
                if( name and not address):
                    cursor.execute('SELECT transaction_id,name_orig FROM ssot.transaction')
                    user_dict = dict(cursor.fetchall())
                    name_list = list(user_dict.values())
                    matched_names_scores = process.extract(name, name_list, limit=3)
                elif(address and not name):
                    cursor.execute('SELECT transaction_id,address1_orig FROM ssot.transaction')
                    user_dict = dict(cursor.fetchall())
                    address_list = list(user_dict.values())
                    matched_names_scores = process.extract(address, address_list, limit=3)
                #print(matched_name)
                cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_schema = \'ssot\' AND table_name = \'transaction\'')
                temp_columns = list(cursor.fetchall())
                response_list=[]
                response_columns = [name for (name,) in temp_columns]
                matched_names=[name for (name,score) in matched_names_scores]
                matched_scores=[score for (name,score) in matched_names_scores]
                matched_id=[]
                for id, name in user_dict.items():
                    if name in matched_names:
                        index_name=matched_names.index(name)
                        matched_names.remove(name)
                        #print(index_name)
                        cursor.execute('SELECT * FROM ssot.transaction WHERE transaction_id = %s',(id,))
                        response_data = cursor.fetchone()
                        print(response_data)
                        response_dict = dict(zip(response_columns,response_data))
                        #response_list.append(response_dict)
                        response_dict_filtered={}
                        response_parameter_list = response_parameters.split(",")
                        if ',' in response_parameters:
                            for i in response_parameter_list:
                                response_dict_filtered[i] = response_dict[i]
                        elif (response_parameters):
                            response_dict_filtered[response_parameters] = response_dict[response_parameters]
                        response_dict_filtered['score']=matched_scores[index_name]
                        response_list.append(response_dict_filtered)
                response_list = sorted(response_list, key=lambda k: 100-k['score'])
                #from operator import itemgetter
                #sortedresponse = sorted(response_list, key=itemgetter('score'))
                return cls(response_list=response_list)

    @classmethod
    def load_from_db_by_name_address(cls, name,address,response_parameters):
        with CursorConnectionFromPool() as cursor:

            cursor.execute('SELECT transaction_id,name_orig FROM ssot.transaction')
            dict_name=dict(cursor.fetchall())
            cursor.execute('SELECT transaction_id,address1_orig FROM ssot.transaction')
            dict_address=dict(cursor.fetchall())
            ds = [dict_name, dict_address]
            merged_dict = {}
            for k in dict_name:
                merged_dict[k] = " ".join([str(d[k]) for d in ds])
            name_address_list = list(merged_dict.values())
            matched_nameaddress = process.extract(name+address, name_address_list,limit=3)
            print("matched_name",matched_nameaddress)
            cursor.execute('SELECT column_name FROM information_schema.columns WHERE table_schema = \'ssot\' AND table_name = \'transaction\'')
            temp_columns = list((cursor.fetchall()))
            response_columns = [name for (name,) in temp_columns]
            response_list = []
            matched_names = [name for (name, score) in matched_nameaddress]
            matched_scores = [score for (name, score) in matched_nameaddress]
            matched_id = -99999999
            for id, nameaddress in merged_dict.items():
                if nameaddress in matched_names:
                    index_name = matched_names.index(nameaddress)
                    matched_names.remove(nameaddress)
                    cursor.execute('SELECT * FROM ssot.transaction WHERE transaction_id = %s',(id,))
                    response_data = cursor.fetchone()
                    print('response data',response_data)
                    response_dict = dict(zip(response_columns,response_data))
                    # response_list.append(response_dict)
                    response_dict_filtered = {}
                    response_parameter_list = response_parameters.split(",")
                    if ',' in response_parameters:
                        for i in response_parameter_list:
                            response_dict_filtered[i] = response_dict[i]
                    elif (response_parameters):
                        response_dict_filtered[response_parameters] = response_dict[response_parameters]
                    response_dict_filtered['score'] = matched_scores[index_name]
                    response_list.append(response_dict_filtered)
            response_list=sorted(response_list,key=lambda k: 100-k['score'])
            return cls(response_list=response_list)