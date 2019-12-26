from jinja2.loaders import BaseLoader
import os
from os import path
from jinja2.exceptions import TemplateNotFound
from jinja2.utils import open_if_exists
import yaml


def split_template_path(template):
    """Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if path.sep in piece \
                or (path.altsep and path.altsep in piece) or \
                piece == path.pardir:
            raise TemplateNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces


class GenieLoader(BaseLoader):
    """Loads templates from the file system.  This loader can find templates
        in folders on the file system and is the preferred way to load them.

        The loader takes the path to the templates as string, or if multiple
        locations are wanted a list of them which is then looked up in the
        given order::

        >>> loader = GenieLoader('/path/to/templates', queries_dialect)
        >>> loader = GenieLoader(['/path/to/templates', '/other/path'], queries_dialect)

        Per default the template encoding is ``'utf-8'`` which can be changed
        by setting the `encoding` parameter to something else.

        To follow symbolic links, set the *followlinks* parameter to ``True``::

        >>> loader = GenieLoader('/path/to/templates', queries_dialect, followlinks=True)

        .. versionchanged:: 2.8+
           The *followlinks* parameter was added.
        """

    def __init__(self, searchpath, queries_dialect, encoding='utf-8', followlinks=False):
        if isinstance(searchpath, str):
            searchpath = [searchpath]
        self.searchpath = list(searchpath)
        self.queries_dialect = queries_dialect
        self.encoding = encoding
        self.followlinks = followlinks

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = path.getmtime(filename)
            self.queries_dialect[path.basename(filename)] = yaml.full_load(contents)['dialect']

            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False

            return contents, filename, uptodate
        raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            walk_dir = os.walk(searchpath, followlinks=self.followlinks)
            for dirpath, dirnames, filenames in walk_dir:
                for filename in filenames:
                    template = os.path.join(dirpath, filename) \
                        [len(searchpath):].strip(os.path.sep) \
                        .replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)
