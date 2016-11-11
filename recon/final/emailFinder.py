
import urllib, urllib2
import mechanize
from bs4 import BeautifulSoup
import re
import time
import socket
from Controller import Controller
import threading
import Cookie

mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT = 10.0

#get domain from user and return array of links from google
class WebCr(object):

	def __init__(self, domain):

		self.domain = domain
		self.path = "workspace/"+self.domain+"/employees.txt"
		self.db 			= Controller(domain)
		self.moudle 		= "WebCr"
		self.db_table 		= 'contacts_t'
		self.txtFile 		= "contacts"
		print "### Moudle -> "+self.moudle
		self.timeout 		= 10
		self.temp_arr		= []
		self.contactEmails 	= []
		try:
			self.userFile = open(self.path, 'w')
			links = self.getLinkAddress()
			self.multiThreadEngine(links)
			
			print self.temp_arr
			self.sqlite_array 	= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
			ans = raw_input("Do you want to insert to the table emails based on pattern for the DB contacts? Y/N   ")
			if ans == str('Y') or str('y'):
				self.createEmployeesEmailsFile()
				self.db.printBeautifulTable(self.db_table)
			else:
				pass
		except:
			print "ERROR: Can't 'run' WebCr moudle"

	def getLinkAddress(self):
	    br = mechanize.Browser()
	    br.set_handle_robots(False)
	    br.addheaders= [('User-agent','chrome')]
	    
	    links_array = []
	    http_head = 'http'
	    term =  self.domain.replace(" ","+")
	    
	    
	    query_array = [
	                    "http://www.google.com/search?num=100&q="+term,
	                    "http://www.google.com/search?num=100&q="+"@"+term,
	                    "http://www.google.com/search?num=100&q="+term+"email"+"address",
	                    "http://www.google.com/search?num=100&q="+term+"linkedin",
	                    "http://www.google.com/search?num=100&q="+term+"+contact"+"+information",
	                    "http://www.google.com/search?num=100&q="+term+"+contact"+"+us",
	                    "http://www.google.com/search?num=100&q="+term+"mailto"
	                  ]
	    print "Searching for links"
	    for query in query_array:
	        htmltext  = br.open(query,timeout=30).read()
	        soup = BeautifulSoup(htmltext)
	        search = soup.findAll('h3',attrs={'class':'r'})  
	           
	        for item in search:
	            soup2 = BeautifulSoup(str(item))
	            links = str(soup2.findAll('a'))
	            source_link = str(links.split('href="')[1])

		    if http_head not in source_link[:5]:
			    link_only 	= str(source_link[7:].split('&amp')[0])
		    else:
			    link_only 	= str(source_link.split('"')[0])
		    if http_head  in source_link:
			    links_array.append(link_only)
	        
	    return links_array

	def multiThreadEngine(self, links_array):
		list_dev = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		lists_arr = list_dev(links_array,20)
		i = 1
		count_sleep_time = 0
		for item in lists_arr:
			self.links_array = item
			print "thread %d sleeps for 3 seconds" % i
			time.sleep(3)
			print "thread %d woke up" % i
			t1 = threading.Thread(target=self.getAllEmail(), args=[])
			t1.start()
			#t1.join(TIMEOUT*3+3)
			#t1.close()
			count_sleep_time += 3
			i += 1
		time_count = (1*self.timeout) + (count_sleep_time+i) + self.timeout
		print "################ Total Proccess TIME -> %i Seconds " %time_count
		timer = count_sleep_time
		while timer < time_count:
			time.sleep(1)
			timer+=1
			print "########### Time passed -> %i seconds" %timer

	def getAllEmail(self):
		int_array = []
		
		for link in self.links_array:
			print link
			res = self.findContactEmails(link)
			int_array.extend(res)
		self.removeUnnecessaryEmail(int_array)

	def findContactEmails(self, link):
		mails_array = []
		pattern = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b',re.IGNORECASE)    

		try:
			htmlCode = urllib2.urlopen(link,timeout=30)
			html = htmlCode.read()
			emailAddresses = re.findall(pattern, html)
			for email in emailAddresses:
				mails_array.append(str(email))  
			mails_array = set(mails_array)
		except:
	   		print "Error - Can't open link -> "+link
		return mails_array

	def removeUnnecessaryEmail(self,int_array):
		ext_array = [".png",".js",".jpg", ".jpeg"]
		for item in int_array:
			#print item
			if not any(s in item[-5:] for s in ext_array):
				company = str(self.domain.split('.')[0])
				if company in item:
					self.temp_arr.append(item)

	def createEmployeesEmailsFile(self):
		names = self.db.getSpecificData('contacts_t','name')
		self.userFile.write("\n".join(str(x[0]) for x in names))		
		
		self.userFile = open(self.path, 'r')

		print
		print "look at the following options:"	
		print "1. FirstName@domain.com"
		print "2. LastName@domain.com"
		print "3. [firstLetter]FirstName.[FirstLetter]LastName@domain.com" 
		print "4. [firstLetter]LastName.[FirstLetter]FirstName@domain.com"
		print "5. [firstLetter]FirstName.LastName@domain.com"
		choise = raw_input("plese choose your request tamplate:")		

		for employee in self.userFile.readlines():
			try:	
				if employee != "":
					temp_list = []
					employee = employee.replace("\n","")
					firstName = employee.split(' ')[0]
					lastName =  employee.split(' ')[1]
					
					if choise == str('1'):
						E_mail = firstName + '@' + self.domain

					if choise == str('2'):
						E_mail = lastName + '@' + self.domain

					if choise == str('3'):
						E_mail = firstName[0] + '.' + lastName[0] + '@' + self.domain

					if choise == str('4'):
						E_mail = lastName[0] + '.' + firstName[0] + '@' + self.domain

					if choise == str('5'):
						E_mail = firstName[0] + '.' + lastName + '@' + self.domain
							
					temp_list.append(E_mail)
					temp_list.append(employee)
					if E_mail in self.temp_arr:
						self.temp_arr.remove(email)
						print E_mail
					
					try:
						self.db.updateContactsEmail(temp_list)
					except:
						print "Can't update contact email"
						pass

					self.contactEmails.append(temp_list)
					E_mail = ""
			except:
				pass
		print self.contactEmails
	
	def createSqliteTable(self):
		list_array = []
		for item in self.temp_arr:
			array = (None,"","",item,"","","","","","","",self.moudle)
			list_array.append(array)
		return list_array
