"""
The MIT License

Copyright (c) 2007 Leah Culver

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request, urllib.parse, urllib.error


class Base(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.oauth_server = oauth.OAuthServer(MockOAuthDataStore())
        self.oauth_server.add_signature_method(oauth.OAuthSignatureMethod_PLAINTEXT())
        self.oauth_server.add_signature_method(oauth.OAuthSignatureMethod_HMAC_SHA1())
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    # example way to send an oauth error
    def send_oauth_error(self, err=None):
        # send a 401 error
        self.send_error(401, str(err.message))
        # return the authenticate header
        header = oauth.build_authenticate_header(realm=REALM)
        for k, v in header.items():
            self.send_header(k, v)

    def do_GET(self):

        # debug info
        # print self.command, self.path, self.headers

        # get the post data (if any)
        postdata = None
        if self.command == "POST":
            try:
                length = int(self.headers.getheader("content-length"))
                postdata = self.rfile.read(length)
            except:
                pass

        # construct the oauth request from the request parameters
        oauth_request = oauth.OAuthRequest.from_request(
            self.command, self.path, headers=self.headers, query_string=postdata
        )

        # request token
        if self.path.startswith(REQUEST_TOKEN_URL):
            try:
                # create a request token
                token = self.oauth_server.fetch_request_token(oauth_request)
                # send okay response
                self.send_response(200, "OK")
                self.end_headers()
                # return the token
                self.wfile.write(token.to_string())
            except oauth.OAuthError as err:
                self.send_oauth_error(err)
            return

        # user authorization
        if self.path.startswith(AUTHORIZATION_URL):
            try:
                # get the request token
                token = self.oauth_server.fetch_request_token(oauth_request)
                # authorize the token (kind of does nothing for now)
                token = self.oauth_server.authorize_token(token, None)
                token.set_verifier(VERIFIER)
                # send okay response
                self.send_response(200, "OK")
                self.end_headers()
                # return the callback url (to show server has it)
                self.wfile.write(token.get_callback_url())
            except oauth.OAuthError as err:
                self.send_oauth_error(err)
            return

        # access token
        if self.path.startswith(ACCESS_TOKEN_URL):
            try:
                # create an access token
                token = self.oauth_server.fetch_access_token(oauth_request)
                # send okay response
                self.send_response(200, "OK")
                self.end_headers()
                # return the token
                self.wfile.write(token.to_string())
            except oauth.OAuthError as err:
                self.send_oauth_error(err)
            return

        # protected resources
        if self.path.startswith(RESOURCE_URL):
            try:
                # verify the request has been oauth authorized
                consumer, token, params = self.oauth_server.verify_request(
                    oauth_request
                )
                # send okay response
                self.send_response(200, "OK")
                self.end_headers()
                # return the extra parameters - just for something to return
                self.wfile.write(str(params))
            except oauth.OAuthError as err:
                self.send_oauth_error(err)
            return

    def do_POST(self):
        return self.do_GET()

    def main(wait):
        try:
            server = HTTPServer(("", 8080), RequestHandler)
            print("Test server running...")
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()
