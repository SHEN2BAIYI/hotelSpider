import sys
import time
import logging
import json
import os
import ctypes
import inspect


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def info_format(info):
    info = '{} {}'.format(time.strftime("%m-%d %H:%M:%S", time.localtime()), info)
    return info


def dict2json(dict_list, json_path):
    logger.debug('保存 cookie 文件：{}。'.format(json_path))

    if os.path.exists(json_path):
        os.remove(json_path)

    with open(json_path, mode='w', encoding='utf-8') as f:
        json.dump(dict_list, f)


def json2dict(json_path):
    logger.info('读取 cookie 文件：{}。'.format(json_path))
    with open(json_path, mode='r', encoding='utf-8') as f:
        dict_data = json.load(f)

    return dict_data


def get_logger(LEVEL, log_file=None):
    head = '[%(asctime)-15s] [%(levelname)s] [%(filename)s] [%(funcName)s] %(message)s'
    if LEVEL == 'info':
        logging.basicConfig(level=logging.INFO, format=head)
    elif LEVEL == 'debug':
        logging.basicConfig(level=logging.DEBUG, format=head)
    logger = logging.getLogger()
    if log_file:
        fh = logging.FileHandler(log_file)
        logger.addHandler(fh)
    return logger


logger = get_logger('info')





