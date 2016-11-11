import urllib, urllib2
import mechanize
from Controller import Controller
import webbrowser
import time
import threading

class AdminPanel(object):
	def __init__(self,domain):
		try:
			self.moudle 			= "AdminPanel"
			self.db 				= Controller(domain)
			print "### Moudle -> "+self.moudle
			self.link 				= "http://www."+domain+"/"
			self.db_table 			= 'web_vul_t'
			self.timeout 			= 20
			self.temp_arr			= []
			self.server_source_code = self.openBrowserToGetServiceSidePlatform()
			self.links_array 		= self.setLinkPanelAdmin()
			self.multiThreadEngine()
			self.sqlite_array 		= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' AdminPanel moudle"

	def multiThreadEngine(self):
		list_dev = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		lists_arr = list_dev(self.links_array,5)
		i = 1
		count_sleep_time = 1
		for item in lists_arr:
			self.links_array = item
			print "thread %d sleeps for 1 seconds" % i
			time.sleep(1)
			print "thread %d woke up" % i
			t1 = threading.Thread(target=self.getLinkAddress, args=[])
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

	#get domain from user and return array of links from google
	def setLinkPanelAdmin(self):
		panel_admin_array = []
		file_name = "bruteForce/"+self.server_source_code+".txt"
		try:
			source_code_file = open(file_name,"r")
			for line in source_code_file.readlines():
				line = line.strip()
				url = self.link+line
				panel_admin_array.append(url)
		except:
			"File Open -> Failed"
		return panel_admin_array

	def getLinkAddress(self):
		for item in self.links_array:
			print "Try url: " + item
			try:
				html_code = urllib2.urlopen(item,timeout=self.timeout)
				real_link = html_code.geturl()
				self.temp_arr.append(real_link)
				print "############## Found panel -> " +  real_link
			except:
				print "Error: Can't open url ->"+item
		#return set(panel_admin_array)
	
	def openBrowserToGetServiceSidePlatform(self):
		server_side_code = ['php','asp','js','brf','cfm','cgi']
		print "########### Server-Side-Script ############"
		print "php -> 1"
		print "asp -> 2"
		print "js  -> 3"
		print "brf -> 4"
		print "cfm -> 5"
		print "cgi -> 6"
		print
		webbrowser.get('firefox').open_new_tab(self.link)
		user_input = int(raw_input("find the server-source-code... and enter the result between 1-6: "))
		if user_input in [1,2,3,4,5,6]:
			return server_side_code[user_input-1]
		else:
			print "Wrong number!!!"
			return server_side_code[0]


	def createSqliteTable(self):
		list_array = []
		temp = set(self.temp_arr)
		for item in temp:
			array = (None,item,self.moudle)
			list_array.append(array)

		return list_array

	#print list in a beautiful pattern
	def printLinksList(linkArray):
		i=1
		for item in linkArray:
			print i,") "+item
			i += 1