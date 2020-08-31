from logging import Logger
from databricks_api.databricks import DatabricksAPI


class JobIdFinder:

    def __init__(
        self,
        logger: Logger,
        dbxApi: DatabricksAPI,
    ):
        self.__logger = logger
        self.__dbxApi = dbxApi

    def find(self, jobName: str):
        jobsResponse = self.__dbxApi.jobs.list_jobs()

        if 'jobs' not in jobsResponse:
            self.__logger.info('No jobs exist')
            return None

        jobs = jobsResponse['jobs']
        for job in jobs:
            if job['settings']['name'] == jobName:
                return job['job_id']
        return None
