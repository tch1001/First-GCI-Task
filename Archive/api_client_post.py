import urllib.request
import json

server = "http://localhost:8080"


data = { "key" : "HgDjPGeYzgkwmdVHiWXgeNDzDogt8mGK", # key field
            "signUp": 'false', # signUp field
            "upload": 'false', # upload field
            "upload_data": {'cats':'meow', 'cows':'moo', 'dogs':'ruff'}, # (for uploading) animal sounds as data :D
        	'admin_password': 'meow'} # admin password field, only for signing up
        	
        # to sign up, turn key "signUp" to 'true' (checked first in server code)
        	# the username and password are in the headers
        	# if the field "admin_password" matches the admin password on the server,
        	# 	you will become admin (can upload)
        	# otherwise you are just a user (cannot upload)
        
        # to upload data, turn key "upload" to 'true' (checked second in server code)
        	# the data to upload is in the field "upload_data" (as pairs of keys and values, (dictionary))
        	
        	
        # if both "signUp" and "upload" are 'false', server will return API data
        	# list of pairs of keys and values
        
        
data_enc = urllib.parse.urlencode(data).encode("utf8")

# Set up headers
headers = { "Content-type" : "application/x-www-form-urlencoded",
            "Content-length" : len(data_enc) ,
            "Username": "meow", "Password":"meowmeow"}
            

request = urllib.request.Request(server, data_enc, headers, method="POST")


with urllib.request.urlopen(request) as response:
    print(response.read().decode("utf-8"))
