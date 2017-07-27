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
    #this will be the email
    username = ndb.StringProperty()

class Symptom(ndb.Model):
    nameSymp = ndb.StringProperty()
    profile_key = ndb.KeyProperty(Profile)
    postTime = ndb.DateTimeProperty(auto_now_add=True)

class Report(ndb.Model):
    symptom_key = ndb.KeyProperty(Symptom)
    time = ndb.DateTimeProperty(auto_now_add = True)
    severity = ndb.IntegerProperty()

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        username = None

        if user:
            username = user.email()
            profile = Profile.query(Profile.username == username).get()
            if profile is None:
                profile_key = None
            else:
                profile_key = profile.key
        else:
            profile_key = None

        logout = users.create_logout_url('/')
        login = users.create_login_url('/')

        #if the username is already created, looks up in database by username
        #if it isnt already there, create a profile
            #this has users username

        #creates profile and ties it to the username
        template_vars = {
            'login': login,
            'logout': logout,
            'username': username,
            'profile_key': profile_key
        }
        #login = login, logout=logout, username=username, profile_key = profile_key

        template = jinja_environment.get_template("templates/home.html")
        self.response.write(template.render(template_vars))


class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        urlsafe_key = self.request.get('key')

        current_user = users.get_current_user()
        username = current_user.email()

        if urlsafe_key == "":
            profile = Profile(name =  "", sex = "", age = "", weight = "")
            profile.put()

            profile_query = Profile.query()
            profile_query = profile_query.filter(Profile.username == username)
            profileInfo= profile_query.get()
        else:
            profile_key = ndb.Key(urlsafe=urlsafe_key)
            profile = profile_key.get()

            profile_query = Profile.query()
            profile_query = profile_query.filter(Profile.username == username)
            profileInfo= profile_query.get()

        template_vars = {
            'profileInfo': profileInfo
        }


        template = jinja_environment.get_template("templates/profile.html")
        self.response.write(template.render(template_vars))

    def post(self):
        name = self.request.get('name')
        sex = self.request.get('sex')
        age = self.request.get('age')
        weight = self.request.get('weight')

        current_user = users.get_current_user()
        username = current_user.email()

        profile = Profile(name=name, sex=sex, age=age, weight = weight, username = username)
        profile.put()

        self.redirect('/')

class Symptom_ListHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user() #userobject
        # Get the profile key
        profile_query = Profile.query(Profile.username == current_user.email())
        profile = profile_query.get()

        symptom_query = Symptom.query(Symptom.profile_key == profile.key).order(-Symptom.postTime)
        symptoms = symptom_query.fetch()

        template = jinja_environment.get_template("templates/symptom_list.html")
        self.response.write(template.render(symptoms = symptoms))

    def post(self):
        # Get current user
        # Get the Profile for that user from datastore
        current_user = users.get_current_user() #userobject
        # Get the profile key
        profile_query = Profile.query(Profile.username == current_user.email())
        profile = profile_query.get() #looks up all profiles matching to a nickname

        # Get the symptom name
        newSymp = self.request.get('newSymp') #string you get out of a request
        # create symptom
        symptom = Symptom(nameSymp = newSymp, profile_key= profile.key)
        # put it in datastore
        symptom.put()
        self.redirect('/Symptom_List')


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
    ('/profile', ProfileHandler),
    ('/Symptom_List', Symptom_ListHandler)

], debug=True)
