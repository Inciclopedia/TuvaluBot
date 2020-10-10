class Interwiki(object):

    def __init__(self, idioma, api, fake, skip):
        self.language = idioma
        self.api = api
        self.fake = fake
        self.skip = skip