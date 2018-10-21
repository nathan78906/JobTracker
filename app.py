import sendgrid
import os
import json
import requests
from datetime import datetime
from sendgrid.helpers.mail import *
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

filter_words = set(["co-op", "coop", "internship", "intern", "student"])
blacklist = set(["internal", "international"])

with open('greenhouse.json') as json_data:
    greenhouse = json.load(json_data)
    
with open('lever.json') as json_data:
    lever = json.load(json_data)

email_list = []

for g in greenhouse:
	try:
		response = requests_retry_session().get(g["url"], timeout=2)
	except Exception as x:
		print("{} : {}".format(x.__class__.__name__, g["url"]))
		email_list.append("{} : {}".format(x.__class__.__name__, g["url"]))
		continue

	if response.status_code != 200:
		print("Status: {}, Headers: {}, Error Response: {}".format(response.status_code, response.headers, response.text))
		email_list.append("{} : {}".format(response.status_code, g["url"]))
		continue

	print(g["url"])
	for job in response.json()["jobs"]:
		if any([x in job["title"].lower() for x in filter_words]) and not any([x in job["title"].lower() for x in blacklist]):
			email_list.append("{} - {} : {}".format(g["name"], job["title"], job["absolute_url"]))


for l in lever:
	try:
		response = requests_retry_session().get(l["url"], timeout=2)
	except Exception as x:
		print("{} : {}".format(x.__class__.__name__, l["url"]))
		email_list.append("{} : {}".format(x.__class__.__name__, l["url"]))
		continue

	if response.status_code != 200:
		print("Status: {}, Headers: {}, Error Response: {}".format(response.status_code, response.headers, response.text))
		email_list.append("{} : {}".format(response.status_code, l["url"]))
		continue
		
	print(l["url"])
	for job in response.json():
		if any([x in job["text"].lower() for x in filter_words]) and not any([x in job["text"].lower() for x in blacklist]):
			email_list.append("{} - {} : {}".format(l["name"], job["text"], job["hostedUrl"]))

now = datetime.now()

sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
from_email = Email("intern@jobs.com", "InternTracker")
to_email = Email(os.environ['TO_EMAIL'])
subject = "Internships & Co-ops - {}".format(now.strftime("%x"))
content = Content("text/plain", "\n\n".join(email_list))
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers)
