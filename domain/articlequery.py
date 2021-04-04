from typing import Generator

from mwclient import Site
from mwclient.listing import Category
from mwclient.page import Page


def after(x1: str, x2: str):
    return x1 == x2 or sorted([x1, x2])[0] == x2


def before(x1: str, x2: str):
    return x1 == x2 or sorted([x1, x2])[1] == x2


def filterredir(value: str, article: Page):
    return value == 'all' or value == 'redirects' and article.redirect or \
           value == 'nonredirects' and not article.redirect


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
        self.category = None

    def invoke(self) -> Generator[str, None, None]:
        print("Buscando artículos...")
        if self.category:
            for article in self.client.categories[self.category]:
                if self.start and not after(article.name, self.start):
                    continue
                if self.end and not before(article.name, self.end):
                    continue
                if self.prefix and not article.name.startswith(self.prefix):
                    continue
                if self.namespaces and not str(article.namespace) in self.namespaces:
                    continue
                if self.filterredir and not filterredir(self.filterredir, article):
                    continue
                if self.minsize and article.length < self.minsize:
                    continue
                if self.maxsize and article.length > self.maxsize:
                    continue
                yield article.name
        elif self.namespaces:
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
