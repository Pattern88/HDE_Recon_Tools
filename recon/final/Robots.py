import urllib,urllib2
import mechanize
from bs4 import BeautifulSoup
import re
from Controller import Controller

class Robots(object):
	def __init__(self,domain):
		try:
			self.moudle = "Robots"
			self.db = Controller(domain)
			self.db_table = 'web_vul_t'
			self.link = "http://www."+domain+"/"
			self.links_array = self.getLinkAddress()
			self.sqlite_array = self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' Netcraft moudle"
	#get domain from user and return array of links from google
	def getLinkAddress(self):
		
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders= [('User-agent','chrome')]
		term = "robots.txt"
		disallow_array = []
		querys = self.link+term
		try:
			f = br.open(querys)
			disallow_str = "Disallow"
			for l in f.readlines():
				l = l.strip() 
				if (disallow_str in l) and (l[0] != "#") and ("//" not in l):
					disallow_array.append(self.link[:len(self.link)-1]+l[10:])	
		except:
			print "Error: Can't find -> "+querys
			pass
		return disallow_array
	#print list in a beautiful pattern
	def printLinksList(self,linkArray):
		i=1
		for item in linkArray:
			print i,") "+item
			i += 1

	def createSqliteTable(self):
		list_array = []
		for item in self.links_array:
			array = (None,item,self.moudle)
			list_array.append(array)

		return list_array