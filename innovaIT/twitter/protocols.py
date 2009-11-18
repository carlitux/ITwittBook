#!/usr/bin/env python
#coding:utf-8
# Author: Luis Carlos Cruz
# Purpose: 
# Created: 13/10/09

from innovaIT.utils import BaseHandler
from innovaIT.utils import OAuthDataStore
from innovaIT.utils import RequestToken
from innovaIT.utils import login_required
from innovaIT.utils import authorize_required

from oauth.core import OAuthConsumer
from oauth.twitter import OAuthTwitter


SERVICE = 'Twitter'

class BaseTwitterHandler(BaseHandler):
    
    def __init__(self, *arg, **karg):
        BaseHandler.__init__(self, *arg, **karg)
        
        # require config variable using tornado
        self.require_setting("twitter_consumer_key", "Twitter OAuth")
        self.require_setting("twitter_consumer_secret", "Twitter OAuth")
        self.require_setting("twitter_callback_url", "Twitter OAuth")
        
        # oauth object instances
        self._oauth_consumer = OAuthConsumer(self.settings["twitter_consumer_key"],
                                             self.settings["twitter_consumer_secret"])
        self._oauth_datastore = OAuthDataStore.get_or_insert("user", user=self.current_user,
                                                             service=SERVICE)
        
        self._oauth_client = OAuthTwitter(self._oauth_consumer)
        self._oauth_client.set_callback_url(self.settings["twitter_callback_url"])
        self._oauth_client.oauth_datastore = self._oauth_datastore
    
    def _get_twitter_oauth(self):
        return self._oauth_client
        
    
    oauth_client = property(_get_twitter_oauth)


# TODO: If an OAuthError is raised return an 404 response
class TwitterLoginHandler(BaseTwitterHandler):
    @login_required
    def get(self):
        if self.oauth_client.is_authorized():
            url = ''.join([self.request.protocol, '://', self.request.host, '/'])
        else:
            url, token = self.oauth_client.fetch_for_authorize()
            data = RequestToken.get_or_insert("user", user=self.current_user, service=SERVICE)
            data.save_token(token)
        self.redirect(url)

        
# TODO: If an OAuthError is raised return an 404 response
class TwitterAccessTokenHandler(BaseTwitterHandler):
    @login_required
    def get(self):
        """Fetch for access token"""
        if not self.oauth_client.is_authorized():
            token_key = self.get_argument("oauth_token", None)
            token = RequestToken.get_or_insert("user", user=self.current_user, service=SERVICE)
            if token.oauth_key == token_key:
                self.oauth_client.fetch_access_token(token.lookup_token())
            else:
                self.redirect('../login')
                return
        self.redirect('/')

class TwitterLogoutHandler(BaseHandler):
    def get(self):
        self.oauth_client.deauthorize()
        self.redirect('/')
    
class TwitterProfileHandler(BaseTwitterHandler):
    @login_required
    @authorize_required
    def get(self):
        self.write(self.oauth_client.fetch_resource('https://twitter.com/account/verify_credentials.json').read())
    
class TwitterTimelineHandler(BaseTwitterHandler):
    @login_required
    @authorize_required
    def get(self):
        self.write(self.oauth_client.fetch_resource('https://twitter.com/statuses/friends_timeline.json').read())
    
    @login_required
    @authorize_required
    def post(self):
        data = {'status': _utf8_str(self.get_argument("status"))}
        self.write(self.oauth_client.fetch_resource('https://twitter.com/statuses/update.json', data, "POST").read())

class TwitterStreamTimelineHandler(BaseTwitterHandler):
    @login_required
    @authorize_required
    def get(self):
        self.write(self.oauth_client.get_signed_url('http://stream.twitter.com/1/statuses/filter.json').to_url())

def _utf8_str(s):
    """Convert unicode to utf-8."""
    if isinstance(s, unicode):
        return s.encode("utf-8")
    else:
        return str(s)