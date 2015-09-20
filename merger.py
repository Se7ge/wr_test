#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from lib.manager import Manager
from lib.git import GitException
import logging

logger = logging.getLogger(__name__)


def main(argv):
    try:
        manager = Manager(argv)
        manager.execute()
    except AttributeError as e:
        logger.error(e)
    except GitException as e:
        logger.log(e.level, e.message)
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    main(sys.argv[1:])
