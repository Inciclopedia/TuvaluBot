MAIN_NAMESPACE = '(Principal)'


class Namespace(object):

    def __init__(self):
        self.id = None
        self.canonical_name = None
        self.__site_name = None

    @property
    def site_name(self):
        return self.__site_name

    def set_site_name(self, site_name):
        if site_name == '':
            self.__site_name = MAIN_NAMESPACE
        else:
            self.__site_name = site_name

    def from_dict(self, id, info):
        self.id = id
        self.canonical_name = info['canonical'] if 'canonical' in info else None
        self.set_site_name(info['*'])
