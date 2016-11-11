
import urllib, urllib2
import mechanize
from bs4 import BeautifulSoup
import re
from Controller import Controller
import webbrowser

class GoogleDorking(object):
	def __init__(self,domain):
		try:
			self.moudle 			= "GoogleDorking"
			self.db 				= Controller(domain)
			self.link 				= "http://www."+domain+"/"
			self.db_table			= "web_vul_t"
			print "### Moudle -> "+self.moudle
			self.timeout 			= 30
			self.links_array 		= self.getLinkAddress()
			self.links_array 		= self.removeUnnecessaryLink()
			self.links_array 		= self.removeNotFoundLink()
			self.sqlite_array 		= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' GoogleDorking moudle"

	#get domain from user and return array of links from google
	def getLinkAddress(self):

		br 			  	= mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders 	= [('User-ugent','chrome')]
		term 			= "site%3A'"+self.db.domain+"'+-allinurl%3A'*.html+*.htm'"
		links_array 	= []
		querys			= "http://www.google.com/search?num=200&q="+term
		print "Searching for: '"+querys+"'"
		try:
			htmlText = br.open(querys)
			soup 			= BeautifulSoup(htmlText.read())
			search 			= soup.findAll('h3', attrs={'class':'r'})
			http_str 		= 'http'
			for item in search:
				soup2 		= BeautifulSoup(str(item))
				link  		= str(soup2.findAll('a'))
				link_only 	= str(link.split('href="')[1])
				if (http_str) not in link_only[:5]:
					link_only 	= str(link_only[7:].split('&amp')[0])
				else:
					link_only 	= str(link_only.split('"')[0])
				if http_str in link_only:
					links_array.append(link_only)
		except:
			print "Error: Can't open link-> "+term
		return links_array

	#remove Unnecessary emails from arrray of emails 
	def removeUnnecessaryLink(self):
		link_array = []
		ext_array = [".html", ".htm"]
		for item in self.links_array:
			#print item
			if not any(s in item[-5:] for s in ext_array):
				link_array.append(item)
		return set(link_array)


	#remove Unnecessary emails from arrray of emails 
	def removeNotFoundLink(self):
		link_array = []
		for item in self.links_array:
			try:
				htmlCode = urllib2.urlopen(item,timeout=self.timeout)
				real_link = htmlCode.geturl()
				if ("Not Found" and "404" not in str(htmlCode.read())):
					link_array.append(real_link)
				else:
					print "Notting here... link->"+item
			except:
				print "Error: Can't Find link->"+item
		return link_array
	
	def createSqliteTable(self):
		list_array = []
		for item in self.links_array:
			array = (None,item,self.moudle)
			list_array.append(array)

		return list_array

	#print list in a beautiful pattern
	def printLinksList(self):
		i=1
		for item in self.links_array:
			print i,") "+item
			i += 1




