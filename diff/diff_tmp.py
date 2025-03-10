#! /bin/bash/env python3
# -*- coding:UTF-8 -*-

from collections import deque
import base64
import json
import copy
import glob
import sys
import pandas as pd
sys.path.append("..")
from util.file import read_json,save_json

nokeys = {"HTTP_X_REQUEST_ID","X-Req-Json","X-Req-Bytes","Date","Server","x-req-json","date","server"}
key_headers = {"host","connection","content-length","transfer-encoding","range","upgrade","max-forwards","expect"}

def diff_req(req1,req2):
    # param req1, orign_req
    # param req2, parsed_req
    # req1[key] != req2[key] mod
    # req1[headers][key] != req2[headers][key] mod
    # req1[headers][key] key not in req2 del
    # req2[headers][key] key not in req1 add
    # result = {"mod":[key,key2],"add":[key,key2],"del":[key,key2]}
    # req = {
    #     "method":"GET",
    #     "uri":"/",
    #     "protocol":"HTTP/1.1",
    #     "authority":"",
    #     "headers":[
    #         ("Content-Length","1"),
    #         ("Range", "0-100"),
    #         ("Host", "localhost"),
    #         (" BAD-header-line",""),
    #         ("header-name", "BAD-header-value")
    #     ],
    #     # "body":"BBBBBB"
    #     "body":b"1\r\na"
    # }
    result = {}
    tmp_mod = []
    tmp_add = []
    tmp_del = []
    keys = (set(req1.keys()) | set(req2.keys()) ) - nokeys
    for key in keys:
        if "headers" == key:
            continue
        if key not in req2 and key in req1:
            tmp_del.append((key,req1[key]))
            continue
        if key in req2 and key not in req1:
            tmp_add.append((key,req2[key]))
            continue
        if(req1[key] != req2[key]):
            tmp_mod.append((key,req1[key],req2[key]))

    req1_headers = deque(req1["headers"])
    req2_headers = deque(req2["headers"])
    req1_headers_len = len(req1_headers)
    req2_headers_len = len(req2_headers)
    i = 0
    flag = False
    while i < req1_headers_len:
        flag = False
        req1_header = req1_headers.popleft()
        j = 0
        req2_headers_len = len(req2_headers)
        while j < req2_headers_len:
            req2_header = req2_headers.popleft()
            header1_name = req1_header[0]
            header2_name = req2_header[0]
            if(header1_name == header2_name):
                # value == value
                if(req1_header[1] == req2_header[1]):
                    flag = True
                    break
            req2_headers.append(req2_header)
            j = j +1
        if not flag: 
            req1_headers.append(req1_header)
        i = i +1
    req1_headers_len = len(req1_headers)
    req2_headers_len = len(req2_headers)
    i = 0
    while i < req1_headers_len:
        flag = False
        req1_header = req1_headers.popleft()
        j = 0
        req2_headers_len = len(req2_headers)
        while j < req2_headers_len:
            req2_header = req2_headers.popleft()
            header1_name = req1_header[0]
            header2_name = req2_header[0]
            if(header1_name == header2_name):
                 # value == value
                if(req1_header[1] != req2_header[1]):
                    flag = True
                    tmp_mod.append((header1_name,req1_header[1],req2_header[1]))
                    break
            req2_headers.append(req2_header)
            j = j +1
        if not flag: 
            req1_headers.append(req1_header)
        i = i +1
    if len(req1_headers) >0 : tmp_del = [(item[0],item[1]) for item  in req1_headers ]
    if len(req2_headers) >0 : tmp_add = [(item[0],item[1]) for item  in req2_headers ]


    result = {
        "mod":tmp_mod,
        "add":tmp_add,
        "del":tmp_del
    }   
    
    return result

