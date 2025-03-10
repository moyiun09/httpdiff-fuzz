#! /bin/bash/env python3
# -*- coding:UTF-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import time
import random


if __name__=="__main__":
    # 写一个简单的爬虫
    # index_url = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
    # res = requests.get(index_url)
    # # index.html --> (local) index.html
    file_path = '../mdn/index.html'
    # with open(file_path,"w") as f:
    #     f.write(res.text)
    #     f.close()
    with open(file_path,"r") as f:
        data = f.read()
        f.close()
    soup = BeautifulSoup(data, "html.parser")
    res = soup.select("#sidebar-quicklinks > nav > div > div.sidebar-body > ol > li:nth-child(18) > details > ol > li")
    # print(res)
    # print(headers[0])
    # print(res[0].find('code').text)
    # print(type(res[0]))
    headers = []
    for item in res:
        headers.append(item.find('code').text)
    # print(headers)
    # each header --> url --> header example
    # header_url = "https://developer.mozilla.org/en-US/docs/Web/HTTP/{}"
        
    header_url = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/{header}"
    # print(header_url)
    # crawl header page
    #content > article > section:nth-child(3) > div > div > pre
    #content > article > section:nth-child(4) > div > div.code-example > pre
    #content > article > section:nth-child(3)
    # example  css select --> #content > article > section[aria-labelledby="syntax"] > .section-content > .code-example > pre
    # example  css select --> #content > article > section[aria-labelledby="examples"] > .section-content > .code-example > pre
    # res = requests.get(header_url)
    # file_path = "../mdn/header.html"
    # with open(file_path,"w") as f:
    #     f.write(res.text)
    #     f.close()
    # with open(file_path,"r") as f:
    #     data = f.read()
    #     f.close()
    header_examples = []
    # print(headers[0:10])
    for header in headers:
        res = requests.get(header_url.format(header=header))
        # print(header)
        print("-"*3+header_url.format(header=header)+"-"*3)
        soup = BeautifulSoup(res.text, "html.parser")
        # soup = BeautifulSoup(res, "html.parser")
        try :
            examples = soup.select('#content > article > section[aria-labelledby="examples"] > .section-content > .code-example > pre')
        
            for item in examples:
                text = item.find('code').text
                print(str.encode(text))
                lines = text.split("\n")
                for line in lines:
                    # print(str.encode(line))
                    line = line.strip()
                    if(len(line) > 0):
                        if(line[0] == "\\"):
                            # comment
                            continue
                        if(re.match(r"^[A-Za-z-_]+: .*?",line)):
                            # extract header by re match
                            header_examples.append(line)

        except AttributeError:
            print("error _ log ")
        
        time.sleep(random.randint(3,5))
    file_path = "../mdn/header.txt"
    with open(file_path,"w") as f:
        f.write("\r\n".join(header_examples))
        f.close()
    # print(header_examples)





    


