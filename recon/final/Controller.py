#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import os
from prettytable import PrettyTable


class Controller(object):
	web_vul_t 	= [("ID","INTEGER PRIMARY KEY"),("url","TEXT"),("moudle","TEXT")]
	hosts_t 	= [("ID","INTEGER PRIMARY KEY"),("host","TEXT"),("ip","TEXT"),("city","TEXT"),("region","TEXT"),("country","TEXT"),("lat","TEXT"),("long","TEXT"),("zip_code","TEXT"),("port","TEXT"),("service","TEXT"),("moudle","TEXT")]
	metadata_t 	= [("ID","INTEGER PRIMARY KEY"),("name","TEXT"),("type","TEXT"),("size","TEXT"),("creator","TEXT"),("author","TEXT"),("title","TEXT"),("createdDate","TEXT"),("modifyDate","TEXT"),("software","TEXT"),("producer","TEXT"),("compObjUserType","TEXT"),("application","TEXT"),("moudle","TEXT")]
	contacts_t 	= [("ID","INTEGER PRIMARY KEY"),("name","TEXT"),("jobs","TEXT"),("emails","TEXT"),("phones","TEXT"),("linkedin_url","TEXT"),("facebook_url","TEXT"),("address","TEXT"),("birthday","TEXT"),("pic","TEXT"),("geolocation","TEXT"),("moudle","TEXT")]

	def __init__(self,domain):
		self.domain = domain
		try:
			self.createDatabase()
		except:
			print "Error: Can't create database"
			sys.exit(1)
		try:
			self.createAllTables()
		except:
			print "Error: Can't create all table"
		'''	
		try:
			self.insertData("web_vul",self.t_w_v)
		except:
			print "Error: Can't insert data to DB"
		'''
	def createAllTables(self):
		self.createTable("web_vul_t",self.web_vul_t)
		self.createTable("hosts_t",self.hosts_t)
		self.createTable("metadata_t",self.metadata_t)
		self.createTable("contacts_t",self.contacts_t)

	def ifDataBaseExist(self):
		db_name = self.domain+".db"
		if open(db_name):
			return True
		else:
			return False

	def dropAllTables(self):
		try:
			self.cur.execute("DROP TABLE IF EXISTS web_vul_t")
			self.cur.execute("DROP TABLE IF EXISTS hosts_t")
			self.cur.execute("DROP TABLE IF EXISTS metadata_t")
			self.cur.execute("DROP TABLE IF EXISTS contacts_t")
			self.conn.commit()
		except:
			print "Error: Can't drop tables"

	def createDatabase(self):
		#if not self.ifDataBaseExist():
		path = "workspace/"+self.domain

		#create workspace folder for project database
		try: 
		    os.makedirs(path)
		    os.makedirs(path+"/files")
		except OSError:
		    if not os.path.isdir(path):
		        raise

		#create database
		try:
			self.conn = sqlite3.connect(path+"/"+self.domain+".db")
			self.cur = self.conn.cursor()
			self.cur.execute('SELECT SQLITE_VERSION()')
			data = self.cur.fetchone()
			print "workspace: "+self.domain
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)

	def createTable(self,table_name,array):
		#print array
		query = "CREATE TABLE "+table_name+"("
		for i in array:
   			query += i[0]+" "+i[1]+","
   		query = query[:len(query)-1]+")"
		try:
			self.cur.execute(query)
			self.conn.commit()
		except:
			pass

	def updateRowHostIp(self,update_data,check_value):
		array = []
		array.append(update_data)
		array.append(check_value)
		query = ("UPDATE hosts_t SET ip = ? WHERE host = ?")
		try:
			self.cur.execute(query,array)
			self.conn.commit()
		except:
			print "Error: Can't excute query ->"+query

	def updateContactsEmail(self,update_array):
		query = ("UPDATE contacts_t SET emails = ? WHERE name = ?")
		try:
			self.cur.execute(query,update_array)
			self.conn.commit()
		except:
			print "Error: Can't excute query ->"+query

	def updateGeoLocationFields(self,update_array):
		query = ("UPDATE hosts_t SET ip = ?, city = ?, region = ?, country = ?, lat = ?, long = ?, zip_code = ?, moudle = ? WHERE host = ?")
		try:
			self.cur.execute(query,update_array)
			self.conn.commit()
		except:
			print "Error: Can't excute query ->"+query

	def insertData(self,table_name,data):

		val = "VALUES("
		counter = 0
		try:
			while counter < len(data[0]):
				val += "?,"
				counter += 1
			val = val[:len(val)-1]+")"
			query = "INSERT INTO "+table_name+" "+val
		except:
			print "Error: len(data[0]) is empty!"
			pass
		
		try:
			self.cur.executemany(query, data)
			self.conn.commit()
		except:
			print "Error: Can't excute query -> insertData()"
			pass

	def showTable(self,table_name):
		try:
			query = "SELECT * FROM "+table_name
			self.cur.execute(query)
			rows = self.cur.fetchall()
			for row in rows:
				print row
		except:
			print "Error: Can't excute query ->"+query

	def deleteTable(self,table_name):
		query = "DROP TABLE "+table_name
		try:
			self.cur.execute(query)
			self.conn.commit()
		except:
			print "Error: Can't excute query ->"+query

	def deleteRow(self,table_name,id_num):
		query = "DELETE FROM "+table_name+" WHERE ID = %i" %(id_num)
		try:
			self.cur.execute(query)
			self.conn.commit()
		except:
			print "Error: Can't excute query ->"+query
	def delRows(self):
		i = 0
		while i <140:
			self.deleteRow("hosts_t",i)
			i +=1

	def getData(self,table_name):
		try:
			query = "SELECT * FROM "+table_name
			self.cur.execute(query)
			rows = self.cur.fetchall()
			return rows
		except:
			print "Error: Can't excute query ->"+query
			return [False]

	def getSpecificData(self,table_name,field_name):
		try:
			query = "SELECT "+field_name+" FROM "+table_name
			self.cur.execute(query)
			rows = self.cur.fetchall()
			return rows
		except:
			print "Error: Can't excute query ->"+query
			return [False]
		#ToDo: get relevent data by parameter

	def editData(self):
		pass
		#ToDo: edit relevent data by parameter 

	def printBeautifulTable(self,table_name):
		try:
			query = "SELECT * FROM "+table_name
			self.cur.execute(query)
		except:
			print "Error: Can't get data form table->"+table_name

		try:
			col_names 				= [cn[0] for cn in self.cur.description]
			rows 					= self.cur.fetchall()
			x 						= PrettyTable(col_names)
			x.align[col_names[1]] 	= "l" 
			x.align[col_names[2]] 	= "r" 
			x.padding_width 		= 1    
			for row in rows:
			    x.add_row(row)

			print (x)
			tabstring = x.get_string()
			file_path = "workspace/"+self.domain+"/"
			file_name = table_name+"_export.txt"
			use_file  = file_path+file_name 
			output = open(use_file,"w")
			output.write("Recon Data"+"\n")
			output.write(tabstring)
			output.close()
		except:
			print "Error: Can't print beautiful table->"+table_name
			self.showTable(table_name)