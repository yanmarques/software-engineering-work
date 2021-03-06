from ....crawler import item

import os
import dataclasses
from urllib.parse import unquote


def parse_subject_name(class_name):
    '''
    Extract subject name from class name.

    Eg.:
    >>> parse_subject_name('AOL - UA - Grafos')
    Grafos
    >>> parse_subject_name('Grafos')
    Grafos
    '''

    fragments = class_name.split('-')

    # only understands 3 fragment, otherwise skip
    if len(fragments) != 3:
        return class_name

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
    subject: Subject
    
    download_url: str = item.field(
        item.text_processor(unquote)
    )

    filename: item.Text = dataclasses.field(default=None)
    is_external: bool = dataclasses.field(default=False)
    seems_downloadable: bool = dataclasses.field(default=False)

    qs_file_arg = 'arquivo'

    @property
    def path(self):
        media_name = self.filename
        media_dir = self.subject.name
        return os.path.join(media_dir, media_name)