import inject


def configure_injector(binder):
    from util.config import IConfig, Config
    binder.bind(IConfig, Config())
    from util.lang import JsonLang, Lang
    binder.bind(Lang, JsonLang())


def bind_injector():
    inject.configure(configure_injector)
