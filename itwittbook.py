import os.path
import wsgiref.handlers

from google.appengine.api import users

from tornado import web
from tornado import wsgi
from tornado.options import define
from tornado.options import options

from innovaIT.utils import BaseHandler, login_required
from innovaIT.twitter import *
from innovaIT.facebook import *

# Define some options
define("facebook_api_key", help="", default="your facebook_api_key here")
define("facebook_secret", help="", default="your facebook_secret here")
define("facebook_callback_url", help="", default="your facebook_secret here")
 
define("twitter_consumer_key", help="", default="your facebook_secret here")
define("twitter_consumer_secret", help="", default="your facebook_secret here")
define("twitter_callback_url", help="", default="your facebook_secret here")


class IndexHandler(BaseHandler):
    @login_required
    def get(self):
        self.render('twitbook.html', title="ITwittBook App", url_logout=users.create_logout_url('/'))

settings = {
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    # facebook setup
    "facebook_api_key": options.facebook_api_key,
    "facebook_secret": options.facebook_secret,
    "facebook_callback_url": options.facebook_callback_url,
    # twitter setup
    "twitter_consumer_key": options.twitter_consumer_key,
    "twitter_consumer_secret": options.twitter_consumer_secret,
    "twitter_callback_url": options.twitter_callback_url,
    #"xsrf_cookies": True,
    "debug": True,
    "cookie_secret":"secret cookie",
}

application = wsgi.WSGIApplication([
    (r"^/?$", IndexHandler),
    
    (r"^/twitter/?$", TwitterTimelineHandler),
    (r"^/twitter/login/?$", TwitterLoginHandler),
    (r"^/twitter/save/?$", TwitterAccessTokenHandler),
    (r"^/twitter/profile/?$", TwitterProfileHandler),
    (r"^/twitter/logout/?$", TwitterLogoutHandler),
    
    (r"^/facebook/?$", FacebookStreamHandler),
    (r"^/facebook/login/?$", FacebookLoginHandler),
    (r"^/facebook/save/?$", FacebookSessionHandler),
    (r"^/facebook/profile/?$", FacebookProfileHandler),
    (r"^/facebook/logout/?$", FacebookLogoutHandler),
    
    #(r"^/facebook/?$", StreamHandler),
], **settings)


def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()