import os
from dataclasses import dataclass, field


@dataclass
class Subject:
    name = str
    class_id = str


@dataclass
class Book:
    name = str
    download_url = str
    filename = str
    subject = Subject
    is_external = bool
    seems_downloadable = field(default=True)

    qs_file_arg = field(init=False, default='arquivo')

    @property
    def path(self):
        media_name = self.filename
        media_dir = self.subject.name
        return os.path.join(media_dir, media_name)