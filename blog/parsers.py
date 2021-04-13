from rest_framework.parsers import MultiPartParser, DataAndFiles
from rest_framework.utils import json


class RecipeMultiPartParser(MultiPartParser):
    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream=stream, media_type=media_type, parser_context=parser_context)
        data = {}
        for key, value in result.data.items():
            if key in ('ingredients', 'tags', 'steps'):
                data[key] = json.loads(value)
            else:
                data[key] = value
        return DataAndFiles(data, result.files)
