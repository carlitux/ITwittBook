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

import pyfacebook as facebook

from tornado.escape import json_encode
from datetime import datetime

from innovaIT.utils import BaseHandler
from innovaIT.utils import login_required
from innovaIT.utils import authorize_required

class FakeOauthClient(object):
    """ This class to use the authorize_required method. """
    def __init__(self, handler):
        self._handler = handler
    
    def is_authorized(self):
        time = self._handler.get_secure_cookie("session_key_expires")
        if time:
            time = datetime.fromtimestamp(float(time))
            return self._handler.get_secure_cookie("uid") and \
                   self._handler.get_secure_cookie("session_key") and \
                   time >= datetime.now()
        else:
            return False

class BaseFacebookHandler(BaseHandler):
    
    def __init__(self, *arg, **karg):
        BaseHandler.__init__(self, *arg, **karg)
        
        # require config variable using tornado
        self.require_setting("facebook_api_key", "Facebook connect")
        self.require_setting("facebook_secret", "Facebook connect")
        self.require_setting("facebook_callback_url", "Facebook connect")
        
        # Creating facebook instance and setting as a attribute object
        self.facebook = facebook.Facebook(api_key=self.settings["facebook_api_key"],
                                          secret_key=self.settings["facebook_secret"],
                                          callback_path=self.settings["facebook_callback_url"],
                                          app_name="twitbook",                                          
                                          internal=False)
        
        self.oauth_client = FakeOauthClient(self)
        
        if self.get_secure_cookie("uid") and self.get_secure_cookie("session_key"):
            self.facebook.session_key = self.get_secure_cookie("session_key")
            self.facebook.uid = self.get_secure_cookie("uid")
            self.facebook.session_key_expires = self.get_secure_cookie("session_key_expires")
    

class FacebookLoginHandler(BaseFacebookHandler):
    @login_required
    def get(self):
        if self.oauth_client.is_authorized():
            url = ''.join([self.request.protocol, '://', self.request.host, '/'])
        else:
            url = self.facebook.get_login_url(next=self.facebook.callback_path, canvas=False)
        self.redirect(url)
    
class FacebookProfileHandler(BaseFacebookHandler):
    @login_required
    @authorize_required
    def get(self):
        info = self.facebook.users.getInfo(uids=[self.facebook.uid],
                                           fields=["name", "pic_small"])
        self.write(json_encode(info[0]))
    
class FacebookSessionHandler(BaseFacebookHandler):
    @login_required
    def get(self):
        fb = self.facebook
        try:
            fb.auth_token = self.get_argument("auth_token")
            fb.auth.getSession()
            self.set_secure_cookie("session_key", fb.session_key)
            self.set_secure_cookie("uid", str(fb.uid))
            self.set_secure_cookie("session_key_expires", str(fb.session_key_expires))
            url = '/'
        except:
            url = self.facebook.get_login_url(next=self.facebook.callback_path, canvas=False)
        finally:
            self.redirect(url)
    
class FacebookStreamHandler(BaseFacebookHandler):
    @login_required
    @authorize_required
    def get(self):
        try:
            info = self.facebook.stream.get(viewer_id=self.facebook.uid,
                                            limit=20)
            del info['albums'] # deleting photo posts for simplicity
            self.write(json_encode(info))
        except:
            response = {"redirect": True,
                        "url": self.facebook.get_ext_perm_url('read_stream', next=self.facebook.callback_path)}
            self.write(json_encode(response))
    
    @login_required
    @authorize_required
    def post(self):
        try:
            data = {'status': _utf8_str(self.get_argument("status"))}
            success = self.facebook.status.set(**data)
            info = {'success':success}
            self.write(json_encode(info))
        except facebook.FacebookError:
            response = {"redirect": True,
                        "url": self.facebook.get_ext_perm_url('status_update', next=self.facebook.callback_path)}
            self.write(json_encode(response))
    
def _utf8_str(s):
    """Convert unicode to utf-8."""
    if isinstance(s, unicode):
        return s.encode("utf-8")
    else:
        return str(s)
