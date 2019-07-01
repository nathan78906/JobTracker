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
            title=job.get("title".lower().rstrip(), ""),
            id=str(job["id"]),
            location=job.get("location", {}).get("name".rstrip(), ""),
            url=job.get("absolute_url".lower().rstrip(), ""))
    elif link["type"] == "lever":
        return Job(
            title=job.get("text".lower().rstrip(), ""),
            id=str(job["id"]),
            location=job.get("categories", {}).get("location".rstrip(), ""),
            url=job.get("hostedUrl".lower().rstrip(), ""))
    elif link["type"] == "jobscore":
        return Job(
            title=job.get("title".lower().rstrip(), ""),
            id=str(job["id"]),
            location=job.get("location".rstrip(), ""),
            url=job.get("detail_url".lower().rstrip(), ""))
