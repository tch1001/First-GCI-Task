from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import string
import random

# response_dict = {
#  "business": "Pizza Hut",
#  "founded": 2010, # Bogus date
#  "locations": [
#  "Pasir Ris",
#  "Tampines",
#  "Bishan",
#  "Toa Payoh",
#  "Orchard" # ...and everywhere else
#  ]
# }

class DemoHandler(BaseHTTPRequestHandler):
	def do_GET(self):
 		# Add a "200 OK" response code to the headers buffer
 		self.send_response(200)
 		self.send_header('Content-type', 'text/html')
 		self.end_headers()
 		# The output to send back in the response
 		response = db_keygen()
 		# Write the response into the output stream
 		message_bytes = bytes(response, "utf8")
 		self.wfile.write(message_bytes)
 		return
 		

 		
def run(server_class=HTTPServer, handler_class=DemoHandler):
	print('starting server...')
	# Server settings
	# Run server in localhost on port 8080
	server_address = ("localhost", 8080)
	httpd = server_class(server_address, handler_class)

	print('running server...')
	httpd.serve_forever()
	
def keygen(length=32):
	charspace = string.ascii_letters + string.digits
	key = ''
	for _ in range(length):
		key+=random.choice(charspace)
	return key
	
# print(keygen(32))

def db_init():
	db = sqlite3.connect('auth.db')
	db.execute("""CREATE TABLE IF NOT EXISTS keys (key text, status integer, quota integer, used integer)""")
	db.commit()
	db.close()
	
def db_keygen():
	db = sqlite3.connect('auth.db')
	newkey = keygen()
	t = (newkey, )
	
	db.execute("INSERT INTO keys VALUES (?, 1, 10, 0)", t)
	
	
# 	db.execute("DELETE FROM keys")
	db.commit()
	for row in db.execute("SELECT * FROM keys"):
		print(row)
	db.close()
	return newkey

db_init()
run()