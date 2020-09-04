from argparse import ArgumentParser, Namespace
from logging import Logger
from box import Box
import time
from consolebundle.ConsoleCommand import ConsoleCommand
from jobsbundle.job.ValuesFiller import ValuesFiller
from databricks_api.databricks import DatabricksAPI
from jobsbundle.job.JobIdFinder import JobIdFinder
from jobsbundle.job.JobPermissionUpdater import JobPermissionUpdater


class StreamingJobCreateOrUpdateCommand(ConsoleCommand):

    def __init__(
        self,
        jobsRawConfig: Box,
        logger: Logger,
        dbxApi: DatabricksAPI,
        valuesFiller: ValuesFiller,
        jobIdFinder: JobIdFinder,
        permissionUpdater: JobPermissionUpdater
    ):
        self.__jobsRawConfig = jobsRawConfig
        self.__logger = logger
        self.__dbxApi = dbxApi
        self.__valuesFiller = valuesFiller
        self.__jobIdFinder = jobIdFinder
        self.__permissionUpdater = permissionUpdater

    def getCommand(self) -> str:
        return 'databricks:job:streaming-create-or-update'

    def getDescription(self):
        return 'Creates new or updates existing Databricks streaming job based on given job identifier and cancels the active run if exists'

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

        jobId = self.__jobIdFinder.find(jobConfig.name)

        if jobId:
            self.__logger.info(f'Existing job found with ID: {jobId}, updating')
            self.__dbxApi.jobs.reset_job(jobId, jobConfig.to_dict())
            self.__logger.info(f'Job successfully updated')
            self.__cancelActiveRun(jobId)
        else:
            self.__logger.info(f'No existing job with name "{jobConfig.name}" found, creating new one')
            jobId = self.__dbxApi.jobs.create_job(**jobConfig.to_dict())['job_id']
            self.__logger.info(f'Job with ID {jobId} successfully created')

        self.__dbxApi.jobs.run_now(jobId)
        self.__logger.info(f'Job with ID {jobId} successfully run')

        if 'permission' in jobRawConfig:
            self.__permissionUpdater.run(jobRawConfig['permission'], jobId)

    def __cancelActiveRun(self, jobId: str):
        self.__logger.info('Looking for active runs...')
        runsActive = self.__dbxApi.jobs.list_runs(job_id=jobId, active_only=True)
        while 'runs' in runsActive:
            for run in runsActive['runs']:
                run_id = run['run_id']
                self.__dbxApi.jobs.cancel_run(run_id=run_id)
                self.__logger.info(f'Run {run_id} canceled')

                time.sleep(5)
                runsActive = self.__dbxApi.jobs.list_runs(job_id=jobId, active_only=True)
        else:
            self.__logger.info('No active run exists')
