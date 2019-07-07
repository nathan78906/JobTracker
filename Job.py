class Job:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def jobs_response(response, link):
    if link["type"] == "greenhouse" or link["type"] == "jobscore":
        return response.json()["jobs"]
    elif link["type"] == "ultipro":
        return response.json()["opportunities"]
    elif link["type"] == "lever":
        return response.json()

def create_job(job, link):
    if link["type"] == "greenhouse":
        return Job(
            title=job.get("title", "").rstrip(),
            id=str(job["id"]),
            location=job.get("location", {}).get("name", "").rstrip(),
            url=job.get("absolute_url", "").rstrip())
    elif link["type"] == "lever":
        return Job(
            title=job.get("text", "").rstrip(),
            id=str(job["id"]),
            location=job.get("categories", {}).get("location", "").rstrip(),
            url=job.get("hostedUrl", "").rstrip())
    elif link["type"] == "jobscore":
        return Job(
            title=job.get("title", "").rstrip(),
            id=str(job["id"]),
            location=job.get("location", "").rstrip(),
            url=job.get("detail_url", "").rstrip())
    elif link["type"] == "ultipro":
        return Job(
            title=job.get("Title", "").rstrip(),
            id=str(job["Id"]),
            location=job.get("Locations", [{}])[0].get("Address", {}).get("City", "").rstrip(),
            url=link["url"].rstrip("JobBoardView/LoadSearchResults") + "/OpportunityDetail?opportunityId=" + str(job["Id"]))
