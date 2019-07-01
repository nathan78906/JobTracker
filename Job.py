class Job:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def jobs_response(response, link):
    if link["type"] == "greenhouse" or link["type"] == "jobscore":
        return response.json()["jobs"]
    elif link["type"] == "lever":
        return response.json()

def create_job(job, link):
    if link["type"] == "greenhouse":
        return Job(
            title=job["title"].lower().rstrip(),
            id=str(job["id"]),
            location=job["location"]["name"].rstrip(),
            url=job["absolute_url"])
    elif link["type"] == "lever":
        return Job(
            title=job["text"].lower().rstrip(),
            id=str(job["id"]),
            location=job["categories"]["location"].rstrip(),
            url=job["hostedUrl"])
    elif link["type"] == "jobscore":
        return Job(
            title=job["title"].lower().rstrip(),
            id=str(job["id"]),
            location=job["location"].rstrip(),
            url=job["detail_url"])
