from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen
from urllib.error import HTTPError,URLError
import urllib
from multiprocessing import Pool
from fake_useragent import UserAgent
from flask import jsonify
from pymongo import MongoClient

class Linked_in_scraper:

    
    def get_user_profile_urls(self):
        soup = BeautifulSoup(self.search_page_source,'html.parser')
        user_profiles = soup.find_all('a', attrs={'class':'profile-img'})
        user_profile_urls = [a.attrs.get('href') for a in user_profiles]
        return user_profile_urls

    def get_profile_data(self,user_profile_url):

        profile_data = {}
        try:
            urlopener= urllib.request.build_opener()
            urlopener.addheaders = [('User-agent', UserAgent().random)]
            profile_page_source = urlopener.open(user_profile_url).read()
        
            soup = BeautifulSoup(profile_page_source,'html.parser')
            profile_data['Title'] = soup.title.string
            profile_data['Profile'] = soup.find('div',attrs={'id':'profile'})

        except:
            pass

        return profile_data

    def search_profile(self):
        urlopener= urllib.request.build_opener()
        urlopener.addheaders = [('User-agent', "Mozilla/5.0 Chrome/39.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3")]
        self.search_page_source = urlopener.open('https://www.linkedin.com/pub/dir/?first=isuru&last=&trk=uno-reg-guest-home-name-search&search=Search').read()
        
        profile_details = []
        for user_profile in user_profiles:
            profile_details.append([self.get_profile_data(user_profile)])
#        pool = Pool(4)
#        user_profiles = self.get_user_profile_urls()
#        profile_details = pool.map(self.get_profile_data, user_profiles)
        return str(profile_details)


    def insert_data_in_database(self, user_data):
        client = MongoClient("mongodb://admin:admin@ds153765.mlab.com:53765/asidsocialmedia")
        db = client.asidsocialmedia
        linkedin_collection = db.linked_in
        inserted_user_profile = linkedin_collection.insert_one(user_data)
        return "New record " + str(inserted_user_profile.inserted_id) + " was inserted successfully"

    def scrape_profile_div(self,user_profile_url):

        urlopener= urllib.request.build_opener()
        urlopener.addheaders = [('User-agent', UserAgent().random)]
        profile_page_source = urlopener.open(user_profile_url).read()
        soup = BeautifulSoup(profile_page_source, 'html.parser')

        user_profile = {}
        name = soup.find('h1', attrs={'class':'fn','id':'name'})
        user_profile['name'] = name.text

        profile_picture = soup.find('div', attrs={'class':'profile-picture'})
        if(profile_picture != None):
            user_profile['profile_picture'] = profile_picture.a.img['data-delayed-url']

        education = soup.find('ul',attrs={'class':'schools'})
        if(education != None):
            school_list = []
            for school in education.children:
                school_data = {}
                school_header = school.header
                for child in school_header:
                    if(child['class']==['item-title']):
                        school_data['school'] = child.text
                    elif(child['class']==['item-subtitle']):
                        for subtitle_child in child:
                            if(subtitle_child['class']==['original','translation']):
                                school_data['course'] = subtitle_child.text
                            else:
                                continue
                    else:
                        continue
                school_list.append(school_data)
            user_profile['education'] = school_list

        awards = soup.find_all('li',attrs={'class':'award'})
        if(awards != None):
            awards_list = []
            for award in awards:
                award_data = {}
                award_header = award.header
                for child in award_header:
                    if(child['class']==['item-title']):
                        award_data['award'] = child.text
                    elif(child['class']==['item-subtitle']):
                        award_data['organisation'] = child.text
                    else:
                        continue
                awards_list.append(award_data)
            if len(awards_list) != 0:
                user_profile['awards'] = awards_list


        skills = soup.find_all('li',attrs={'class':'skill'})
        if(skills != None):
            skills_list = []
            for skill in skills:
                if((skill['class']==['skill', 'see-more'])|(skill['class']==['skill', 'see-less', 'extra'])):
                    continue
                else:
                    skills_list.append(skill.text)
            user_profile['skills'] = skills_list

        positions = soup.find('ul',attrs={'class':'positions'})
        if(positions != None):
            positions_list = []
            for position in positions:
                position_data = {}
                position_header = position.header
                for child in position_header:
                    if(child['class']==['item-title']):
                        position_data['position'] = child.text
                    elif(child['class']==['item-subtitle']):
                        position_data['organisation'] = child.text
                    else:
                        continue
                positions_list.append(position_data)
            user_profile['experience'] = positions_list
        
        projects = soup.find_all('li',attrs={'class':'project'})
        if(projects != None):
            projects_list = []
            for project in projects:
                project_data = {}
                project_data['project'] = project.header.text
                projects_list.append(project_data)

            if len(projects_list) != 0:
                user_profile['projects'] = projects_list

        organisations = soup.find('section',attrs={'id':'organizations'})
        if(organisations != None):
            organisations_list = []
            for organisation in organisations.ul.children:
                organisations_list.append(organisation.header.text)

            if len(organisations_list) != 0:
                user_profile['organisations'] = organisations_list

        languages = soup.find_all('li', attrs={'class': 'language'})
        if(languages != None):
            languages_list = []
            for language in languages:
                for child in language.div.children:
                    if(child['class']==['name']):
                        languages_list.append(child.text)
                    else:
                        continue
            if len(languages_list) != 0:
                user_profile['languages'] = languages_list

        user_profile['linkedin'] = user_profile_url
        user_profile['matched'] = False

        return self.insert_data_in_database(user_profile)

    def scrape_one_profile(self,profile_url):
        return self.scrape_profile_div(profile_url)

    def __init__(self, profile_name):
        self.profile_name = profile_name
