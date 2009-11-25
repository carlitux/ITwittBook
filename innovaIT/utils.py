##################################################################################
##
## The MIT License
## 
## Copyright (c) 2009 Luis C. Cruz
## 
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to deal
## in the Software without restriction, including without limitation the rights
## to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
## copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
## 
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
## 
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
## OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
## THE SOFTWARE.
##
##################################################################################

import oauth

from tornado import web
from google.appengine.api import users
from google.appengine.ext import db

SERVICES = ("Twitter", "Facebook")

def login_required(method):
    """A decorator that control if a user is logged."""
    def wrapper(self, *arg, **karg):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
            else:
                raise web.HTTPError(403)
        else:
            method(self, *arg, **karg)
    return wrapper

def authorize_required(method):
    """A decorator that control if a user is authorized to access private data."""
    def wrapper(self, *arg, **karg):
        if not self.oauth_client.is_authorized():
            raise web.HTTPError(403)
        else:
            method(self, *arg, **karg)
    return wrapper

class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        return users.get_current_user()
    
    def get_login_url(self):
        return users.create_login_url(self.request.uri)
    
    #def render_string(self, template_name, **kwargs):
        ## Let the templates access the users module to generate login URLs
        #return web.RequestHandler.render_string(
            #self, template_name, users=users, **kwargs)
    

class OAuthDataStore(db.Model, oauth.core.OAuthDataStoreMixin):
    """Google app engine model for consumer data."""
    oauth_key    = db.StringProperty()
    oauth_secret = db.StringProperty()
    service      = db.StringProperty(required=True, choices=SERVICES)
    created      = db.DateTimeProperty(auto_now_add=True)
    user         = db.UserProperty(required=True)
    
    def lookup_token(self):
        if self.oauth_key is not None and \
           self.oauth_secret is not None:
            return oauth.core.OAuthToken(self.oauth_key, self.oauth_secret)
        return None
    
    def save_token(self, token):
        self.oauth_secret = token.secret
        self.oauth_key = token.key
        self.put()
    
    def delete_token(self):
        self.oauth_key = None
        self.oauth_secret = None
        self.put()
    
class RequestToken(db.Model, oauth.core.OAuthDataStoreMixin):
    oauth_key    = db.StringProperty()
    oauth_secret = db.StringProperty()
    service      = db.StringProperty(required=True, choices=SERVICES)
    created      = db.DateTimeProperty(auto_now_add=True)
    user         = db.UserProperty(required=True)
    
    def lookup_token(self):
        if self.oauth_key is not None and \
           self.oauth_secret is not None:
            return oauth.core.OAuthToken(self.oauth_key, self.oauth_secret)
        return None
    
    def save_token(self, token):
        self.oauth_secret = token.secret
        self.oauth_key = token.key
        self.put()
    
    def delete_token(self):
        self.oauth_key = None
        self.oauth_secret = None
        self.put()