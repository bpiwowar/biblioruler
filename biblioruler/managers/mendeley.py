# Mendeley backend

import logging
import managers
import mendeley
import oauth2 as oauth
import http.server
import socketserver
from subprocess import call

PORT = 5000
CLIENT_ID = "3060"
CLIENT_SECRET = "Ov2qzRIsrpQXFUje"
REDIRECT_URI = "http://localhost:5000"

class StateGenerator():
    def generate_state(self):
        return "1231293jfh2asdn24324wsa"

class AuthException(BaseException):
    def __init__(self, path):
        self.path = path

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Authorization successful.</title></head>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        raise AuthException(self.path)
class Mendeley(managers.Paper):
    def __init__(self):
        m = mendeley.Mendeley(CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, state_generator=StateGenerator())
        auth = m.start_authorization_code_flow()
        login_url = auth.get_login_url()
        httpd = socketserver.TCPServer(("", PORT), Handler)
        call(["open", login_url])

        path = None
        try:
            httpd.serve_forever()
        except AuthException as e:
            path = e.path
        finally:
            httpd.server_close()

        session = auth.authenticate(path)



# import urllib.parse
# import oauth2 as oauth

# consumer_key = CLIENT_ID
# consumer_secret = CLIENT_SECRET

# request_token_url = 'https://api.mendeley.com/oauth/token'
# access_token_url = 'https://api.mendeley.com/oauth/access_token'
# authorize_url = 'https://api.mendeley.com/oauth/authorize'

# consumer = oauth.Consumer(consumer_key, consumer_secret)
# client = oauth.Client(consumer)

# # Step 1: Get a request token. This is a temporary token that is used for
# # having the user authorize an access token and to sign the request to obtain
# # said access token.

# resp, content = client.request(request_token_url, "GET")
# if resp['status'] != '200':
#     raise Exception("Invalid response %s." % resp['status'])

# request_token = dict(urllib.parse.parse_qsl(content))

# print("Request Token:")
# print("    - oauth_token        = %s" % request_token['oauth_token'])
# print("    - oauth_token_secret = %s" % request_token['oauth_token_secret'])
# print()

# # Step 2: Redirect to the provider. Since this is a CLI script we do not
# # redirect. In a web application you would redirect the user to the URL
# # below.

# print("Go to the following link in your browser:")
# print("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))
# print()

# # After the user has granted access to you, the consumer, the provider will
# # redirect you to whatever URL you have told them to redirect to. You can
# # usually define this in the oauth_callback argument as well.
# accepted = 'n'
# while accepted.lower() == 'n':
#     accepted = input('Have you authorized me? (y/n) ')
# oauth_verifier = input('What is the PIN? ')

# # Step 3: Once the consumer has redirected the user back to the oauth_callback
# # URL you can request the access token the user has approved. You use the
# # request token to sign this request. After this is done you throw away the
# # request token and use the access token returned. You should store this
# # access token somewhere safe, like a database, for future use.
# token = oauth.Token(request_token['oauth_token'],
#     request_token['oauth_token_secret'])
# token.set_verifier(oauth_verifier)
# client = oauth.Client(consumer, token)

# resp, content = client.request(access_token_url, "POST")
# access_token = dict(urllib.parse.parse_qsl(content))

# print("Access Token:")
# print("    - oauth_token        = %s" % access_token['oauth_token'])
# print("    - oauth_token_secret = %s" % access_token['oauth_token_secret'])
# print()
# print("You may now access protected resources using the access tokens above.")
# print()
