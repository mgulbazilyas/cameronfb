import re

import mysql.connector
import string
import random
import json
import datetime
import os

import wget

class con:

    def __init__(self,path):
        self.path = path
        self.createcon()



    def createcon(self):
        self.con = mysql.connector.connect(host="162.241.252.209",
                                            user="seasonli_fbuser",
                                            password="facebook1",
                                            database="seasonli_jobsapi"
        )
        print("succesfull")
        self.query = '''insert into `job_detail` (message,post_time,email_id,post_id,location_id) VALUES (%s,%s,%s,%s,%s)'''
    def get_groups(self):

        query = '''SELECT link FROM seasonli_fbgroup.`groups`'''
        self.createcon()
        cur = self.con.cursor()
        cur.execute(query)
        results = [i[0] for i in cur.fetchall()]
        cur.close()
        return results
    def addData(self,data,tries=0):
        if tries>3:return False
        group = data[0]
        post_text = data[1]
        title = data[3]
        experience = data[4]
        size = data[5]
        email = data[2]
        try: cur = self.con.cursor()
        except: self.createcon();self.addData(data)
        try:
            self.con.commit()
            cur.execute(self.query, (post_text,datetime.datetime.now(),email,group,1))
            cur.close()
            print("done")
            return True
        except Exception as e:
            print(e)
            self.createcon()

            self.addData(data, tries+1)


