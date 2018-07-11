import configparser
from collections import defaultdict


cfg_file = "base.ini"
cfg = defaultdict(lambda: None)
cfg_header = defaultdict(lambda: None)


def get_cfg_all():
    #print(cfg)
    return cfg

def get_cfg(key):
    return cfg[key]

def set_cfg(key, val):
    cfg[key] = val

def load_cfg_all():
    global cfg
    try:
        c = configparser.ConfigParser()
        c.read(cfg_file, encoding="utf-8")
        for s in c.sections():
            dic = dict(c.items(s))
            cfg = dict(cfg, **dic)
    except:
        print("Fail parse config file '%s'!"%cfg_file)
        return cfg
    for k,v in cfg.items():
        try:
            cfg[k] = float(v)
        except:
            continue
    return cfg

def get_cfg_header():
    return cfg_header

def load_cfg_header():
    global cfg_header
    cfg_header = load_cfg_section("request_header")
    return cfg_header

def load_cfg_section(section):
    try:
        c = configparser.ConfigParser()
        c.read(cfg_file, encoding="utf-8")
        return dict(c.items(section))
    except:
        print("Fail parse config file '%s'!"%cfg_file)

def get_cfg_plat():
    """return platform name"""
    #print(cfg['base_url'])
    return cfg['base_url'].split('.')[1]
    

def print_cfg():
    print(cfg)

        
if __name__ == '__main__':
    """test"""
    print(load_cfg_all())
    print(load_cfg_section('request_header'))
    print(get_cfg_plat())
    
    
