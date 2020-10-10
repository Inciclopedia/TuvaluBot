import inject


def configure_injector(binder):
    from util.configimpl import Config, ConfigImpl
    binder.bind(Config, ConfigImpl())
    from util.lang import JsonLang, Lang
    binder.bind(Lang, JsonLang())


def bind_injector():
    inject.configure(configure_injector)
