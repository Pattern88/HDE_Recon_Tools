import urllib, urllib2
import mechanize
import cookielib
import Cookie
import socket
from Controller import Controller
import time
import threading

class SubDomain(object):
	def __init__(self,domain):
		try:
			self.moudle 		= "SubDomain"
			self.db 			= Controller(domain)
			self.db_table 		= 'hosts_t'
			self.txtFile 		= "hostnames"
			print "### Moudle -> "+self.moudle
			self.timeout 		= 10
			self.temp_arr		= []
			self.error_arr		= []
			self.links_array 	= self.getHostnamesArray()
			self.multiThreadEngine()
			self.sqlite_array 	= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' SubDomain moudle"

	def multiThreadEngine(self):
		list_dev = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		lists_arr = list_dev(self.links_array,20)
		i = 1
		count_sleep_time = 0
		for item in lists_arr:
			self.links_array = item
			print "thread %d sleeps for 3 seconds" % i
			time.sleep(3)
			print "thread %d woke up" % i
			t1 = threading.Thread(target=self.getLinkAddress, args=[])
			t1.start()
			count_sleep_time += 3
			i += 1
		time_count = (1*self.timeout) + (count_sleep_time+i) + self.timeout
		print "################ Total Proccess TIME -> %i Seconds " %time_count
		timer = count_sleep_time
		while timer < time_count:
			time.sleep(1)
			timer+=1
			print "########### Time passed -> %i seconds" %timer

	def getHostnamesArray(self):
		sub_domain_array = []
		file_name = "bruteForce/"+self.txtFile+".txt"
		try:
			source_code_file = open(file_name,"r")	
			for line in source_code_file.readlines():
				line = line.strip()
				sub_domain_array.append(line)
		except:
			print "File Open -> Failed"
		return sub_domain_array
	#get domain from user and return array of links from google
	def getLinkAddress(self):
		for item in self.links_array:
			url = "http://"+item+"."+self.db.domain
			print "Try url: " + url
			try:
				html_code = urllib2.urlopen(url,timeout=self.timeout)
				print html_code.info()
				link = url.split("//")[1]
				self.temp_arr.append(link)
				print "################Found Sub-Domain->" +  link
			except:
				self.error_arr.append(url.split("//")[1])
				pass

	def createSqliteTable(self):
		list_array = []
		for item in self.temp_arr:
			array = (None,item,"","","","","","","","","",self.moudle)
			list_array.append(array)
		return list_array

	def getIp(self,link):
		try:
			data 	= socket.gethostbyname(link.split("//")[1]) 
			ip 		= str(data)
			return ip
		except Exception:
			return "0"

	#print list in a beautiful pattern
	def printLinksList(self,linkArray):
		i=1
		for item in linkArray:
			print i,") "+item
			i += 1