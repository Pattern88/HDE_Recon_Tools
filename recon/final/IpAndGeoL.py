import socket
from urllib2 import urlopen
from contextlib import closing
import json
from Controller import Controller
import time
import threading


class GeoLocation(object):

	def __init__(self,domain):
		try:
			self.moudle 		= "GeoLocation"
			self.db 			= Controller(domain)
			print "### Moudle -> "+self.moudle
			self.db_table 		= 'hosts_t'
			self.timeout 		= 45
			self.links_array 	= self.getLinkAddress()
			self.temp_arr 		= []
			self.error_arr		= []
			self.multiThreadEngine()
			self.updateGeoLocationField()
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' GeoLocation moudle"
			
	def multiThreadEngine(self):
		list_dev = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		lists_arr = list_dev(self.links_array,1)
		i = 1
		count_sleep_time = 1
		for item in lists_arr:
			self.links_array = item
			print "thread %d sleeps for 1 seconds" % i
			time.sleep(1)
			print "thread %d woke up" % i
			t1 = threading.Thread(target=self.getAllIpAndGeoLocation, args=[])
			t1.start()
			count_sleep_time += 1
			i += 1
		time_count = (1*self.timeout) + (count_sleep_time+i) + self.timeout
		print "################ Total Proccess TIME -> %i Seconds " %time_count
		timer = count_sleep_time
		while timer < time_count:
			time.sleep(1)
			timer+=1
			print "########### Time passed -> %i seconds" %timer


	def getLinkAddress(self):
		array = self.db.getSpecificData(self.db_table,"host")
		link_array = []
		for item in array:
			if "." in item[0]:
				link = item[0]
				link_array.append(str(link))
		link_array = set(link_array)
		new_arr = []
		for item in link_array:
			new_arr.append(item)
		return new_arr

	def getIP(self,domain): 
		ip = ""
		try:
			data 	= socket.gethostbyname(domain) 
			ip 		= str(data)
		except:
			pass
		return ip

	def updateIpField(self):
		array = self.getLinkAddress()
		for item in array:
			ip = self.getIP(item)
		try:	
			self.db.updateRowHostIp(ip,item)
		except:
			pass

	#print list in a beautiful pattern
	def printLinksList(self,linkArray):
		i=1
		for val in linkArray:
			print i,") "+str(val)
			i += 1

	def getIpAndGeoLocation(self,domain):
		# Automatically geolocate the connecting IP
		url = 'http://freegeoip.net/json/'+domain
		print "Try get data for-> "+url
		url_array = []
		try:
			with closing(urlopen(url,timeout=self.timeout)) as response:
				location = json.loads(response.read())
				#print location
				url_array = [str(location['ip']), str(location['city']), str(location['region_name']), str(location['country_name']), str(location['latitude']), str(location['longitude']), str(location['zip_code']),self.moudle,domain]
		except:
			url_array = ["","","","","","","",self.moudle,domain]
		print url_array
		return url_array
		#self.updateGeoLocationField(url_array)

	def updateGeoLocationField(self):
		try:
			for item in self.temp_arr:
				self.db.updateGeoLocationFields(item)
		except:
			pass

	def getAllIpAndGeoLocation(self):
		data_array = []
		count = 0
		try:
			for item in self.links_array:
				if "//" in item:
					link = str(item.split("//")[1])
				else:
					link = str(item)
				data_array = self.getIpAndGeoLocation(link)
				self.temp_arr.append(data_array)
		except:
			print "Error: Can't getAllIpAndGeoLocation"

	def createSqliteTable(self):
		list_array = []
		for item in self.temp_arr:
			array = (None,item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],"","",self.moudle)
			list_array.append(array)
		return list_array