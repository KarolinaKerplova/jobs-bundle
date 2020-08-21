from argparse import ArgumentParser, Namespace
from logging import Logger
from box import Box
from consolebundle.ConsoleCommand import ConsoleCommand
from databricks_api.databricks import DatabricksAPI
from jobsbundle.job.ValuesFiller import ValuesFiller

class JobCreatorCommand(ConsoleCommand):

    def __init__(
        self,
        jobsRawConfig: Box,
        logger: Logger,
        dbxApi: DatabricksAPI,
        valuesFiller: ValuesFiller,
    ):
        self.__jobsRawConfig = jobsRawConfig
        self.__logger = logger
        self.__dbxApi = dbxApi
        self.__valuesFiller = valuesFiller

    def getCommand(self) -> str:
        return 'databricks:job:create'

    def getDescription(self):
        return 'Create a new Databricks job based on given job identifier'

    def configure(self, argumentParser: ArgumentParser):
        argumentParser.add_argument(dest='identifier', help='Job identifier')

    def run(self, inputArgs: Namespace):
        if inputArgs.identifier not in self.__jobsRawConfig:
            self.__logger.error('No job found for {}. Maybe you forgot to add the configuration under jobsbundle.jobs?'.format(inputArgs.identifier))
            return

        jobRawConfig = self.__jobsRawConfig[inputArgs.identifier].to_json()
        jobConfig = self.__valuesFiller.fill(
            jobRawConfig['template'],
            jobRawConfig['values'],
            inputArgs.identifier
        )

        self.__logger.info(f'Creating job {inputArgs.identifier} with name "{jobConfig.name}"')

        self.__dbxApi.jobs.create_job(**jobConfig)

        self.__logger.info(f'Job successfully created')
