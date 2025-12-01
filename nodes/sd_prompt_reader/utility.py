__author__ = "receyuki"
__filename__ = "utility.py"
__copyright__ = "Copyright 2023"
__email__ = "receyuki@gmail.com"

def merge_dict(dict1, dict2):
    dict3 = dict1.copy()
    for k, v in dict2.items():
        dict3[k] = merge_str_to_tuple(v, dict3[k]) if k in dict3 else v
    return dict3


def remove_quotes(string):
    return str(string).replace('"', "").replace("'", "")


def add_quotes(string):
    return '"' + str(string) + '"'
