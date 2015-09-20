# -*- coding: utf-8 -*-
from exceptions import Exception
from logging import CRITICAL, ERROR
from cmd import cmd


class GitException(Exception):

    def __init__(self, msg, level=ERROR):
        super(GitException, self).__init__()
        self.message = msg
        self.level = level


def check_git_error(f):

    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if result and result.find('fatal:') > -1:
            raise GitException(result, CRITICAL)
        if result and result.find('error:') == 0:
            raise GitException(result)
        return result

    return wrapper


class Git(object):

    branches = []
    current_branch = ''
    merge_msg_format = u'GitEmulator: Merge {0} into {1}'

    def __init__(self):
        self.__get_branches()

    def __get_branches(self):
        branches = cmd('git branch --list').strip().split('\n')
        for branch in branches:
            if branch[0] == '*':
                self.current_branch = branch[1:].strip()
                self.branches.append(self.current_branch)
            else:
                self.branches.append(branch.strip())

    def check_branch_exists(self, name):
        return name in self.branches

    def __checkout(self, branch):
        if self.current_branch != branch and self.check_branch_exists(branch):
            cmd('git checkout {0}'.format(branch))
            self.current_branch = branch

    @check_git_error
    def __commit(self, msg):
        return cmd(['git', 'commit', '-m', msg])

    @check_git_error
    def __merge(self, branch):
        return cmd('git merge {0} --squash'.format(branch))

    @check_git_error
    def __get_log(self):
        return cmd(['git', 'log', '--pretty=format:%H %P %s'])

    @check_git_error
    def __replace(self, target, replacer):
        return cmd('git replace -f {0} {1}'.format(target, replacer))

    def __find_previous_merge(self, source, destination):
        _search_msg = self.merge_msg_format.format(source, destination)
        log = self.__get_log().strip().split('\n')
        for message in log:
            info = message.split(' ', 2)
            if len(info) == 3 and info[2] == _search_msg:
                return info[0], info[1]
        return None

    def __delete_previous_merge(self, source, destination):
        prev_merge = self.__find_previous_merge(source, destination)
        if prev_merge is None:
            return
        _hash, parent_hash = prev_merge
        self.__replace(_hash, parent_hash)

    def merge(self, source, destination):

        if not self.check_branch_exists(source):
            raise AttributeError(u'Branch "{0}" doesn\'t exists'.format(source))
        if not self.check_branch_exists(destination):
            raise AttributeError(u'Branch "{0}" doesn\'t exists'.format(destination))

        self.__checkout(destination)

        self.__delete_previous_merge(source, destination)

        self.__merge(source)

        self.__commit(self.merge_msg_format.format(source, destination))

        return True
