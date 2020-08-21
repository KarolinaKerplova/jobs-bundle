from argparse import ArgumentParser, Namespace
from logging import Logger
from box import Box
from consolebundle.ConsoleCommand import ConsoleCommand
from jobsbundle.job.ValuesFiller import ValuesFiller
from databricks_api.databricks import DatabricksAPI

class JobCreateOrUpdateCommand(ConsoleCommand):

    def __init__(
        self,
        jobsRawConfig: Box,
        logger: Logger,
        dbxApi: DatabricksAPI,
        valuesFiller: ValuesFiller
    ):
        self.__jobsRawConfig = jobsRawConfig
        self.__logger = logger
        self.__dbxApi = dbxApi
        self.__valuesFiller = valuesFiller

    def getCommand(self) -> str:
        return 'databricks:job:create-or-update'

    def getDescription(self):
        return 'Create new or update existing Databricks job based on given job identifier'

    def configure(self, argumentParser: ArgumentParser):
        argumentParser.add_argument(dest='identifier', help='Job identifier')

    def run(self, inputArgs: Namespace):
        if inputArgs.identifier not in self.__jobsRawConfig:
            self.__logger.error('No job found for {}. Maybe you forgot to add the configuration under jobsbundle.jobs?'.format(inputArgs.identifier))
            return

        jobRawConfig = self.__jobsRawConfig[inputArgs.identifier].to_dict()
        jobConfig = self.__valuesFiller.fill(
            jobRawConfig['template'],
            jobRawConfig['values'],
            inputArgs.identifier
        )

        self.__logger.info(f'Looking for job with name "{jobConfig.name}"')

        jobId = self.__findJobId(jobConfig.name)

        if jobId:
            self.__logger.info(f'Existing job found with ID: {jobId}, updating')
            self.__dbxApi.jobs.reset_job(jobId, jobConfig.to_dict())
            self.__logger.info(f'Job successfully updated')
        else:
            self.__logger.info(f'No existing job with name "{jobConfig.name}" found, creating new one')
            self.__dbxApi.jobs.create_job(**jobConfig.to_dict())
            self.__logger.info(f'Job successfully created')

    def __findJobId(self, jobName: str):
        while True:
            jobsResponse = self.__dbxApi.jobs.list_jobs()

            if 'jobs' not in jobsResponse:
                if 'jobs' in locals():
                    self.__logger.info('No more jobs exist')
                    return None

                self.__logger.info('No jobs exist')
                return None

            jobs = jobsResponse['jobs']

            for job in jobs:
                if job['settings']['name'] == jobName:
                    return job['job_id']

            return None
