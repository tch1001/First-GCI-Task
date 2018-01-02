from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import string
import random
import urllib
import hashlib

ADMIN_PASSWORD = 'meow' # hardcoded admin password

def hashPassword(pwd): # function that hashes passwords
    return hashlib.md5(pwd.encode()).hexdigest() 
    
def keygen(length=32): # generates a random key
	charspace = string.ascii_letters + string.digits # all the characters 
	key = ''
	for _ in range(length): # generate <length> random characters
		key+=random.choice(charspace) 
	return key # return the key
	
def new_key(): # creates a new key and inserts it into the table
	db = sqlite3.connect('auth.db') # db
	newkey = keygen() # newkey generation
	t = (newkey, ) # sql injection prevention
	
	db.execute("INSERT INTO keys VALUES (?, 1, 10, 0)", t) # insertion
	
	db.commit() # save changes
	
	db.close() # close
	return newkey # return the new key

def printDB(): # debugging function to print all database stuff
	db = sqlite3.connect('auth.db') # db
	print("keys: ", [i for i in db.execute("SELECT * FROM keys")]) # print keys 
	print("data: ", [i for i in db.execute("SELECT * FROM data")]) # print data
	print("users: ", [i for i in db.execute("SELECT * FROM users")]) # print users
	db.close() # close

def getData(): # get the API data from table
	db = sqlite3.connect('auth.db') # db
	return [row for row in db.execute("SELECT * FROM data")] # list comprehension gets all data from table "data"
	
def new_user(username, password, admin=False): # creates a new user and adds to db
	db = sqlite3.connect('auth.db') # db
	
	if admin: # if it is an admin
		db.execute('INSERT INTO users VALUES (?, ?, 1)', (username, password)) # 1 for admin field
	else:
		db.execute('INSERT INTO users VALUES (?, ?, 0)', (username, password)) # else 0 for admin field
	db.commit() # save
	db.close() # close
	
	
def auth_key(key=''): # returns True if it is a valid key
	t = (key,) # sqli prevention
	db = sqlite3.connect('auth.db') # db 
	for row in db.execute("SELECT * FROM keys WHERE key == ?", t): # get all keys
		return True # if there is a key, this will run once and thus return True
	return False # if there is no key, return False
	
def usernameExists(username): # determine if a username already exists
	db = sqlite3.connect('auth.db') # db
	username = (username, ) # sqli prevention
	for _ in db.execute("SELECT * FROM users WHERE username = ?", username): # similar idea to above
		return True # if there exists such a username, this would run, and return True
	return False # if no such user, then it would return False
	
class API_handler(BaseHTTPRequestHandler): # server!
	def do_GET(self): # handles GET requests
 		self.send_response(200) # code 200
 		self.send_header('Content-type', 'application/json') # json data response
 		self.end_headers() 
 		
 		response_dict = {'key':new_key()} # response data is the key 
 		message_bytes = bytes(json.dumps(response_dict), 'utf8') # convert to bytes
 		self.wfile.write(message_bytes) # write
#  		printDB() # for debugging
 		return # return!
 		
	def do_POST(self): # handles POST requests
		data = self.rfile.read(int(self.headers.get("Content-length"))).decode("utf-8") # gets the data
		data = urllib.parse.parse_qs(data) # reformats some data
		
		username = self.headers.get("Username") # gets the username
		password = self.headers.get("Password") # gets the password (plaintext)
		
		password = hashPassword(password) # hashes password for security
		
		db = sqlite3.connect('auth.db') # db
		
		if data['signUp'][0].lower() == 'true': # if 'signUp' field is true, run code for signing up
			if usernameExists(username): # if username taken/exists
				self.send_response(403, "Username taken") # error!
				self.end_headers() 
