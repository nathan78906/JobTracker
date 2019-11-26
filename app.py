import sendgrid
import os
import json
import requests
import pymysql
import logging
import sentry_sdk
from Job import jobs_response, create_job
from datetime import datetime
from sendgrid.helpers.mail import *
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=range(500, 600), session=None):
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


sentry_sdk.init(dsn=os.environ['SENTRY'])
logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=logFormatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)

filter_words = set(json.loads(os.environ['FILTER_WORDS']))
blacklist = set(json.loads(os.environ['BLACKLIST']))

mydb = pymysql.connect(host=os.environ['MARIADB_HOSTNAME'],
    user=os.environ['MARIADB_USERNAME'],
    passwd=os.environ['MARIADB_PASSWORD'],
    db=os.environ['MARIADB_DATABASE'])
cursor = mydb.cursor()

links_list = []
completed_list = []
cursor.execute("select * from greenhouse_links")
links_list += [{'name': item[1], 'url': item[2], 'type': 'greenhouse'} for item in cursor]
cursor.execute("select * from lever_links")
links_list += [{'name': item[1], 'url': item[2], 'type': 'lever'} for item in cursor]
cursor.execute("select * from jobscore_links")
links_list += [{'name': item[1], 'url': item[2], 'type': 'jobscore'} for item in cursor]
cursor.execute("select * from ultipro_links")
links_list += [{'name': item[1], 'url': item[2], 'type': 'ultipro'} for item in cursor]
cursor.execute("select * from adp_links")
links_list += [{'name': item[1], 'url': item[2], 'type': 'adp'} for item in cursor]
cursor.execute("select * from greenhouse")
completed_list += [item[0] for item in cursor]
cursor.execute("select * from lever")
completed_list += [item[0] for item in cursor]
cursor.execute("select * from jobscore")
completed_list += [item[0] for item in cursor]
cursor.execute("select * from ultipro")
completed_list += [item[0] for item in cursor]
cursor.execute("select * from adp")
completed_list += [item[0] for item in cursor]

email_list = []

for link in links_list:
    try:
        response = requests_retry_session().get(link["url"], timeout=2)
    except Exception as x:
        logger.error("{} : {}".format(x.__class__.__name__, link["url"]))
        continue

    if response.status_code != 200:
        logger.error("Status: {}, Headers: {}, Error Response: {}, Url: {}".format(response.status_code, response.headers, response.text, link["url"]))
        continue

    for job in jobs_response(response, link):
        job = create_job(job, link)
        if job.id not in completed_list and any(x in job.title.lower() for x in filter_words) and not any(x in job.title.lower() for x in blacklist):
            email_list.append("{} - {} ({}): {}".format(link["name"], job.title, job.location, job.url))
            try:
                cursor.execute("INSERT INTO {}(`id`) VALUES('{}')".format(link["type"], job.id))
                mydb.commit()
            except Exception as x:
                logger.error("{} : {}, id=".format(x.__class__.__name__, link["url"], job.id))
                continue

cursor.close()
now = datetime.now()

if email_list:
    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    from_email = Email(os.environ['FROM_EMAIL'], os.environ['FROM_NAME'])
    to_email = Email(os.environ['TO_EMAIL'])
    subject = "Jobs - {}".format(now.strftime("%x"))
    content = Content("text/plain", "\n\n".join(email_list))
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logger.info(response.status_code)
    logger.info(response.body)
    logger.info(response.headers)
else:
    logger.info("No new jobs for: {}".format(now.strftime("%m/%d/%Y, %H:%M:%S")))
