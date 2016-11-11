import urllib, urllib2
import mechanize
from bs4 import BeautifulSoup
import re
import wget
import time
import threading
import os
from stat import * # ST_SIZE etc
import pwd # not available on all platforms
import datetime 
import subprocess
import random
from Controller import Controller


mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT = 10.0
class Metadata(object):

	def __init__(self,domain):
		try:
			self.moudle 		= "Metadata"
			self.db 			= Controller(domain)
			print "### Moudle -> "+self.moudle
			self.db_table 		= 'metadata_t'
			self.timeout 		= 60
			self.ext_type 		= ""
			self.folder_path 	= "workspace/"+domain+"/files"
			self.links_array 	= self.getAllFiles()
			self.temp_arr 		= []
			self.multiThreadEngine()
			self.foca_array 	= self.getMetadata()
			self.sqlite_array 	= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' metadata moudle"

	#get domain from user and return array of links from google
	def getLinkAddress(self):
		#ext_str   = "doc+%7C+docx+%7C+ppt+%7C+xls+%7C+docs+%7C+pptx+%7C+xlsx+%7C+pdf"
		# put the urls for all of your proxies in a list
		proxies = ["http://197.254.115.110:8080","http://95.85.12.187:3128","http://186.93.166.36:8080",'http://101.4.136.2:9999','http://219.142.192.196:2829','http://182.93.234.54:8080','http://177.200.64.175:8080','http://185.59.127.11:3128','http://54.241.248.52:80']
		term = "inurl:"+self.db.domain+"+filetype:"+self.ext_type
		#term = "inurl:"+domain+" filetype:"+ext_str
		google_file_link_array = []
		#term = "f5.com+pdf+files"
		br 			  	= mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders 	= [('User-ugent','Mozilla/5.0')]
		querys			= "http://www.google.com/search?num=10&q="+term
		
		print "Searching for: '"+querys+"'"
		
		htmlText = br.open(querys).read()	
		# construct your list of url openers which each use a different proxy
		openers = []
		f = open("out.html", "w")
		f.write(str(htmlText))
		f.close()	

		try:
			soup 		= BeautifulSoup(htmlText)
			search 		= soup.findAll('h3', attrs={'class':'r'})
			http_str	= 'http'
			f = open("out.html", "w")
			f.write(str(search))
			f.close()
			for item in search:
				soup2 		= BeautifulSoup(str(item))
				link  		= str(soup2.findAll('a'))
				link_only 	= str(link.split('href="')[1])
				if (http_str) not in link_only[:5]:
					link_only 	= str(link_only[7:].split('&amp')[0])
				else:
					link_only 	= str(link_only.split('"')[0])
				if http_str in link_only:
					google_file_link_array.append(link_only)
		except:
			print "Error: Can't BeautifulSoup ###str###"
		return self.removeUnnecessaryLinks(google_file_link_array)

	def removeUnnecessaryLinks(self,links_array):
		only_files_array = []
		ext_array = ['.doc','.docx','.ppt','.xls','.docs','.pptx','.xlsx','.pdf']
		for item in links_array:
			#print item
			if any(s in item[-5:] for s in ext_array):
				only_files_array.append(item)
		return set(only_files_array)

	def getAllFiles(self):
		all_files_array = []
		ext_array = ['doc','docx','ppt','xls','docs','pptx','xlsx','pdf']
		for item in ext_array:
			self.ext_type = item
			print "15 seceond sleep to avoid lockout"
			time.sleep(15)
			all_files_array.extend(self.getLinkAddress())
		return all_files_array
			
	#print list in a beautiful pattern
	def printLinksList(self,linkArray):
		i=1
		for item in linkArray:
			print i,") "+item
			i += 1

	def multiThreadEngine(self):
		list_dev = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		lists_arr = list_dev(link_array,5)
		i = 1
		count_sleep_time = 1
		for item in lists_arr:
			self.links_array = item
			print "thread %d sleeps for 5 seconds" % i
			time.sleep(5)
			print "thread %d woke up" % i
			t1 = threading.Thread(target=downloadFiles, args=[])
			t1.start()
			count_sleep_time += 1
			i += 1
		time_count = (5*self.timeout) + (count_sleep_time+i) + self.timeout
		print "################ Total Proccess TIME -> %i Seconds " %time_count
		timer = count_sleep_time
		while timer < time_count:
			time.sleep(1)
			timer+=1
			print "########### Time passed -> %i seconds" %timer

	def downloadFiles(self):
		files_name_array = []
		for item in self.links_array:
			try:
				path = "workspace/f5.com/files"
				file_name = wget.download(item,out=self.folder_path)
				splits = item.split('/')
				self.temp_arr.append(splits[len(splits)-1])
				print "download file -> "+item
			except:
				print "Error: Can't get file ->"+item

	def createSqliteTable(self):
		list_array = []
		for item in self.foca_array:
			array = (None,item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],self.moudle)
			list_array.append(array)
		return list_array

	def getMetadata(self):

		metadata_dic = {"name":"",
		"type":"",
		"size":"",
		"creator":"",
		"author":"",
		"title":"",
		"createDate":"",
		"modifyDate":"",
		"software":"",
		"producer":"",
		"compObjUserType":"",
		"application":""
		}
		metadataList = []
		file_name = ""
		file_name_arr = ['workspace/f5.com/files/test1.docx','workspace/f5.com/files/test1.pdf','workspace/f5.com/files/test1.docx']
		resList = []
		for doc in file_name_arr:
			file_name = doc
			docType = str(doc).split('.')[1]
			#self.folder_path+"/"+
			doc = subprocess.check_output(["exiftool %s" % (self.folder_path+"/"+doc)], shell=True).split('\n')
			metadataList.append(doc)	
			i= 0
		metadata_dic["name"] = file_name

		for meta in metadataList:
			miniList = []
			for line in meta:
				if 'File Type      ' in line:
					ftype=line.replace("File Type                       : ","")
					miniList.append(ftype)
					metadata_dic["type"] = ftype

				if 'File Size      ' in line:
					fsize=line.replace("File Size                       : ","")
					miniList.append(fsize)
					metadata_dic["size"] = fsize

				if 'Creator      ' in line:
					user=line.replace("Creator                         : ","")
					miniList.append(user)
					metadata_dic["creator"] = user

				if 'Author' in line:
					user=line.replace("Author                          :","")
					miniList.append(user)
					metadata_dic["author"] = user	

				if 'Title      ' in line:
					title=line.replace("Title                           : ","")
					miniList.append(title)
					if "\xd7" not in title:
						metadata_dic["title"] = title						

				if 'Create Date' in line:
					cDate=line.replace("Create Date                     : ","")
					miniList.append(cDate)
					metadata_dic["createDate"] = cDate
					
				#get modified date
				if 'Modify Date' in line:
					if 'Zip' in line: 
						pass
					else:
						mDate=line.replace("Modify Date                     : ","")
						miniList.append(mDate)
						metadata_dic["modifyDate"] = mDate	

				if 'Software' in line:
					if 'History Software Agent' in line:
						pass
					else:				
						app=line.replace("Software                        : ","")
						miniList.append(app)
						metadata_dic["software"] = app	

				if 'Producer' in line:
					app=line.replace("Producer                        : ","")
					miniList.append(app)
					metadata_dic["producer"] = app
			
				if 'Comp Obj User Type              ' in line:
					app=line.replace("Comp Obj User Type              : ","")
					miniList.append(app)
					metadata_dic["compObjUserType"] = app

				if 'Application   ' in line:
					app=line.replace("Application                     : ","")
					miniList.append(app)	
					metadata_dic["application"] = app
			resList.append(metadata_dic.copy())
		return resList

	def createSqliteTable(self):
		list_array = []
		for item in self.foca_array:
			array = (None,item["name"],item["type"],item["size"],item["creator"],item["author"],item["title"],item["createDate"],item["modifyDate"],item["software"],item["producer"],item["compObjUserType"],item["application"],self.moudle)
			list_array.append(array)
		return list_array