from box import Box
from jobsbundle.git.CurrentBranchResolver import CurrentBranchResolver
from jobsbundle.job.fillTemplate import fillTemplate

class ValuesFiller:

    def __init__(
        self,
        currentBranchResolver: CurrentBranchResolver,
    ):
        self.__currentBranchResolver = currentBranchResolver

    def fill(self, template: dict, values: dict, identifier: str) -> Box:
        values['identifier'] = identifier
        values['currentBranch'] = self.__currentBranchResolver.resolve()

        def fillDictTemplate(value):
            if isinstance(value, dict):
                return {k: fillDictTemplate(v) for k, v in value.items()}

            if isinstance(value, list):
                return list(map(fillDictTemplate, value))

            if isinstance(value, str):
                return fillTemplate(value, values)

            return value

        return Box({k: fillDictTemplate(v) for k, v in template.items()})
