#! /bin/bash/env python3
# -*- coding:UTF-8 -*-

# http1
import sys
from ats.input_tree import InputTree
from util.file import read_data,read_json
from util.helper_functions import print_singel_byte_result,print_len_result,print_dict
from util.helper_functions import send,get_status,print_dict
import random
import copy
from fuzzer import Fuzzer
from diff.diff_http1 import diff_server_single_parse,diff_server_twice_parse



def request_header_normal_test(url,host,verbose):
    seed = 1
    file_path = "./grammar/normal/req-header.json"
    result = {}
    grammar = read_json(file_path)
    ats = InputTree(grammar,seed,url,verbose)
    trees = ats.build_trees(ats.root)
    def test():
        for tree in trees:
            tmp_tree = copy.deepcopy(tree)
            node = ats.find_nodes_by_symbol(tree,"<header>")[0].children[0]
            tmp_node = ats.find_nodes_by_symbol(tmp_tree,"<header>")[0].children[0]
            node.symbol = ""
            # print(str(header_node.children))
            base_req = ats.tree_to_str(tree)
            # print(base_req)
            # print(tmp_header_node.symbol)
            base_res = send(url,base_req)
            # headers= {"Connection":["close","keep-alive"]}
            header_text = tmp_node.symbol
            node.symbol = header_text
            tmp_result = []
            for key in headers:
                print(f"key:{key} testing")
                for value in headers[key]:
                    tmp_header_text = header_text
                    tmp_header_text = tmp_header_text.replace("__HEADER_NAME__",key)
                    tmp_header_text = tmp_header_text.replace("__HEADER_VALUE__",value)
                    tmp_node.symbol = tmp_header_text
                    req = ats.tree_to_str(tmp_tree)
                    res = send(url,req)
                    if diff_server_single_parse(req,res) or diff_server_twice_parse(base_res,res):
                        print("intesting header"+key)
                        print(f"req: {req}")
                        print(f"res: {res}")
                        print(f"base_res: {base_res}")
                        tmp_result.append(key)
                        break
                
            return tmp_result
    
    # common_header rfc normal header
    file_path = "./rfc/common_header.json"
    headers = read_json(file_path)
    result["common"] = test()





if __name__ == "__main__":
    fuzzer = Fuzzer(True,seed='0',outfilename=None,seedfile=None,no_sending=True)
    normal_test_cases = ["request_line_normal_test"]
   
    for normal_test_case in normal_test_cases:
        for url in fuzzer.target_urls:
            globals()[normal_test_case](url,fuzzer.target_hosts[url],False) 
    pass
