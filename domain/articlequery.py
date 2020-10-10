from typing import Generator

from mwclient import Site


class ArticleQuery(object):

    def __init__(self, cliente: Site):
        self.client = cliente
        self.start = None
        self.end = None
        self.prefix = None
        self.namespaces = None
        self.filterredir = 'all'
        self.minsize = None
        self.maxsize = None
        self.prmode = False
        self.prtype = "edit"
        self.prlevel = None
        self.limit = None
        self.dir = 'ascending'
        self.filterlanglinks = 'all'

    def invoke(self) -> Generator[str, None, None]:
        if self.namespaces:
            for namespace in self.namespaces:
                for page in self.client.allpages(self.start, self.prefix, namespace, self.filterredir, self.minsize,
                                                 self.maxsize, self.prtype if self.prmode else None, self.prlevel,
                                                 self.limit, self.dir, self.filterlanglinks, self.end):
                    yield page
        else:
            for page in self.client.allpages(self.start, self.prefix, None, self.filterredir, self.minsize,
                                             self.maxsize, self.prtype if self.prmode else None, self.prlevel,
                                             self.limit, self.dir, self.filterlanglinks, self.end):
                yield page