def diff_server_twice_parse(res1,res2):
    # raw req1
    # print(req1,res1,req2,res2)
    # req1 = b'GET / HTTP/1.1\r\nHost: _HOST_\r\nX-Request-ID: _REQUEST_ID_\r\n\r\n'
    # res1 = b'HTTP/1.1 200 OK\r\nDate: Fri, 13 Sep 2024 18:14:55 GMT\r\nServer: Apache/2.4.54 (Debian)\r\nX-Powered-By: PHP/7.4.33\r\nX-Req: eyJtZXRob2QiOiJHRVQiLCJ1cmkiOiIvaW5kZXgucGhwIiwicHJvdG9jb2wiOiJIVFRQLzEuMSIsImhlYWRlcnMiOnsiSFRUUF9IT1NUIjoiX0hPU1RfIiwiSFRUUF9YX1JFUVVFU1RfSUQiOiJfUkVRVUVTVF9JRF8ifSwiaW5wdXQiOiIifQ==\r\nContent-Length: 22\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nThis is a test message' 
    # req2 = b'GET / HTTP/1.1\r\nHost: _HOST_\r\nX-Request-ID: _REQUEST_ID_\r\nAccept: */*\r\n\r\n' 
    # res2 = b'HTTP/1.1 200 OK\r\nDate: Fri, 13 Sep 2024 18:15:00 GMT\r\nServer: Apache/2.4.54 (Debian)\r\nX-Powered-By: PHP/7.4.33\r\nX-Req: eyJtZXRob2QiOiJHRVQiLCJ1cmkiOiIvaW5kZXgucGhwIiwicHJvdG9jb2wiOiJIVFRQLzEuMSIsImhlYWRlcnMiOnsiSFRUUF9IT1NUIjoiX0hPU1RfIiwiSFRUUF9YX1JFUVVFU1RfSUQiOiJfUkVRVUVTVF9JRF8iLCJIVFRQX0FDQ0VQVCI6IiovKiJ9LCJpbnB1dCI6IiJ9\r\nContent-Length: 22\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nThis is a test message'
    try:
        (res1,parsed_req1) = analy_res_http1_raw(str(res1,encoding="utf-8"))
        (res2,parsed_req2) = analy_res_http1_raw(str(res2,encoding="utf-8"))
    except UnicodeDecodeError as e:
        print("decode error")
        return False
    diff = diff_res(res1,res2)
    diff_http = diff_req(parsed_req1,parsed_req2)
    num = len(diff_http["add"])
    # print("diffres",diff)
    # print("diffreq",diff_http)
    if is_empty_diff(diff) and (1 == num):
        return False
    return True

def diff_server_single_parse(req,res):
    # req = b'GET / HTTP/1.1\r\nHost: _HOST_\r\nX-Request-ID: _REQUEST_ID_\r\n\r\n'
    # res = b'HTTP/1.1 200 OK\r\nDate: Fri, 13 Sep 2024 18:14:55 GMT\r\nServer: Apache/2.4.54 (Debian)\r\nX-Powered-By: PHP/7.4.33\r\nX-Req: eyJtZXRob2QiOiJHRVQiLCJ1cmkiOiIvaW5kZXgucGhwIiwicHJvdG9jb2wiOiJIVFRQLzEuMSIsImhlYWRlcnMiOnsiSFRUUF9IT1NUIjoiX0hPU1RfIiwiSFRUUF9YX1JFUVVFU1RfSUQiOiJfUkVRVUVTVF9JRF8ifSwiaW5wdXQiOiIifQ==\r\nContent-Length: 22\r\nContent-Type: text/html; charset=UTF-8\r\n\r\nThis is a test message' 
    try:
        req = analy_req_http1_raw(str(req,encoding="utf-8"))
        (res,parsed_req) = analy_res_http1_raw(str(res,encoding="utf-8"))
    except UnicodeDecodeError as e:
        print("decode error")
        return False
        # print(req,parsed_req)
    diff = diff_req_parsed(req,parsed_req)
        # print(diff);
    if is_empty_diff(diff):
        return False
    print(diff)
    return True

def analy_req_http1_raw(req_str):
    req = {
        "method":"GET",
        "uri":"/",
        "protocol":"HTTP/1.1",
        "authority":"",
        "headers":[
            ("Content-Length","1"),
            ("Range", "0-100"),
            ("Host", "localhost"),
            (" BAD-header-line",""),
            ("header-name", "BAD-header-value")
        ],
        # "body":"BBBBBB"
        "body":b"1\r\na"
    }
    # req_str = 'GET / HTTP/1.1\r\nContent-Length: 1\r\n\r\nBBBB'
    req = {"headers":[],"body":""}
    if req_str is None:
        return req
    req_parts = req_str.split('\r\n\r\n',1)
    if len(req_parts) < 2:
        # http/0.9?
        pass
    else:
        req["body"] = req_parts[1]
        req_line = req_parts[0].split('\r\n')[0]
        headers = req_parts[0].split('\r\n')[1:]
        # # is_req_line()?
        # # 
        req_line_parts = req_line.split(" ",3)
        if len(req_line_parts) < 3:
            req["protocol"] = "HTTP/0.9"
        else:
            req["protocol"] = req_line_parts[2]
        req["method"] = req_line_parts[0]
        req["uri"] = req_line_parts[1]
        tmp_headers = []
        for header_line in headers:
            header_parts = header_line.split(": ",1)
            header_name = header_parts[0]
            if header_name.lower() in key_headers:
                tmp_headers.append((header_parts[0],header_parts[1] if len(header_parts) >1  else ''))
        req["headers"] = tmp_headers

        # body chunked
        return req
    pass

