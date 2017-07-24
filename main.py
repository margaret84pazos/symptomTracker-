import webapp2
import jinja2
import os

from google.appengine.api import users
#appengine
from google.appengine.ext import ndb

class Profile(ndb.Model):
    name = ndb.StringProperty()
    sex = ndb.StringProperty()
    age = ndb.StringProperty()
    weight = ndb.StringProperty()
    symptoms = ndb.StringProperty()

class Symptoms(ndb.Model):
    nameSymp = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add = True)
    severity = ndb.IntegerProperty()

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        logout_url = users.create_logout_url('/')
        login_url = users.create_login_url('/')

        template_vars = {
            'current_user': current_user,
            'logout_url': logout_url,
            'login_url': login_url
        }

        template = jinja_environment.get_template("templates/home.html")
        self.response.write(template.render(template_vars))


class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        profile_query = Profile.query()
        profileInfo = profile_query.fetch()
        template_vars = {
            'profileInfo': profileInfo
        }

        template = jinja_environment.get_template("templates/profile.html")
        self.response.write(template.render(template_vars))

    #def post(self):
        #1. Get the information submitted in the form.
        #name = self.request.get("name")
        #sex = self.request.get("sex")
        #age = self.request.get("age")
        #weight = self.request.get("weight")
        #symptoms = self.request.get("symptoms")

        #profile = Profile(name =  name, sex = sex, age = age, weight = weight, #symptoms = symptoms)

        #profile.put()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/profile', ProfileHandler)
], debug=True)
