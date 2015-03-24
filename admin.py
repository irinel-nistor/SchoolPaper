#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import users
import webapp2
import os
from google.appengine.ext.webapp import template

import cgi
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.api import mail

import test
import datetime

def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

def test_key(test_name=None):
  """Constructs a datastore key for a Test entity with test_name."""
  return db.Key.from_path('Test', test_name or 'default_test')

class AdminHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if not users.is_current_user_admin():
               self.redirect('/')

            testQuery = test.Test.all()
            testQuery.filter("supervizor =", users.get_current_user())
            tests = testQuery.fetch(1)

            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            template_values = {
               'url': url,
               'url_linktext': url_linktext
            }
            for item in tests:
               template_values['test'] = item
               break

            path = os.path.join(os.path.dirname(__file__), 'Views/admin.html')
            self.response.out.write(template.render(path,template_values))

        else:
            self.redirect(users.create_login_url(self.request.uri))

class StartHandler(webapp2.RequestHandler):
    def post(self):

        test1 = test.Test()
        
        user = users.get_current_user()
        test1.supervizor = user

        test1.question1 = "What is the speed of light in Km/s"
        test1.answer1 = "300000"
        test1.points1 = 1
        test1.question2 = "Which is the largest planet in the Solar System"
        test1.answer2 = "Jupiter"
        test1.points2 = 1
        test1.question3 = "What is the distance to the Moon in km"
        test1.answer3 = "380000"
        test1.points3 = 2

        test1.passingGrade = 2
        
        test1.startTime = datetime.datetime.now()
        test1.put()
        self.redirect(self.request.referer)

        
class EndHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            testQuery = test.Test.all()
            testQuery.filter("supervizor =", user)
            tests = testQuery.fetch(1)

            template_values = {}
            for item in tests:
               item.delete()
               break

            resultQuery = test.Result.all()
            resultQuery.filter("supervizor =", user)
            results = resultQuery.fetch(30)

            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'

            template_values = {
               'url': url,
               'url_linktext': url_linktext,
               'results': results
            }

            path = os.path.join(os.path.dirname(__file__), 'Views/result.html')
            self.response.out.write(template.render(path,template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))


class SendEmailPage(webapp2.RequestHandler):
    def post(self):

        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return

        resultQuery = test.Result.all()
        resultQuery.filter("supervizor =", user)
        results = resultQuery.fetch(30)

        emails_sent = 0
        for result in results:
            if result.attendee:
                user_address = result.attendee.email()
            else:
                continue

            if not mail.is_email_valid(user_address):
                pass
            else:
                emails_sent += 1
                grade = result.grade
                passed = result.passed

                if passed:
                    message = " and you passed the test"
                else:
                    message = " and I'm sorry, you didn't pass the test"

                sender_address = user.email()
                subject = "Test result"
                body = """
Your grade is %s
""" % grade 
                body += message

                mail.send_mail(sender_address, user_address, subject, body)

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(str(emails_sent) + ' where sent' + body)

app = webapp2.WSGIApplication([
    ('/admin', AdminHandler),
    ('/admin/start', StartHandler),
    ('/admin/end', EndHandler),
    ('/admin/send', SendEmailPage)
], debug=True)

def main():
    application.run()

if __name__ == "__main__":
    main()