# 				print("repeated username") # for debugging 
				return # return
			if data['admin_password'][0] == ADMIN_PASSWORD: # if admin password is right
				new_user(username, password, True) # create new admin
				self.send_response(200) # code 200
				self.send_header('Content-type', 'application/json') # json response
				self.end_headers()
				response_dict = {'status':'success', 'level':'admin', 'message':'Welcome, (admin) '+username} # return status, level, & message
				message_bytes = bytes(json.dumps(response_dict), 'utf8') # convert to bytes
				self.wfile.write(message_bytes) # write back
				print("New admin!")
			else:
				new_user(username, password, False) # admin password fails, just a normal user
				self.send_response(200) # code 200
				self.send_header('Content-type', 'application/json') # json response
				self.end_headers()
				# return status, level, and message
				response_dict = {'status': 'success', 'level':'user', 'message': 'Welcome, ' + username}
				message_bytes = bytes(json.dumps(response_dict), 'utf8') # bytes format
				self.wfile.write(message_bytes) # write 
				print("New user!") 
		elif data['upload'][0].lower() == 'true': # if 'upload' field is true (& 'signUp' field is False)
			noUsername = True
			wrongPassword = True
			
			for _ in db.execute('SELECT * FROM users WHERE username == ?', (username,)):
				noUsername = False
			if noUsername:
				self.send_response(403, 'No such username')
				self.end_headers()
				return
			for _ in db.execute('SELECT * FROM users WHERE username == ? AND password == ?', (username, password)):
				wrongPassword = False
			if  wrongPassword:
				self.send_response(403, 'Wrong password')
				self.end_headers()
				return
			for _ in db.execute('SELECT * FROM users WHERE admin==1 AND username==? AND password == ?', (username, password)):
				# this code only runs if the user is an admin
# 				print('its an admin')
				json_data = json.loads(data['upload_data'][0].replace("'", "\"")) # get the json data
# 				print(json_data) # for debugging
				for i,j in json_data.items(): # loops through individual key,value pairs
					db.execute('INSERT INTO data VALUES (?, ?)', (i,j)) # inserts them one by one into db
				db.commit() # save
# 				printDB() 
				self.send_response(200) # code 200
				self.send_header('Content-type', 'application/json') # json response
				self.end_headers()
				response_dict = {'status':'success', 'data_uploaded':json_data} # status and returns the data uploaded
				message_bytes = bytes(json.dumps(response_dict), 'utf8') # bytes
				self.wfile.write(message_bytes) # write
				return # return
# 			print('nope not admin') # if not admin
			self.send_response(403, 'You need to be an admin to upload') # error message
			self.end_headers()
			return # return
		else: # neither "signUp" nor "upload" fields are true, it's to get data!
			key = data['key'][0] # gets the key
			if auth_key(key) == True: # if the key is authorised/exists
 				self.send_response(200) # code 200
 				self.send_header('Content-type', 'application/json') # json response
 				self.end_headers() 
 				response_dict = {'key':key, 'data':getData()} # gets the API data (list format)
 				message_bytes = bytes(json.dumps(response_dict), 'utf8') # bytes
 				self.wfile.write(message_bytes) # write
#  				print('valid api key') 
			else: 
				self.send_response(403, "API key is invalid") # API key is invalid
				self.end_headers()
# 				print('invalid api key') 

			
		db.close() # close

# 		printDB()
		return  # return
 		
def run(server_class=HTTPServer, handler_class=API_handler):
	print('Starting server...')
	# Server settings
	# Run server in localhost on port 8080
	server_address = ("localhost", 8080)
	httpd = server_class(server_address, handler_class)

	print('Running server...')
	httpd.serve_forever() # serve forever, always listening
	


def db_init():
	db = sqlite3.connect('auth.db') # db
# 	db.execute("DROP TABLE users") # these 3 are for convenient resetting
# 	db.execute("DROP TABLE keys")
# 	db.execute('DROP TABLE data')

	# these 3 lines are to create the tables (if not existing already)
	db.execute("CREATE TABLE IF NOT EXISTS keys (key text, status integer, quota integer, used integer)")
	db.execute("CREATE TABLE IF NOT EXISTS users (username text, password text, admin integer)")
	db.execute("CREATE TABLE IF NOT EXISTS data (key text, value text)")
	
# 	printDB() 
	
	db.commit() # save
	db.close() # close
	

db_init() # init DB
run() # run everything