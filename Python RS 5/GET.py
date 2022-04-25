import requests

auth = requests.auth.HTTPDigestAuth("Default User", "robotics")

response = requests.get("http://152.94.0.38/rw/panel/ctrlstate", auth = auth)

print(response.text)

