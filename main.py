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
import os
import webapp2
import jinja2
import json
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class DictModel(db.Model):
    def to_dict(self):
       return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
       
class Blog(DictModel):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):

    def render_front(self, title="", entry="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
    	self.render("front.html", title=title, entry=entry, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title") 
        entry = self.request.get("entry")
        if title and entry:
            e = Blog(title = title, entry = entry)
            e.put()
            self.redirect("/blog/newpost")
        else:
        	error = "we need both a title and an entry!" 
        	self.render("front.html", error = error)

class NewBlogPage(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        self.render("newpost.html", blogs=blogs)

class MainJson(Handler):

    def get(self):
        #blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC")
        blogs = Blog.all()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.body = json.dumps([blog.to_dict() for blog in blogs])
        self.response.set_status(200)

app = webapp2.WSGIApplication([
    ('/blog', MainPage), 
    ('/blog/newpost', NewBlogPage),
    ('/blog.json', MainJson)
], debug=True)
