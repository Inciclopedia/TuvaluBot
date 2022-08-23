import json
from abc import ABC, abstractmethod


class Config(ABC):

    @abstractmethod
    def bootstrap(self, script_description):
        raise NotImplementedError

    @property
    @abstractmethod
    def args(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def config(self) -> dict:
        raise NotImplementedError

    @property
    @abstractmethod
    def interwikis(self) -> dict:
        raise NotImplementedError


class ConfigImpl(Config):

    def __init__(self):
        self.__args = None
        self.__config = None
        self.__interwikis = None

    def __parse_args(self, description):
        global DEBUG
        import argparse
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('realm', type=str, help='Wiki from which we load config (inciclopedia, uncyclopedia...)')
        parser.add_argument('user', type=str, nargs='?',
                            help='Bot username', default=None)
        parser.add_argument('password', type=str, nargs='?', help='Bot password', default=None)
        parser.add_argument('-t', '--tasks', default='', help='Location of the tasks file')
        parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
        args = parser.parse_args()
        return args

    def bootstrap(self, script_description):
        self.__args = self.__parse_args(script_description)
        with open("config/{realm}/config.json".format(realm=self.__args.realm), "r", encoding="utf-8") as f:
            self.__config = json.load(f)
        with open("config/{realm}/interwiki.json".format(realm=self.__args.realm), "r", encoding="utf-8") as f:
            self.__interwikis = json.load(f)

    @property
    def args(self):
        if self.__args is None:
            raise ValueError("You must call bootstrap() from config before asking values")
        return self.__args

    @property
    def config(self) -> dict:
        if self.__config is None:
            raise ValueError("You must call bootstrap() from config before asking values")
        return self.__config

    @property
    def interwikis(self) -> dict:
        if self.__interwikis is None:
            raise ValueError("You must call bootstrap() from config before asking values")
        return self.__interwikis
