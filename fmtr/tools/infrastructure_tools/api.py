import importlib

from fmtr.tools import api_tools as api
from fmtr.tools.constants import Constants


class Api(api.Base):
    TITLE = f'Infrastructure API'
    URL_DOCS = '/'
    PORT = 9100  # todo fix

    def get_endpoints(self):
        endpoints = [
            api.Endpoint(method_http=self.app.get, path='/{name}/recreate', method=self.recreate),
            api.Endpoint(method_http=self.app.get, path='/{name}/release', method=self.release),

        ]

        return endpoints

    def get_project(self, name: str):
        Project = importlib.import_module(f'{name}.project').Project
        return Project

    async def recreate(self, name: str):
        Project = self.get_project(name)
        project = Project()

        project.stacks.channel[Constants.DEVELOPMENT].recreate()

    async def release(self, name: str):
        Project = self.get_project(name)
        project = Project()

        project.releaser.run()


if __name__ == '__main__':
    Api.launch()
