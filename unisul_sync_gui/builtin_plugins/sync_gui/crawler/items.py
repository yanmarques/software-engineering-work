from ....crawler import item

import os
import dataclasses
from urllib.parse import unquote


def parse_subject_name(name):
    fragments = name.split('-')

    # TODO does this cover all cases?
    if 'AOL' in fragments[0]:
        return fragments[-1]
    return fragments[-2]

@dataclasses.dataclass
class Subject(item.Item):
    class_id: item.Text
    name: str = item.field(
        input_processor=item.text_processor(parse_subject_name)
    )


@dataclasses.dataclass
class Book(item.Item):
    name: item.Text
    filename: item.Text
    subject: Subject
    
    download_url: str = item.field(
        item.text_processor(unquote)
    )

    is_external: bool = dataclasses.field(default=False)
    seems_downloadable: bool = dataclasses.field(default=True)

    qs_file_arg = 'arquivo'

    @property
    def path(self):
        media_name = self.filename
        media_dir = self.subject.name
        return os.path.join(media_dir, media_name)