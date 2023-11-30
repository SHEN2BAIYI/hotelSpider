import os
import configparser


CONFIG_FILE = './config/Config.cfg'

""" 通过输入的 dict 形成 cfg 文件 """
def save_config(cfg_dict):
    conf = configparser.ConfigParser()

    # 遍历
    for key1 in cfg_dict.keys():
        # 设置段名
        conf.add_section(key1)

        # 增加参数名
        for key2 in cfg_dict[key1].keys():
            conf.set(key1, key2, cfg_dict[key1][key2])

    # 写入
    try:
        cfg_file = open(CONFIG_FILE, 'w')
    except FileNotFoundError:
        os.mkdir('./config')
        cfg_file = open(CONFIG_FILE, 'w')
    conf.write(cfg_file)
    cfg_file.close()


""" 读取 cfg 文件, 返回 dict """
def read_config():
    try:
        if os.path.exists(CONFIG_FILE):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)

            config = {s: dict(config.items(s)) for s in config.sections()}
            return config
    except Exception:
        pass
    return None




