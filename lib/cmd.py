# -*- coding: utf-8 -*-
import subprocess


def cmd(command):
    if isinstance(command, basestring):
        command = command.split()
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, error = result.communicate()
    if error is not None:
        raise error
    return out
