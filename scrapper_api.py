from flask import Flask
from flask import jsonify
from flask import make_response
from flask_httpauth import HTTPBasicAuth
from urllib.error import HTTPError,URLError
from flask import request
from linked_in_scrapper import Linked_in_scraper
from facebook_scrapper import Facebook_scraper

auth = HTTPBasicAuth()
app = Flask(__name__)

scraper_api_base_url = '/scraper/api/v1.0'

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def scrape_linkedin_profile(profile_name):
    linkedin_page = Linked_in_scraper(profile_name)
    return linkedin_page.scrape_one_profile(profile_name)

def scrape_facebook_profile(profile_name):
    facebook_page = Facebook_scraper(profile_name)
    return facebook_page.scrape_one_profile(profile_name)

@app.route('/scraper/api/v1.0/linkedin_profile', methods=['GET'])
def get_linkedin_profile():
    try:
        if 'name' in request.args:
            print(request.args['name'])
            return scrape_linkedin_profile(request.args['name'])
    except HTTPError as e:
        print(e.code)
        return str(e) + 'HTTPError'
    except URLError as e:
        print(e.args)
        return str(e) + 'Url Error'

@app.route('/scraper/api/v1.0/facebook_profile', methods=['GET'])
def get_facebook_profile():
    try:
        if 'name' in request.args:
            print(request.args['name'])
            return scrape_facebook_profile(request.args['name'])
    except HTTPError as e:
        print(e.code)
        return str(e) + 'HTTPError'
    except URLError as e:
        print(e.args)
        return str(e) + 'Url Error'

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1',debug=True)