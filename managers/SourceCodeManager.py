import bs4
import json


class SourceCodeManager:

    def parse_code(self, source_code):
        parsed_code = bs4.BeautifulSoup(source_code, 'lxml')
        return parsed_code

    def to_json(self, string):
        return json.loads(string)

    def get_text(self, html_tag):
        if html_tag is None:
            return None
        else:
            return html_tag.text.strip()

