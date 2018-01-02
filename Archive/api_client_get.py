import urllib.request

server = "http://localhost:8080"

request = urllib.request.Request(server, method="GET")
with urllib.request.urlopen(request) as response:
    print(response.read().decode("utf-8")) # gets the API key
