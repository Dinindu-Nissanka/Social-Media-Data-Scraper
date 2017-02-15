import sys
import requests
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen
import urllib
from pymongo import MongoClient
from fake_useragent import UserAgent
import lxml
from flask import jsonify

class Facebook_scraper:

    BASE_URL = "https://m.facebook.com/login.php"

    facebook_url = "https://www.facebook.com/"
    url_education = "/about?section=education&pnref=about"
    url_living = "/about?section=living&pnref=about"
    url_contact = "/about?section=contact-info&pnref=about"
    url_relationship = "/about?section=relationship&pnref=about"
    url_events = "/about?section=year-overviews&pnref=about"

    session = None

    def insert_data_in_database(self, user_data):
        client = MongoClient("mongodb://admin:admin@ds153765.mlab.com:53765/asidsocialmedia")
        db = client.asidsocialmedia
        facebook_collection = db.facebook
        inserted_user_profile = facebook_collection.insert_one(user_data)
        return "New record " + str(inserted_user_profile.inserted_id) + " was inserted successfully"
    
    def scrape_profile_div(self,user_profile_url):

        #proxy = urllib.request.ProxyHandler({'http': 'cache.mrt.ac.lk:3128','https':'cache.mrt.ac.lk:3128'})
        urlopener= urllib.request.build_opener()
        #urlopener.addheaders = [('User-agent', UserAgent().random)]
        profile_page_source = urlopener.open(self.BASE_URL).read()
        soup = BeautifulSoup(profile_page_source, 'html.parser')

        hidden_values = soup.find_all('input')
        data_form = dict()
        for x in hidden_values:
            if x.has_attr('value'):
                data_form[x['name']] = x['value']

        data_form['email']="asidcse@yahoo.com"
        data_form['pass']='1qaz2wsx@'
        data_form['login'] = 'Log In'


        s = requests.Session()
        r = s.post(self.BASE_URL, data=data_form)
        r.raise_for_status()

        soup = BeautifulSoup(r.content,'html.parser')

        url_splitted_words= user_profile_url.split("/")
        user_id = url_splitted_words[3].split("?")[0]

        user_education_url = self.facebook_url + user_id + self.url_education
        contents = s.get(user_education_url).content
        soup = BeautifulSoup(contents,'html.parser')

        user_profile = {}

        code = soup.find_all('code')
        for code_block in code:
            comment = code_block.contents[0]
            if not isinstance(comment, Comment):
                continue
            parsed = BeautifulSoup(comment, 'lxml').body.contents[0]
            code_block.replace_with(parsed)

        user_profile['name'] = soup.title.string 
        profile_picture = soup.find('a', attrs={'class':'profilePicThumb'})
        if(profile_picture != None):
            user_profile['profile_picture'] = profile_picture.img['src']

        work = soup.find('div', attrs={'data-pnref':'work'})
        if(work != None):
            work_experience = work.find_all('li', attrs= {'class':['_43c8', '_5f6p','fbEditProfileViewExperience','experience']})
            if(work_experience != None):
                work = []
                for child in work_experience:
                    work_place_data = {}
                    work_place = child.find('div', attrs= {'class':['_21zr','_50f5', '_50f7']})
                    work_place_data['work'] = work_place.text
                    work_place_details = child.find('div', attrs= {'class':['fsm','fwn', 'fcg']})
                    if(work_place_details != None):
                        work_place_data['details'] = work_place_details.text

                    work.append(work_place_data)
            user_profile['work'] = work

        education = soup.find('div', attrs={'data-pnref':'edu'})
        if(education != None):
            edu_experience = education.find_all('li', attrs= {'class':['_43c8', '_5f6p','fbEditProfileViewExperience','experience']})
            if(edu_experience != None):
                education = []
                for child in edu_experience:
                    school_data = {}
                    school = child.find('div', attrs= {'class':['_21zr','_50f5', '_50f7']})
                    school_data['school'] = school.text
                    school_details = child.find('div', attrs= {'class':['fsm','fwn', 'fcg']})
                    if(school_details != None):
                        school_data['details'] = school_details.text

                    education.append(school_data)
                user_profile['education'] = education



        url_living_url = self.facebook_url + user_id + self.url_living
        contents = s.get(url_living_url).content
        soup = BeautifulSoup(contents,'html.parser')
        code = soup.find_all('code')
        for code_block in code:
            comment = code_block.contents[0]
            if not isinstance(comment, Comment):
                continue
            parsed = BeautifulSoup(comment, 'lxml').body.contents[0]
            code_block.replace_with(parsed)

        places = soup.find_all('li', attrs= {'class':['_3pw9', '_2pi4','_2ge8']})
        if(places != None):
            places_lived = []
            for child in places:
                places_data = {}
                city = child.find('span', attrs= {'class':['_50f5', '_50f7']})
                if(city != None):
                    places_data['city'] = city.text
                city_details = child.find('div', attrs= {'class':['fsm','fwn', 'fcg']})
                if(city_details != None):
                    places_data['status'] = city_details.text

                if len(places_data) != 0:
                    places_lived.append(places_data)
                    user_profile['places'] = places_lived

        url_info_url = self.facebook_url + user_id + self.url_contact
        contents = s.get(url_info_url).content
        soup = BeautifulSoup(contents,'html.parser')
        code = soup.find_all('code')
        for code_block in code:
            comment = code_block.contents[0]
            if not isinstance(comment, Comment):
                continue
            parsed = BeautifulSoup(comment, 'lxml').body.contents[0]
            code_block.replace_with(parsed)


        personal_info = soup.find_all('li', attrs= {'class':['_3pw9', '_2pi4','_2ge8']})
        if(personal_info != None):
            for child in personal_info:
                personal_data = {}
                info_type = ''
                info_details = ''
                for sub_child in child.children:
                    if((len(list(sub_child.children))) != 1):
                        info_type = sub_child.find('div',attrs={'class':['_4b17','_3xdi', '_52ju']}).text.lower()
                        info_details = sub_child.find('div',attrs={'class':['_4b17','_pt5']}).text
                        if(info_type == 'languages'):
                            info_details = info_details.replace(" ","")
                            info_details = info_details.split("·")
                        if(info_type == 'mobile phones'):
                            info_type = "mobile"
                        user_profile[info_type] = info_details
        
        url_family_url = self.facebook_url + user_id + self.url_relationship
        contents = s.get(url_family_url).content
        soup = BeautifulSoup(contents,'html.parser')
        code = soup.find_all('code')
        for code_block in code:
            comment = code_block.contents[0]
            if not isinstance(comment, Comment):
                continue
            parsed = BeautifulSoup(comment, 'lxml').body.contents[0]
            code_block.replace_with(parsed)
        
        marital_status = soup.find('div', attrs={'class':['_vb-','_50f5']})
        if(marital_status != None):
            user_profile['marital_status'] = marital_status.text

        #family_members_div = soup.find('div', attrs={'class':'_5h60','id':'family-relationship-pagelet'})
        family_members = soup.find_all('li', attrs={'class':['_43c8','_2ge8']})
        if(family_members != None):
            family_data = []
            for member in family_members:
                member_data = member.find_all('div', attrs={'class':['fsm','fwn','fcg']})
                if(member_data != None):
                    member_data_json = {}
                    for member_data_detail in member_data:
                        if member_data_detail.find('span', attrs={'class':['_50f5', '_50f7']}) != None:
                            member_data_json['name'] = member_data_detail.find('span', attrs={'class':['_50f5','_50f7']}).text
                        else:
                            member_data_json['relation'] = member_data_detail.text

                    family_data.append(member_data_json)
                user_profile['family'] = family_data

        user_profile['facebook'] = self.facebook_url + user_id

        print(user_profile)
        return self.insert_data_in_database(user_profile)

    def scrape_one_profile(self,profile_url):
        return self.scrape_profile_div(profile_url)

    def __init__(self, profile_name):
        self.profile_name = profile_name


