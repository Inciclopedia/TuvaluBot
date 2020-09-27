from typing import Generator

from mwclient import Site

from domain.namespace import Namespace


class SiteInfo(object):

    @staticmethod
    def namespace_list(sitio: Site) -> Generator[Namespace, None, None]:
        salida = sitio.api('query', meta='siteinfo', siprop='namespaces')
        namespaces_dict = salida['query']['namespaces']
        for id, namespace_info in namespaces_dict.items():
            namespace = Namespace()
            namespace.from_dict(id, namespace_info)
            yield namespace
