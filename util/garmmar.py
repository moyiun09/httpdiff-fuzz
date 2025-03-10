#! /bin/bash/env python3
# -*- coding:UTF-8 -*-
import json
# 根据http1的特性生成三种语法，
from file import read_data,save_data,read_json,save_json

# req_line
def req_line_grammar_gen():

    # rule fusion 若对同类语法规则做扩展
    file_path = "../grammar/base/req-line.json"
    grammar = read_json(file_path)

    file_path = "../rfc/req_line.json"
    # rules = {"method":[],"uri":[],"http_version":[]}
    rules = read_json(file_path)

    for key in rules:
        # rule in config.grammar
        # <method>  in config.grammar
        rule_name = "<"+key+">"
        if rule_name in grammar:
            grammar[rule_name] += rules[key]
            grammar[rule_name] = list(set(grammar[rule_name]))
    
    file_path = "../grammar/req-line.json"
    save_json(grammar,file_path)


    # pass
def req_header_grammar_gen():
    # 想要保留req-line中正确的集合
    # <req-line> = {GET / HTTP/1.1}

    file_path = "../grammar/base/req-header.json"
    grammar = read_json(file_path)

    file_path = "../rfc/common_header.json"
    # rules = {"header-name":[header-value,]}
    rules = read_json(file_path)
    new_rules = {}
    new_rules["header"] = ["<"+key+">" for key in rules]
    for key in rules:
        # "Header": ["value",]
        # <Header>:<Header-name><colon><sp><Header-value>
        # <Header-name>: "Header"
        # <Header-value>: ["value",]
        new_rules["<{}>".format(key)] = ["<{}-name><colon><sp><{}-value>".format(key,key)]
        new_rules["<{}-name>".format(key)] = ["{}".format(key)]
        new_rules["<{}-value>".format(key)]= rules[key]
    for key in new_rules:
        if key in grammar:
            grammar[key] = list(set(grammar[key] + new_rules[key]))
        else:
            grammar[key] = new_rules[key]
    file_path = "../grammar/common-header.json"
    save_json(grammar,file_path)       







if __name__ == "__main__":

    # 由获取的报文元素信息
    # 和配置文件直接构建语法文件

    # 语法文件基本的构成
    # <a> -> ['b']
    # <start> 作为起始符,作为语法推导的开始
    # <[^<>]> 作为规则， 规则可以推导出值，可以有多个值，但一次推导只能选择一个
    # <[a-z-]> -> ['token1','token2'] ，值之间是或的关系
    # token1 可以为具体的值，数字，字符串，只要不是以<[^<>]>即可，需要避免使用<>
    # token1 可以为规则 <rule1>
    # token1 可以为两者的组合，token1 = "hello<rule1>"
    # 语法需要满足上下文无关性，且需要能够完整结束，
    req_header_grammar_gen()
    # pass