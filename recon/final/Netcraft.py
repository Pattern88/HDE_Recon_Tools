import urllib2, urllib
import Cookie
from bs4 import BeautifulSoup
import mechanize
import cookielib
import re
import hashlib
import time
import random
import sys, os
import socket
from Controller import Controller

class Netcraft(object):

	def  __init__(self, domain):
		try:
			self.moudle 		= "Netcraft"
			self.db 			= Controller(domain)
			self.db_table 		= 'hosts_t'
			print "### Moudle -> "+self.moudle
			session 			= self.openConnection()
			self.links_array	= self.searchSubDomain(session)
			self.sqlite_array 	= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' Netcraft moudle"

		#print "Error - failed to connect"

	def openConnection(self):
		session = mechanize.Browser()
		session.set_handle_equiv(True)
		session.set_handle_redirect(True)
		session.set_handle_referer(True)
		session.set_handle_robots(False)
		session.addheaders = [('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.0'), ('Accept', '*/*')]

		return session

	def searchSubDomain(self, session):
		cj = cookielib.LWPCookieJar()
		session.set_cookiejar(cj)	
		
		url=session.open("http://searchdns.netcraft.com/?restriction=site%2Bends%2Bwith&host=" + str(self.db.domain)).read()

		for cookie in cj:
			if cookie.name == 'netcraft_js_verification_challenge':
				challenge = cookie.value
				response = hashlib.sha1(urllib.unquote(challenge)).hexdigest()
				cj.set_cookie(cookielib.Cookie(version=0,name='netcraft_js_verification_response',value=response,port=None,port_specified=False,domain='.netcraft.com',domain_specified=True,domain_initial_dot=False,path='/',path_specified=True,secure=False,expires=None,discard=False,comment=None,comment_url=None,rest=None))
		try:
			url=session.open("http://searchdns.netcraft.com/?restriction=site%2Bends%2Bwith&host=" + str(self.db.domain)).read()

			soup = BeautifulSoup(url)

			num = soup.find_all('p', attrs={'align':'center'})

			resultsNum = str(num[0]).split("<em>")[1].split("</em>")[0]
			print resultsNum
			res = str(resultsNum[6:].split('sites')[0])
			if int(res)%10 == 0:
				pageEnd = int(res)/20
			else: 
				pageEnd = int(res)/20 + 1
			print pageEnd


			linklists =[]
			pattern = '<td align\=\"left\">\s*<a href=\"http://(.*?)/"'
			sites = re.findall(pattern,url)
			for site in sites:
				linklists.append(site)

			pageNum = 21
			if pageEnd > 1:
				lastDomain = sites[int(pageNum)-2]
				
				
			for i in range (1, pageEnd):
				print "sleep to avoid lockout"
				time.sleep(random.randint(5,15))
				query = "http://searchdns.netcraft.com/?host=*." + str(self.db.domain) + "&last=" + str(lastDomain) + "&from=" + str(pageNum) + "&restriction=site%20contains&position=limited"

				url = session.open(query).read()

				sites = re.findall(pattern,url)

				for site in sites:
					linklists.append(site)
				lastDomain = sites[len(sites)-1]
				pageNum+=20
				pageEnd-=1

			return linklists

		except:
			print "Error - please try again."


	def createSqliteTable(self):
		list_array = []
		for item in self.links_array:
			array = (None,item,"","","","","","","","","",self.moudle)
			list_array.append(array)
		return list_array