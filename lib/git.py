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

    def __track_all_branches(self):
        remote_branches = cmd('git branch -r').strip().split('\n')
        for branch in remote_branches:
            if branch.find('HEAD') > -1 or branch.find('master') > -1:
                continue
            cmd('git branch --track {0} {1}'.format(branch.strip().replace('origin/', ''), branch.strip()))
        # cmd('git fetch --all')

    def __get_branches(self):
        self.__track_all_branches()
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
    def __get_last_commit_hash(self):
        return cmd('git rev-parse HEAD').strip()

    @check_git_error
    def __merge(self, branch, param=''):
        return cmd('git merge {0} --squash {1}'.format(branch, param))

    @check_git_error
    def __get_log(self):
        return cmd(['git', 'log', '--pretty=format:%H %P %s'])

    @check_git_error
    def __replace(self, target, replacer):
        return cmd('git replace -f --graft {0} {1}'.format(target, replacer))

    @check_git_error
    def __reset(self, _hash):
        return cmd('git reset {0}'.format(_hash))

    @check_git_error
    def __clean(self):
        return cmd('git clean -f')

    def __find_previous_merge_with_child(self, source, destination, exclude=None):
        if not exclude:
            exclude = []
        _search_msg = self.merge_msg_format.format(source, destination)
        log = self.__get_log().strip().split('\n')
        for idx, message in enumerate(log):
            info = message.split(' ', 2)
            if len(info) == 3 and info[0] not in exclude and info[2] == _search_msg:
                # return child hash, current hash & parent hash
                return log[idx-1].split(' ', 2)[0], info[0], info[1]
        return None

    def __find_previous_merge(self, source, destination):
        _search_msg = self.merge_msg_format.format(source, destination)
        log = self.__get_log().strip().split('\n')
        for message in log:
            info = message.split(' ', 2)
            if len(info) == 3 and info[2] == _search_msg:
                return info[0], info[1]
        return None

    def __delete_previous_merge(self, source, destination):
        prev_merge = self.__find_previous_merge_with_child(source, destination)
        if prev_merge is None:
            return
        child_hash, _hash, parent_hash = prev_merge
        if _hash == self.__get_last_commit_hash():
            # if merge commit is the last one
            self.__reset(parent_hash)
            self.__clean()
            return
        else:
            self.__replace(child_hash, parent_hash)
            return True

    def merge(self, source, destination):

        if not self.check_branch_exists(source):
            raise AttributeError(u'Branch "{0}" doesn\'t exists'.format(source))
        if not self.check_branch_exists(destination):
            raise AttributeError(u'Branch "{0}" doesn\'t exists'.format(destination))

        self.__checkout(destination)

        status = self.__delete_previous_merge(source, destination)
        merge_param = ''
        if status is True:
            merge_param = '-X theirs'
        self.__merge(source, merge_param)

        self.__commit(self.merge_msg_format.format(source, destination))

        return True
