import json
import sys
sys.path.append("..")
from util.file import read_json,save_json




request_line = ['GET / HTTP/1.1','POST / HTTP/1.1','POST / HTTP/0.9','HEAD / HTTP/1.1']

# key-headers
header_names = ['Content-Length','Range','Upgrade',"Host","Transfer-Encoding","Connection","Max-Forwards","Expect"]

# load headers file
file_path = "../rfc/common_header.json"
common_headers = read_json(file_path)
file_path = "../rfc/other_header.json"
other_headers = read_json(file_path) 
file_path = "../rfc/ban_header.json"
ban_headers = read_json(file_path)



file_path = "./base/req-header.json"
req_header_base_grammar = read_json(file_path)

file_path = "./base/req-body.json"
req_body_base_grammar = read_json(file_path)

# 根据测试的结果补充生成fuzz语法测试文件

req_body_base_grammar["<request-line>"] = request_line
file_path = "./fuzz/req-body.json"
save_json(req_body_base_grammar,file_path)

tmp_list = []
for item in header_names:
    tmp_list.append("<"+item+">")
    req_header_base_grammar["<"+item+">"] = ["<"+item+"-name>"+"<colon><space>"+"<"+item+"-value>"+"<newline>"]
    req_header_base_grammar["<"+item+"-name>"] = [item]

req_header_base_grammar["<header>"] = tmp_list

for header_name in header_names:
    if header_name in  common_headers:
       req_header_base_grammar["<"+header_name+"-value>"] = common_headers[header_name]

    if header_name in  other_headers:
       req_header_base_grammar["<"+header_name+"-value>"] = other_headers[header_name]
    if header_name in  ban_headers:
       req_header_base_grammar["<"+header_name+"-value>"] = ban_headers[header_name]

req_header_base_grammar["<request-line>"] = request_line
file_path = './fuzz/req-header.json'
save_json(req_header_base_grammar,file_path)