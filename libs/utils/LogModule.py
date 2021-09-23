#!/usr/bin/env python
import logging
import sys
import inspect
import os.path
import os

#logging.config.dictConfig("log.conf")

def configure(name, console=True, debug=False, logfile=None):
    """
    Configure the logger
    :param name: Name of the logger object
    :param console: Enable/Disable console logging (Default: True)
    :param debug: Enable/Disable debug logging to console (Default: False)
    :param logfile: Log file output (Default: None)
    :return : None
    """
    if os.environ.get("DISABLECONSOLE", False):
        console = False
    logger = logging.getLogger(name)
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter('%(asctime)s	%(name)50s  %(funcName)20s  %(levelname)10s : %(message)s')
    logger.setLevel(level)

    if console:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    if logfile:
        handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

def getLogger(name):
    """
    Get the logger object
    :param name: Name of the logger object
    :return: Logger object
    """
    if "." in name:
        name = name.split(".")[-1]
    stack = inspect.stack()
    if name == "__main__":
        module = stack[1][1]
        moduleName = os.path.basename(module).split(".")[0]
        name = moduleName
    else:
        modulesPathList = []
        for item in stack[::-1]:
            if item[4] and "import " in item[4][0]:
                modulesPathList.append(os.path.basename(item[1].split(".")[0]))
        if modulesPathList != []:
            modulesPathList.append(name)
            name = ".".join(modulesPathList)
    logger = logging.getLogger(name)
    return logger
