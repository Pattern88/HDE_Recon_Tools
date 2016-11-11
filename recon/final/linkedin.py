import json, sys, re, os
import requests
import getpass
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
import mechanize
import urllib
import urllib2
import getpass
from Controller import Controller

class Linkedin(object):
	def __init__(self,domain):
		try:
			self.moudle 		= "Linkedin"
			self.db 			= Controller(domain)
			self.db_table 		= 'contacts_t'
			print "### Moudle -> "+self.moudle+" ###"
			self.temp_arr		= []
			self.session = self.loginToLinkedin()
			self.companyId = self.chooseCompany()
			self.links_array 	= self.find_contacts()
			#self.multiThreadEngine()
			self.sqlite_array 	= self.createSqliteTable()
			self.db.insertData(self.db_table,self.sqlite_array)
			#self.printLinksList(self.error_arr)
			self.db.printBeautifulTable(self.db_table)
		except:
			print "ERROR: Can't 'run' Linkedin moudle"
	
	def loginToLinkedin(self):
		try:
			accountUsername = raw_input("Please insert your email: ")
			accountPassword = getpass.getpass("Please insert your password: ")

			linkedinSession = requests.Session()
			r = linkedinSession.get('https://www.linkedin.com/')
			pattern = re.compile('name="loginCsrfParam" value="([^"]+)"')
			match = pattern.search(r.text)
			
			url = 'https://www.linkedin.com/uas/login-submit'
			params = {'session_key': accountUsername, 'session_password': accountPassword , 'loginCsrfParam': match.group(1)}
			r = linkedinSession.post(url, data=params)
			print "You looged in Successfully"
		
		except:
			print "Something went wrong during login."

		return linkedinSession

	def chooseCompany(self):
		
		try:	
			response = self.session.get('https://www.linkedin.com/vsearch/cj?type=companies&keywords=' + self.db.domain)
			response = json.loads(response.text)['content']
			dictOfResults = response['page']['voltron_unified_search_json']['search']['results']
			
			companies_list = []
			i = 0
			for company in dictOfResults:
						
				c = company['company']
				c_list = []
				c_list.append(i)

				c_id = c['id']
				c_list.append(c_id)

				c_name = re.sub('<[a-zA-Z ="/]+>', '', c['fmt_canonicalName'].encode('ascii', 'ignore'))
				c_name = re.sub(r"&.*?;", '', c_name)

				c_list.append(c_name)

				companies_list.append(c_list)
				i+=1
				                                                                                                                                                            
			print "Please choose the company department:"
			for company in companies_list:
				print str(company[0]) + " - " + str(company[2])
			chosen = raw_input()
			
			for company in companies_list:
				if int(company[0]) == int(chosen):
					return company[1]
		except:
			print "Error"
		
	def find_contacts(self):
		request = 'https://www.linkedin.com/vsearch/pj?f_CC=' + str(self.companyId)
		response = self.session.get(request)
		response = json.loads(response.text)['content']
		resultCount = response['page']['voltron_unified_search_json']['search']['formattedResultCount'].replace(',','').replace('.','')
		
		print ("There are: " + str(resultCount) + " contacts on the web")	

		pageNum = 1
		contactCount = 0 
		contacts_list = []

		if int(resultCount)%10 == 0:   
			pageEnd = int(resultCount)/10
		else:
			pageEnd = int(resultCount)/10 + 1

		while (pageNum <= 100) and (pageEnd != 0): 
			try: 
				dictOfResults = response['page']['voltron_unified_search_json']['search']['results']
					
				for person in dictOfResults:
					try:	
						p = person['person']

						p_list = []

						contact_firstName = p['firstName'].encode('ascii', 'ignore')
						p_list.append(contact_firstName)
						
						contact_lastName = p['lastName'].encode('ascii', 'ignore')
						p_list.append(contact_lastName)

						job = re.sub('<[a-zA-Z ="/]+>', '', p['fmt_headline'].encode('ascii', 'ignore'))
						job = re.sub(r"&.*?;", '', job)
						p_list.append(job)

						contact_url = re.sub('<[a-zA-Z ="/]+>', '', p['link_nprofile_view_4'].encode('ascii', 'ignore')).split('&')[0]
						p_list.append(contact_url)
											
						if (contact_firstName != "") or (contact_lastName != ""):
							contacts_list.append(p_list)
							contactCount += 1
							p_list = []
					except:
						pass

				pageNum +=1
				pageEnd -=1

				string = 'https://www.linkedin.com/vsearch/pj?f_CC=' + str(self.companyId) + '&page_num=' + str(pageNum)
				response = self.session.get(string)
				response = json.loads(response.text)['content']
			except:
				pass
				pageNum +=1
				pageEnd -=1

		print str(contactCount) + "  contacts were added to the DB"
		return contacts_list

	def createSqliteTable(self):
		list_array = []
		for item in self.links_array:
			array = (None,item[0]+" "+item[1],item[2],"","",item[3],"","","","","",self.moudle)
			list_array.append(array)
		return list_array