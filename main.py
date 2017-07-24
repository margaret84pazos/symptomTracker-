import webapp2
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


from google.appengine.api import users
from google.appengine.ext import ndb


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(template.render(template_vars)

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
