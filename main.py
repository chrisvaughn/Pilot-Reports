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

import os, re, base64, logging, uuid
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users as google_users
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from models import Users

token_length = 10

class MainHandler(webapp.RequestHandler):
	""" handler for / """
	def get(self):
		""" this handler supports http get """
		data = {}
		if google_users.get_current_user():
			google_user = google_users.get_current_user()
			user = db.Query(Users).filter('user_id =', google_user.user_id()).get()
			if user is None:
				token = generate_token(token_length)
				user = Users(user_id = google_user.user_id(), email = google_user.email(), token = token)
				db.put(user)

			data['url'] = google_users.create_logout_url(self.request.uri)
			data['user'] = google_users.get_current_user()
			data['user_token'] = user.token

		else:
			data['url'] = google_users.create_login_url(self.request.uri)

		path = os.path.join(os.path.dirname(__file__), 'home.html')
		self.response.out.write(template.render(path, data))


def generate_token(token_length):
	u = uuid.uuid4()
	return u.bytes.encode("base64")[:token_length]

def main():
	application = webapp.WSGIApplication([('/', MainHandler)],
										 debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
