#! /bin/bash/env python3
# -*- coding:UTF-8 -*-


import requests
import re
import os
from loguru import logger
import time
import random
import xml.etree.ElementTree as ET
import json
import base64



# save list to txt
def save_data(result, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(result)
    logger.info("Save data to {}".format(path))
    return

def save_list_newline(list,path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.writelines(list)
    logger.info("Save data to {}".format(path))
    return

def read_data(file_path,type):
    with open(file_path, type) as f:
        data = f.read()
        f.close()
    return data

def getABNFByXML():
    # doing
    # pass

    file_path = "../rfc/xml/rfc9112.xml"
    tree = ET.ElementTree(file=file_path)

    for elem in tree.iter(tag='sourcecode'):
        if 'abnf' in elem.attrib['type']:
            text = elem.text.replace('\n','\r\n')
            # two question
            # 1. empty line  
            # formate 
            # 2. uri = <section URI>  // invalid abnf 
            # according to parse all http doc, ignore or pass
            # Or Recursive parsing
            print(text)



    

def getHTTPMessageByTXT(data):

    # RFC_DIR = "../rfc/txt/"
    # file_path = "../rfc/txt/rfc9421.txt"
    req_line_pattern = r"^[A-Z]+ \S+ HTTP\/\d\.\d"
    res_line_pattern = r"^HTTP\/\d\.\d \d{3} [A-Z]+"
    header_pattern = r'^[A-Za-z_-]+: .*?'
    message = {

        "req_lines":[],
        "req_headers":[],
        "req_bodys":[],
        "tables":[],
    }
    # "\r\n\r\nHTTP-Message\r\n\r\n"
    paras = data.split("\r\n\r\n")
    mess_flag = False
    for para in paras:
        para = para.strip()
        # "\r\n","\r","\n"
        if(re.match(r"^[+-]",para)):
            # table
            message["tables"].append(para)
            continue
        if (mess_flag and len(para) > 0):

            mess_flag = False

            message["req_bodys"].append(para)
        if(len(para)>1):
            lines = para.split("\r\n")
            for i in range(len(lines)):
                if i == 0:
                    match_req_line = re.match(req_line_pattern,lines[i])
                    match_res_line = re.match(res_line_pattern,lines[i])
                match_header = re.match(header_pattern,lines[i])
                if match_header:
 
                    message["req_headers"].append(lines[i])                           
              
            if match_req_line or match_res_line:
                if match_header:
                    mess_flag = True
                # print("req_line" if match_req_line else "res_line")
                # print(lines[i])
                if match_req_line:
                    message["req_lines"].append(lines[0])
    return message
     




# RFC clean
def clean_rfc(data):
    # '\r\n\r\n' split
    paras = data.split("\n\n")
    start = 0
    end = len(paras)
    for i in range(len(paras)):
        para = paras[i]
        if len(para) < 1 : continue
        if para[0] == "\n" : para = para[1:]
        if para[-1] == "\n" : para = para[0:-1]
        match = re.search(r"^1.  Introduction$",para)
        if match:
            start = i
        match = re.search(r"^\d+.  References$",para)
        if match:
            end = i
    paras = paras[start:end+1]
    tmp_para = ""
    new_paras = []
    for i in range(len(paras)):
        paras[i] = paras[i].strip()
        match = re.search(r"^\d.*?",paras[i])
        if match:
            continue
        if re.search(r"\[Page \d+\]",paras[i]) : continue
        match = re.search(r"[\.]$",paras[i])
        if match:
            continue
        match = re.search(r"^[a-zA-Z+-]",paras[i])
        if not match:
            continue
        lines = paras[i].split("\n")
        double_flag = False
        new_line = ""
        new_lines = []
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            new_line = ''
            if(len(lines[i]) < 1):
                continue
            if not double_flag :
                if lines[i][-1] == "\\" :
                    double_flag = True
                    start_line = i
                else :
                    new_line = lines[i]
    
            else:
                if lines[i][-1] != "\\":
                    end_line = i
                    tmp_lines = lines[start_line:end_line]
                    new_line = ''.join(item[:-1] for item in tmp_lines)
                    new_line += lines[end_line]
                    double_flag = False
            new_lines.append(new_line)
        new_para = "\r\n".join(new_lines)
        new_paras.append(new_para)
            
    result = "\r\n\r\n".join(new_paras)
    return result


    

def getHTTPMessageByXML():
    file_path = "../rfc/xml/rfc9112.xml"
    tree = ET.ElementTree(file=file_path)
    message = {

        "req_lines":[],
        "req_headers":[],
        "req_bodys":[],
        "tables":[]
    }
    for elem in tree.iter(tag='sourcecode'):
        if 'type' in elem.attrib and  'message' in elem.attrib['type']:
            data = elem.text
            data = clean_rfc(data)
            res = getHTTPMessageByTXT(data)
            print(res)


    return message
  
def getHTTPMessage():
     
    
     RFC_DIR = "../rfc/txt/"
     RFC_CLEANED_DIR = "../rfc/cleaned_test/"
     RFC_RESUTL_DIR = "../rfc/"
     req_line_file_path = '../rfc/req_line.txt'
     header_file_path = '../rfc/header.txt'
     body_file_path = '../rfc/body.txt'
     table_file_path = "../rfc/table.txt"
     tables = set()
     req_lines = set()
     req_headers= set()
     req_bodys = set()
     files = os.listdir(RFC_DIR)
     for file_name in files:
         file_path = RFC_DIR+file_name
         with open(file_path,"r") as f:
             data = f.read()
             f.close()
         data = clean_rfc(data)
         res = getHTTPMessageByTXT(data)
         req_lines = req_lines | set(res["req_lines"])
         req_headers = req_headers | set(res["req_headers"])
         req_bodys = req_bodys | set(res["req_bodys"])
         tables = tables | set(res["tables"])
     save_data("\r\n".join(req_lines),req_line_file_path)
     save_data("\r\n".join(req_headers),header_file_path)
     save_data("\r\n\r\n".join(req_bodys),body_file_path)
     save_data("\r\n\r\n".join(tables),table_file_path)

            
def getRFCHTTPFileName():
    url = "https://www.iana.org/assignments/http-fields/http-fields.xml"
    file_path = "../rfc/http-fields.xml"
    # res = requests.get(url)
    # with open(file_path,"w") as f:
    #     f.write(res.text)
    #     f.close()
    with open(file_path,"r") as f:
        data = f.read()
        f.close()
    root = ET.fromstring(data)
    xml_namespace = "{http://www.iana.org/assignments}"
    headers = {}
    # print(root.tag)
    for item in root.iter(tag = xml_namespace + "record"):
    #   <record updated="2021-10-01">
    #   <value>Accept</value>
    #   <status>permanent</status>
    #   <xref type="rfc" data="rfc9110">RFC9110, Section 12.5.1: HTTP Semantics</xref>
    #   </record>
        # print(item.find(xml_namespace + "value").text+"-"*3+)
        name = item.find(xml_namespace + "value").text
        status = item.find(xml_namespace + "status").text
        headers[name] = status
    return headers
        

    # pass





if __name__=="__main__":

    # reqs_line = {"method":[],"uri":[],"http_version":[]}
    # rfc_normal_header ={"":[],}, rfc_ban_header = {},other_header = {}

 

    headers = getRFCHTTPFileName()
    rfc_common_name = []
    rfc_ban_name = []
    other_name = []
    rfc_common_headers = {}
    rfc_ban_headers = {}
    other_headers = {}
    for name in headers.keys():
        if headers[name] == "permanent":
            rfc_common_name.append(name)
        elif headers[name] == "deprecated" or headers[name] == "obsoleted":
            rfc_ban_name.append(name)
        else:
            other_name.append(name)
    
    file_path = "../mdn/header.txt"
    data = read_data(file_path,"r")
    lines = set(data.split("\n"))
    file_path = "../rfc/header.txt"
    data = read_data(file_path,"r")
    lines = lines | set(data.split("\n"))
    for line in lines:
        # <header-name>:<sp><header-value>
        parts = line.split(":",1)
        name = parts[0]
        value = parts[1].strip()
        if name in rfc_common_name:
            tmp_headers = rfc_common_headers
        elif name in rfc_ban_name:
            tmp_headers = rfc_ban_headers
        else:
            tmp_headers = other_headers
        if name not in tmp_headers:
            tmp_headers[name] = []
        if value not in tmp_headers[name]:
            tmp_headers[name].append(value)
    # print(rfc_common_headers)
    common_header_path = "../rfc/common_header.json"
    ban_header_path = "../rfc/ban_header.json"
    other_header_path = "../rfc/other_header.json"
    save_data(json.dumps(rfc_common_headers),common_header_path)
    save_data(json.dumps(rfc_ban_headers),ban_header_path)
    save_data(json.dumps(other_headers),other_header_path)


    




