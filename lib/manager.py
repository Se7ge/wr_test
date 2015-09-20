# -*- coding: utf-8 -*-
import sys
import logging
from git import Git, GitException

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class Manager(object):

    def __init__(self, params):
        self.git = Git()
        self.__init_properties(params)

    def __init_properties(self, params):
        if len(params) != 2:
            raise AttributeError(u'Wrong number of arguments')
        self.command = 'merge'
        self.params = params

    def __merge(self, source, destination):
        try:
            result = self.git.merge(source, destination)
        except GitException as e:
            raise e
        else:
            return result

    def execute(self):
        if self.command == 'merge':
            source, destination = self.params
            if self.__merge(source, destination):
                logger.info(u'Merge branch "{0}" into "{1}" succeeded'.format(source, destination))
        else:
            raise AttributeError(u'Command "{0}" not supported'.format(self.command))
