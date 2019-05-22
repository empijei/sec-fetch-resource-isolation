# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class ResourceIsolation():
  """
  ResourceIsolation protects an app by preventing cross-site resource inclusion
  and CSRF for browsers that support Fetch Metadata.

  Sample usage:
    def app(environ, start_response):
      start_response('200 OK', [('Content-Type', 'text/html')])
      return [b'Hello, world!']

    if __name__ == '__main__':
      from wsgiref.simple_server import make_server
      httpd = make_server('', 8080, ResourceIsolation(app))
      print('Serving on port 8080...')
      try:
          httpd.serve_forever()
      except KeyboardInterrupt:
          print('Goodbye!')
  """

  def __init__(self, app):
     self._app = app

  def __call__(self, environ, start_response):
    # Allow requests from browsers which don't send Fetch Metadata
    if 'HTTP_SEC_FETCH_SITE' not in environ or 'HTTP_SEC_FETCH_MODE' not in environ:
      return self._app(environ, start_response)

    # Allow requests from same-site and browser-initiated requests.
    if environ['HTTP_SEC_FETCH_SITE'] in ['none', 'same-site', 'same-origin']:
      return self._app(environ, start_response)

    # Allow simple top-level navigations from anywhere
    if environ['HTTP_SEC_FETCH_MODE'] == 'navigate' and environ['REQUEST_METHOD'] == 'GET':
      return self._app(environ, start_response)

    # Block everything else.
    start_response('403 Forbidden', [])
    return [b'Invalid resource access']