def analy_res_http1_raw(res_str):
    # res_str = 'HTTP/1.1 200 OK\r\nHost: localhost\r\nContent-Length: 4\r\n\r\nBBBB'
    req = {
        "response-line":"HTTP/1.1 200 Ok",
        "protocol":"HTTP/1.1",
        "status":"200",
        "reason":"OK",
        "headers":[
            ("Content-Length","1"),
            ("Range", "0-100"),
            ("Host", "localhost"),
            (" BAD-header-line",""),
            ("header-name", "BAD-header-value")
        ],
        # "body":"BBBBBB"
        "body":b"1\r\na"
    }
    # res_str = 'HTTP/1.1 200 OK\r\nHost: localhost\r\nContent-Length: 4\r\n\r\nBBBB'
    res = {"status":"XXX","headers":[],"body":"","flag":"TIME_OUT"}
    parsed_req = {"headers":{}}
    if "" == res_str:
        return (res,parsed_req)
    res_parts = res_str.split('\r\n\r\n',1)
    if len(res_parts) < 2:
        # 
        # 错误的格式？
        res["flag"] = "HTTP/0.9"
        return (res,parsed_req)
    else:
        res["flag"] = "TRUE"
        res["body"] = res_parts[1]
        res_line = res_parts[0].split('\r\n')[0]
        headers = res_parts[0].split('\r\n')[1:]
        # is_req_line()?
        res["response-line"] = res_line
        # 
        res_line_parts = res_line.split(" ",3)
        # res["protocol"] = res_line_parts[0]
        res["status"] = res_line_parts[1]
        # res["reason"] = res_line_parts[2]
        tmp_headers = []
        for header_line in headers:
            header_parts = header_line.split(": ",1)
            header_name = header_parts[0]
            header_value = header_parts[1] if len(header_parts) >1  else ''
            if("X-Req-Bytes" == header_parts[0] or "x-req-bytes" == header_parts[0]):
                parsed_req = get_parsed_req_bytes(header_value)
            if(header_parts[0] in nokeys):
                continue
        return (res,parsed_req)
    pass




def get_parsed_req_bytes(req_bytes):
    return analy_req_http1_raw(str(base64.b64decode(req_bytes),encoding="utf-8"))

def is_empty_diff(diff):
    # diff= {
    #     "add":[],
    #     "del":[],
    #     "mod":[]
    # }
    if 0 == len(diff["add"]) + len(diff["del"]) + len(diff["mod"]):
        return True
    return False

def check_status(res):
    if res["status"].startswith("1") or res["status"].startswith("2"):
        return True

def exist_diff(_diff):
    for k in _diff:
        if _diff[k] != 0:
            return True

def diff(res_str1,res_str2):
    # diff {"0"} ==
    # diff {"1"} state diff
    # diff {"2"} status diff
    # diff {"3"} ziduan diff
    res1,req1 = analy_res_http1_raw(res_str1)
    res2,req2 = analy_res_http1_raw(res_str2)
    if res1["flag"] != res2["flag"]:
        return 1
    elif res1["flag"] == "TRUE":
        #  HTTP/1.1 normal
        if res1["status"] != res2["status"]:
            return 2
        elif check_status(res1):
            _diff_res = diff_req(res1,res2)
            if not is_empty_diff(_diff):
                return 3
    
    return 0
        

    
    pass








    

if __name__ == "__main__":
   
    # req = "POST * HTTP/1.0\r\nHost: hostname\r\nConnection: close\r\nX-Request-ID: 6\r\nContent-LENGTH\x00: 7\r\nRange&%: bytes=0-1000\r\n\r\nBBBB"
    # print(analy_req_http1_raw(req))
    # req2 = "GET / HTTP/1.1\r\nHost: hostname\r\nConnection: close\r\nTransfer-Encoding: chunked\r\n\r\n\r\n12345"
    # req2 = analy_req_http1_raw(req2)
    # req1 = analy_req_http1_raw(req)
    # result = diff_req_raw(req1,req2)
    # print(result)
    # res_str = 'HTTP/1.1 200 OK\r\nHost: localhost\r\nContent-Length: 4\r\n\r\nBBBB'
    # res1 =  {"method":"GET","uri":"/","protocol":"HTTP/1.1","headers":{"HTTP_CONTENT_LENT":""},"body":"aaa"}
    # res2 =  {"method":"HEAD","uri":"*","protocol":"HTTP/1.1","headers":{"HTTP_TRANSFER_ENCODING":"chunked","HTTP_CONTENT_LENGTH":"9"},"body":"1\r\naaa"}
    # result = diff_req_json(res1,res2)
    # print(result)
    # print(analy_res_http1(res_str))
    # diff_server_single_parse()
    # file_paths = glob.glob("../data/out0.json")
    file_paths = glob.glob("../data/base/out0.json")
    _diff = {}
    result = []
    for file_path in file_paths:
        data  = read_json(file_path)
        for item in data:
            resList = item["resList"]
            count = len(resList)
            if count < 2:
                print("data error")
                exit(0)
            
            for i in range(count):
                for j in range(i+1,count):
                    _diff[f"{i}-{j}"] = diff(resList[i]["res"],resList[j]["res"])
            if exist_diff(_diff):
                _diff["seed"] = item["seed"]
                result.append(_diff)
            break
    # print(result)
    df = pd.DataFrame(result)
    df.to_csv("base.csv")
    pass
