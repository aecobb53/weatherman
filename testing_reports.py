import requests

url = 'http://localhost:8010/'

print(url)

response = requests.get(url)
print(response)
print(response.text)

