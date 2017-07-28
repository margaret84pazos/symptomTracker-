import webapp2
import jinja2
import os
import logging #going to let you log certain things to the console. useful for debugging

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
    symptom_key = ndb.KeyProperty(kind = Symptom)
    time = ndb.DateTimeProperty(auto_now_add = True)
    severity = ndb.IntegerProperty()
    profile_key = ndb.KeyProperty(kind = Profile)
    comment = ndb.StringProperty()

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
        profile = profile_query.get() #looks up all profiles matching to an email

        # Get the symptom name
        newSymp = self.request.get('newSymp') #string you get out of a request
        # create symptom
        symptom = Symptom(nameSymp = newSymp, profile_key= profile.key)
        # put it in datastore
        symptom.put()
        self.redirect('/Symptom_List')

class ReportHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user() #userobject
        # Get the profile key
        profile_query = Profile.query(Profile.username == current_user.email())
        profile = profile_query.get()
        #symptom key
        symptom_query = Symptom.query(Symptom.profile_key == profile.key).order(-Symptom.postTime)
        symptoms = symptom_query.fetch()

        template = jinja_environment.get_template("templates/report.html")
        self.response.write(template.render(symptoms=symptoms))
    def post(self):
        current_user = users.get_current_user()
        profile_query = Profile.query(Profile.username == current_user.email())
        profile = profile_query.get()

        # Get the list of symptoms for this users
        symptom_query = Symptom.query(Symptom.profile_key == profile.key).order(-Symptom.postTime)
        symptoms = symptom_query.fetch()
        # For each symptom, look up the severity
        #for symptom,severity in self.request()
        for symptom in symptoms:
            severity = self.request.get(symptom.nameSymp)
            logging.info (symptom.nameSymp + " is " + severity)
            if severity != "":
            # and create a new report in datastore
                report = Report(severity = int(severity), profile_key = profile.key, symptom_key = symptom.key)
                report.put()
        self.redirect('/Report')
class ChartHandler(webapp2.RequestHandler):
    def get(self):
            template = jinja_environment.get_template("templates/charts.html")
            points = "['Dates', 'Severity'],"

            # symptom_query = Symptom.query(Symptom.profile_key == profile.key).order(-Symptom.postTime)
            # symptoms = symptom_query.fetch()

            symptom_key = self.request.get('key')
            symptom = ndb.Key(urlsafe=symptom_key)

            reports = Report.query().filter(Report.symptom_key == symptom).fetch()

            for report in reports:
                points = points + '[' + '\''   + str(report.time) +  '\',' + str(report.severity) +'],'

            template_vars = {
            'points': points
            }

            self.response.write(template.render(template_vars))


        # template_vars = {
        #     'symptom_key'=symptom_key,
        #     'profile_key'= profile_key,
        #
        # }
        # 1. Read info from db
        # 2. write info as string
        # 3. Build data as js array
        # 4. Add array to template
        # ['Date', 'Severity']
        #     ['2004',  6],
        #     ['2005',  9],
        #     ['2006',  2],
        #     ['2007',  6]



    #def post(self):




app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/profile', ProfileHandler),
    ('/Symptom_List', Symptom_ListHandler),
    ('/Report', ReportHandler),
    ('/charts', ChartHandler)
], debug=True)
