import requests

token = "20984~RenZEFHtXkHeXMeZDWfVEfLJVDt3vePCB2e48fEL36vvxwCWErZckF22Ufzc9uMZ"

request = "https://onu.instructure.com/api/v1/users/self/courses/12946/assignments?per_page=50&access_token=" + token 

resp = requests.get(request)

assignments = resp.json() 
print(assignments)