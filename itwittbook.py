import os.path
import wsgiref.handlers

from tornado import web
from tornado import wsgi
from tornado.options import define
from tornado.options import options

from innovaIT.utils import BaseHandler, login_required
from innovaIT.twitter import *
from innovaIT.facebook import *

# Define some options
define("facebook_api_key", help="", default="14fcd5a9bedc8f9dbb7646daf7783c7e")
define("facebook_secret", help="", default="6b2a47a6c0dedfb2cdebf8772308ef0b")
define("facebook_callback_url", help="", default="http://carlitos-dev.appspot.com/facebook/save/")

define("twitter_consumer_key", help="", default="rU023o2GC4m8ExC0s1I7fQ")
define("twitter_consumer_secret", help="", default="08LwWhvuH8enBPpkgJ3YMkdm2qD9SJon6byVS3sbE")
define("twitter_callback_url", help="", default="http://carlitos-dev.appspot.com/twitter/save/")


class IndexHandler(BaseHandler):
    @login_required
    def get(self):
        self.render('twitbook.html', title="ITwittBook App")

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
    "cookie_secret":"61oETzKXQYGaYdhL5gEsGeJJFuY87EQnp2XdTP1o/Vo=",
}

application = wsgi.WSGIApplication([
    (r"^/?$", IndexHandler),
    
    (r"^/twitter/?$", TwitterTimelineHandler),
    (r"^/twitter/login/?$", TwitterLoginHandler),
    (r"^/twitter/save/?$", TwitterAccessTokenHandler),
    (r"^/twitter/profile/?$", TwitterProfileHandler),
    
    (r"^/facebook/?$", FacebookStreamHandler),
    (r"^/facebook/login/?$", FacebookLoginHandler),
    (r"^/facebook/save/?$", FacebookSessionHandler),
    (r"^/facebook/profile/?$", FacebookProfileHandler),
    
    #(r"^/facebook/?$", StreamHandler),
], **settings)


def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()