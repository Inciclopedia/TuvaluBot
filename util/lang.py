from abc import ABC, abstractmethod


class Lang(ABC):

    @abstractmethod
    def set_lang(self, langid: str):
        raise

    @abstractmethod
    def msg(self, msgid: str) -> str:
        raise

    def t(self, msgid: str) -> str:
        return self.msg(msgid)


class JsonLang(Lang):

    def __init__(self):
        self.__strings = None

    def set_lang(self, langid: str):
        import json
        with open("lang/{langid}.json".format(langid=langid), "r", encoding="utf-8") as f:
            self.__strings = json.load(f)

    def msg(self, msgid: str) -> str:
        path = msgid.split('.')
        obj = self.__strings
        for locator in path:
            if locator not in obj:
                return msgid
            obj = obj[locator]
        return obj
