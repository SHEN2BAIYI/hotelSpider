import sys
import time
import logging
import json
import os


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





