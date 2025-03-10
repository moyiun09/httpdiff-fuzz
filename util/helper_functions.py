import sys
import linecache
import configargparse
import random
import socket
import re

def _parse_url(url):
    """ This function extracts certain 
        components from a given URL.
    """
    authority = url.split('/')[2]
    uri = '/'.join(url.split('/')[3:])

    if ':' not in authority:
        port = 80
        host = authority
    else:
        host, port = authority.split(':')

    return host, port, authority, uri

def _print_exception(extra_details=[]):
    """ This function prints exception details
        including the line number where the exception
        is raised, which is helpful in most cases.
    """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}, {}'.format(filename, lineno, line.strip(), exc_obj, extra_details))

def _parse_args(): 
    """ This function is for parsing the command
        line arguments fed into the script.
    """
    parser = configargparse.ArgParser(description='T-Reqs: Grammar-based HTTP Fuzzer')

    parser.add('-c', dest="config", required=True, help='config file path')
    parser.add('-i', action="store_true", dest="individual_mode", help="Turns the individual mode on where the fuzzer is run only for specified seeds.")
    parser.add('-n', action="store_true", dest="no_sending", help="Turns the no-sending mode on where the fuzzer only generates the inputs without sending them to the targets.")
    parser.add('-s', dest="seed", help="Only needed for individual mode. Seed parameter for random number generator.")
    parser.add('-v', action="store_true", dest="verbose", help="Only needed for individual mode. Adds verbosity.")
    parser.add('-o', dest="outfilename", help = "Only needed for individual mode. File to write output.")
    parser.add('-f', dest="seedfile", help = "Only needed for individual mode. Input file containing seeds.")

    args = parser.parse_args()

    return args

def random_choose_with_weights(possible_expansions):
    probabilities = [0]*len(possible_expansions)
    for index, expansion in enumerate(possible_expansions):
        if "prob=" in expansion:
            probability = expansion[expansion.find("prob=")+5:expansion.find(")")]
            probabilities[index] = float(probability)

    probabilities = [(1-sum(probabilities))/probabilities.count(0) if elem == 0 else elem for elem in probabilities]

    chosen_expansion = random.choices(possible_expansions, weights=probabilities)[0]
    # '(<headers-frame-1><data-frame-1>, opts(prob=0.9))'
    # for cases where symbol looks like above, trimming is needed
    if chosen_expansion.startswith('('):
        chosen_expansion = chosen_expansion.split(',')[0][1:]

    return chosen_expansion


def print_singel_byte_result(result):
    # result = {"status":["0x00","0x01",....]}
    # tmp_list = result["200"]
    # tmp_list.sort(key=lambda x:int(x,16))
    # pass
    for key in result:
        print("=="*3+str(key))
        result[key].sort(key=lambda x:int(x,16))
        # print(len(result[key]))
        # print(result[key])
        # 优化一下输出
        tmp_list = result[key]
        min_item = int(tmp_list[0],16)
        max_item = int(tmp_list[-1],16)
        if len(tmp_list) < 2 : 
            print(tmp_list[0])
        else:
            for i in range(len(tmp_list)-1):
                # 1,2,3,5
                # min --> 1 max -->3
                if( int(tmp_list[i+1],16) == int(tmp_list[i],16) +1):
                    continue
                # min --> 1 max --> 3 min --> 5
                # 1,3
                if(min_item != int(tmp_list[i],16)):
                    print(hex(min_item)+'-'+tmp_list[i])
                else:
                    print(tmp_list[i])
                min_item = int(tmp_list[i+1],16)
            if(min_item != max_item):
                 print(hex(min_item)+'-'+tmp_list[-1])
            else:
                 print(tmp_list[-1])

        print("=="*3)


def print_len_result(result):
    # result = {"(key)":[min,max,[0]]}
    # tmp_list = result["200"]
    # tmp_list.sort(key=lambda x:int(x,16))
    # pass
    for key in result:
        print("=="*3+str(key))
        
        min = result[key][0]
        max = result[key][1]
        empty = False
        flag = True
        if len(result[key]) == 3 :
            if max == 0: 
                print(hex(0))
            else: 
                print(hex(0),(hex(min),hex(max)))
        else:
            print((hex(min),hex(max)))
            
        print("=="*3)


def print_dict(result):
    for key in result:
        print("="*4,key)
        print(result[key])
        print("="*10)

def send(url,req):
    try: 
        host, port, authority, uri = _parse_url(url)
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((host, int(port)))
        _socket.settimeout(2)
        _socket.send(req)
        response = b''
        while True:
            data = _socket.recv(1024)
            if not data:
                break
            else:
                response += data
    except BlockingIOError as e:
        # server socket shutdown
        _print_exception(e)
    except Exception as e:
        _print_exception(e)

    finally:
        _socket.shutdown(socket.SHUT_RDWR)
        _socket.close()
        return response
def get_status(res):
    if res is  None:
        return ('time out',None)
    pattern = r"HTTP\/\d\.\d \d{3}"
    # 若res格式有问题，或前空格乱码字符?
    try:
        res = str(res,encoding="utf-8",errors="ignore")
    except Exception as e:
        #print(res)
        print(e)
    matchs = re.match(pattern,res)
    # print(matchs)
    if matchs is not None:
        res_line = matchs.group()
        proto = res_line.split(" ")[0]
        code =  res_line.split(" ")[1]
    else:
        # HTTP/0.9
        # None
        proto = 'HTTP/0.9'
        code =  None
    return (code,proto)


def getproto(req):
    return str(req,encoding="utf-8").split("\r\n")[0].split(' ')[2]

if __name__ == "__main__":
    req = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    url = "http://localhost:8000/"
    res = send(url,req)
    # print(status)
    print(res)

