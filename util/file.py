#! /bin/bash/env python3
# -*- coding:UTF-8 -*-


import os
from loguru import logger

import json


# save list to txt
def save_data(result, path):
    save_data_type(result,path,"w")
    return

def save_data_type(result, path,type):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, type) as f:
        f.write(result)
    logger.info("Save data to {}".format(path))
    return

def save_json(result,path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(result,f)
        f.close()
    logger.info("Save data to {}".format(path))
        
def read_data(path):
    data = read_data_type(path,"r")
    return data

def read_json(path):
    with open(path, "r") as f:
        data = json.load(f)
        f.close()
    
    logger.info("read data to {}".format(path))
    return data

def read_data_type(path,type):
    with open(path, type) as f:
        data = f.read()
        f.close()
    logger.info("read data to {}".format(path))
    return data

