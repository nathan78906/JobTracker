import sendgrid
import os
import json
import requests
from datetime import datetime
from sendgrid.helpers.mail import *

filter_words = set(["co-op", "coop", "internship", "intern", "student"])
blacklist = set(["internal", "international"])

with open('greenhouse.json') as json_data:
    greenhouse = json.load(json_data)
    
with open('lever.json') as json_data:
    lever = json.load(json_data)

email_list = []

for g in greenhouse:
	try:
		response = requests.get(g["url"], timeout=2)
	except requests.exceptions.Timeout:
		print("Timeout on: " + g["url"])
		email_list.append("Timeout on: " + g["url"])
		continue
	except requests.exceptions.ConnectionError:
		print("Connection Error on: " + g["url"])
		email_list.append("Connection Error on: " + g["url"])
		continue

	if response.status_code != 200:
		print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.text)
		continue
	print(g["url"])
	for job in response.json()["jobs"]:
		if any([x in job["title"].lower() for x in filter_words]) and not any([x in job["title"].lower() for x in blacklist]):
			email_list.append(g["name"] + " - " + job["title"] + ": " + job["absolute_url"])


for l in lever:
	try:
		response = requests.get(l["url"], timeout=2)
	except requests.exceptions.Timeout:
		print("Timeout on: " + l["url"])
		email_list.append("Timeout on: " + l["url"])
		continue
	except requests.exceptions.ConnectionError:
		print("Connection Error on: " + l["url"])
		email_list.append("Connection Error on: " + l["url"])
		continue

	if response.status_code != 200:
		print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.text)
		continues
	print(l["url"])
	for job in response.json():
		if any([x in job["text"].lower() for x in filter_words]) and not any([x in job["text"].lower() for x in blacklist]):
			email_list.append(l["name"] + " - " + job["text"] + ": " + job["hostedUrl"])


now = datetime.now()


sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
from_email = Email("intern@jobs.com", "InternTracker")
to_email = Email(os.environ['TO_EMAIL'])
subject = "Internships & Co-ops" + " - " + now.strftime("%x")
content = Content("text/plain", "\n\n".join(email_list))
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers)