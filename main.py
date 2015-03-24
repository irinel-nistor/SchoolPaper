import os
from google.appengine.ext.webapp import template

import cgi
import datetime
import urllib
import wsgiref.handlers

import test

from google.appengine.ext import db
from google.appengine.api import users
import webapp2


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
  def get(self):

    user = users.get_current_user()

    if user:
        if users.is_current_user_admin():
           self.redirect('admin')  

        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        testsQuery = test.Test.all()
        tests = testsQuery.fetch(10)

        template_values = {
            'tests': tests,
            'url': url,
            'url_linktext': url_linktext,
        }

        path = os.path.join(os.path.dirname(__file__), 'Views/index.html')
        self.response.out.write(template.render(path, template_values))
    else:
        self.redirect(users.create_login_url(self.request.uri))

class TestPage(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    user = users.get_current_user()

    if user:
    
        key = self.request.get('test-key')
        q = test.Test.all()
        q.filter('__key__ =',db.Key(key))
        tests = q.fetch(1)

        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'


        template_values = {
           'url': url,
           'url_linktext': url_linktext
        }
        for item in tests:
            template_values['test'] = item
            break

        path = os.path.join(os.path.dirname(__file__), 'Views/test.html')
        self.response.out.write(template.render(path, template_values))
    else:
        self.redirect(users.create_login_url(self.request.uri))


class CorrectPage(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    user = users.get_current_user()

    if user:
        answer1 = self.request.get('answer1')
        answer2 = self.request.get('answer2')
        answer3 = self.request.get('answer3')

        key = self.request.get('test-key')
     
        q = test.Test.all()
        q.filter('__key__ =',db.Key(key))
        tests = q.fetch(1)

        for item in tests:
           attendedTest = item
           break

        response = attendedTest.correct(answer1,answer2,answer3)
        response.attendee = user
        response.supervizor = attendedTest.supervizor
        response.put()
        self.redirect('/send')
    else:
        self.redirect(users.create_login_url(self.request.uri))
  
  def get(self):
    user = users.get_current_user()
    if user:
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('You will recive an email with the result')
    else:
        self.redirect(users.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/send', CorrectPage),
  ('/attend', TestPage)
], debug=True)


def main():
  application.run()


if __name__ == '__main__':
  main()
