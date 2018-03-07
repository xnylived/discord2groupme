
#!/usr/bin/env python
"""
Very simple HTTP server in python.

Usage::
	./dummy-web-server.py [<port>]

Send a GET request::
	curl http://localhost

Send a HEAD request::
	curl -I http://localhost

Send a POST request::
	curl -d "foo=bar&bin=baz" http://localhost

"""
import sys
import json
import requests

if sys.version_info[0] < 3:
	# python 2 import
	from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
	# python 3 import
	from http.server import BaseHTTPRequestHandler, HTTPServer


fh = open("config.json")
config = json.loads(fh.read());
fh.close()
webhook_url = config['discord_webhook_url']


if config['groupme_user_id'] != "":
	groupme_id = int(config['groupme_user_id'])
	valid_id = True
else:
	print("No user ID set. Send a message and check this output for the user ID, then set it in config.json and restart.")
	valid_id = False

class BaseServer(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		self._set_headers()
		self.wfile.write("<html><body><p>Go away!!</p></body></html>"
							.encode('utf-8'))

	def do_HEAD(self):
		self._set_headers()
		
	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		print(post_data)
		j = json.loads(post_data.decode('utf8'))
		if valid_id:
			if int(j['user_id']) == groupme_id:
				r = requests.post(webhook_url, json={"content":j['text']})
				print(r.status_code, r.reason)
			self._set_headers()
			self.wfile.write("<html><body><p>POST!</p><p>%s</p></body></html>"
								.encode('utf-8') % post_data)
		else:
			print(j['name'] + " (ID " + j['user_id'] + ") sent: " + j['text'])
		
def run(server_class=HTTPServer, handler_class=BaseServer, port=80):
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)
	print('HTTP server running on port %s'% port)
	httpd.serve_forever()

if __name__ == "__main__":
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()
