import mechanize 
import sys
import urllib
import urllib2
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as bs_parse
from re import findall
from bs4 import Comment
import requests
import collections, urlparse , json
from Controller import Controller
import re
import getpass

class Facebook(object):

    def __init__(self,domain):
        try:
            self.domain         = domain
            self.moudle         = "Facebook"
            self.db             = Controller(domain)
            self.db_table       = 'contacts_t'
            print "### Moudle -> "+self.moudle+" ###"
            self.temp_arr       = []
            self.links_array    = []
            self.fbSession        = self.loginToFacebook()
            self.companyUrl     = self.findCompanyInFacebook()
            if self.companyUrl != "":
                self.contacts_array    = self.findContactsFromFacebookThroughtViewSource()
                if len(self.contacts_array) == 0:
                    print "no contact has been found"
                elif len(self.contacts_array) < 12:
                    pass
                else:
                    self.findContactsFromFacebookThroughtCursor()
            else:
                print "Unable to search - please try log in with different user"
            self.sqlite_array   = self.createSqliteTable()
            self.db.insertData(self.db_table,self.sqlite_array)
            self.db.printBeautifulTable(self.db_table)
        except:
           print "ERROR: Can't 'run' Facebook moudle"

    def loginToFacebook(self):
        email = raw_input("Please insert your email: ")
        password = getpass.getpass("Please insert your password: ")

        fbUrl = "https://www.facebook.com/login" 
        session = mechanize.Browser() 
        session.set_handle_robots(False)
        
        session.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'), ('Accept', '*/*')]
        session.open(fbUrl)  
        
        session.select_form(nr=0) 
        session.form["email"] = email 
        session.form["pass"] = password
        session.submit() 

        if session.title() != "Facebook":
            print "Name or pass Wrong!"
            sys.exit()
        else:
            print "Facebook Login Success!"
            return session


    def findCompanyInFacebook(self):
        searchCompanyUrl = "https://www.facebook.com/search/str/" + self.domain + "/keywords_places"
        htmltext = self.fbSession.open(searchCompanyUrl).read()
        url = ""
        soup = BeautifulSoup(htmltext)

        companies = []
        
        companies.append(['0',self.domain.split('.')[0]])
        comments = soup.find_all(text=lambda text:isinstance(text, Comment))
        i=1
        for comment in comments:
            comment_soup = BeautifulSoup(comment)
            links = comment_soup.find_all('div', attrs={'class':'_5d-5'})
            if links:
                for link in links:
                    c_list = []
                    link = re.sub('<div class="_5d-5">', '', str(link))
                    link = re.sub('</div>', '', str(link))
                    link = re.sub(r"&.*?;", '', link)
                    if link not in str(companies):                        
                        c_list.append(i)
                        c_list.append(link)
                        companies.append(c_list)
                        i+=1 

                  
        for company in companies:
            print  str(company[0]) + " - " + str(company[1])

        choosenCompany = raw_input("choose the company you reffer to: ")  
        
        for company in companies:
            if int(company[0]) == int(choosenCompany):
                companyName = company[1]


        companyName = companyName.replace(' ','%20')

        companyUrl = "https://www.facebook.com/search/str/People%20who%20work%20at%20"+companyName+"/keywords_top"

        htmltext = self.fbSession.open(companyUrl).read()

        soup = BeautifulSoup(htmltext)

        comments = soup.find_all(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment_soup = BeautifulSoup(comment)
            company = comment_soup.find_all('div', attrs={'class':'clearfix _42ef'})
            company1 = comment_soup.find_all('footer', attrs={'class':'_2avf'})
            if company:
                soup2 = BeautifulSoup(str(company[0]))
                for tag in soup2.findAll('a', href=True):
                    url_contacts = tag['href']
                    url = "https://www.facebook.com" + url_contacts
            if company1:
                soup2 = BeautifulSoup(str(company1[0]))
                for tag in soup2.findAll('a', href=True):
                    url_contacts = tag['href']
                    url = "https://www.facebook.com" + url_contacts
        return url  
    
    def findContactsFromFacebookThroughtViewSource(self):

        htmltext = self.fbSession.open(self.companyUrl).read()

        
        contacts = []
        pattern_name = r'5d-5">(.*?)\<'
        contact_name = re.findall(pattern_name, htmltext)
        
      
        pattern_url = r'<div class="_gll"><a href="(.*?)ref=br_rs">'
        contact_url = re.findall(pattern_url, htmltext)
      
        pattern_job = r'<div class="_pac" data-bt="&#123;&quot;ct&quot;:&quot;sub_headers&quot;&#125;">(.*?) data-gt='
        contact_job = re.findall(pattern_job, htmltext)

        for i in range(0,len(contact_name)):
            try:
                con = []
                if 'Works at' in contact_job[i]:
                    contact_job2 = "No job title"
                else:
                    contact_job1 = str(contact_job[i].split('/')[4])
                    contact_job2 = contact_job1.replace('-', " ").replace("Works at", "")
                print contact_name[i] + " , " + contact_url[i] + " , " + contact_job2   
                con.append(str(contact_name[i]).replace("?",""))
                con.append(contact_url[i])
                con.append(contact_job2) 
                contacts.append(con) 
            except:
                pass
       
        return contacts

    def findContactsFromFacebookThroughtCursor(self):
        try:
            htmltext = self.fbSession.open(self.companyUrl).read()
                
            pattern_name = r'5d-5\\">(.*?)\\\u003C'
            pattern_url = r'class=\\"_8o _8s lfloat _ohe\\" href=(.*?)\?'
            pattern_job = r'class=\\"_pac\\" data-bt=\\"&#123;&quot;ct&quot;:&quot;sub_headers&quot;&#125;\\">(.*?)\?'
            pattern_cursor = r'cursor":"(.*?)\,"display_params"'
           
            view_query = findall(r'{"view".*\[\]}', htmltext)[0][:-1]
            user_query = '&__usr={0}&__a=1&__dyn=7nmajEyl35xKt2u6aOGeFxq9ACxO4oKAdy8VFLFwxBxCbzES2N6xES2N6xybxu3fzoaUjUkUgx-J0&__req=a&__rev=1666949'.format(findall(r'"viewer":(\d+)', htmltext)[0])
            cursor_query = '{0}:null'.format(findall(r'"cursor".*"tr"', htmltext)[0]) + '}' 
                
            request = 'https://www.facebook.com/ajax/pagelet/generic.php/BrowseScrollingSetPagelet?data={0},{1}{2}'.format(view_query, cursor_query, user_query)
               
            while True:  
                req = self.fbSession.open(request).read()
                c_list = []
                get_contact_name = re.findall(pattern_name,req)
                get_contact_url = re.findall(pattern_url,req)
                get_contact_job = re.findall(pattern_job, req)
                
                contact_url = str(get_contact_url[0]).replace("\\", "").replace('"',"")

                if 'Works at' in get_contact_job[0]:
                    contact_job2 = "No job title"
                else:
                    contact_job1 = str(get_contact_job[0].split('/')[4])
                    contact_job2 = contact_job1.replace('-', " ").replace("Works at", "").replace("\\","")
                       
                print get_contact_name[0] + " , " + contact_url + " , " + contact_job2
                
                c_list.append(get_contact_name[0])
                c_list.append(contact_url)
                c_list.append(contact_job2)
                self.contacts_array.append(c_list)       
                    
                get_cursor =  re.findall(pattern_cursor, req)
                cursor_query = '"cursor":"' + str(get_cursor[0]) + '}'
                      
                request = 'https://www.facebook.com/ajax/pagelet/generic.php/BrowseScrollingSetPagelet?data={0},{1}{2}'.format(view_query, cursor_query, user_query)
                
            return self.contacts_array
        except:
            pass

    def createSqliteTable(self):
        list_array = []
        for item in self.contacts_array:
            array = (None,item[0],item[2],"","","",item[1],"","","","",self.moudle)
            list_array.append(array)
        return list_array

Facebook = Facebook('teslamotors.com')