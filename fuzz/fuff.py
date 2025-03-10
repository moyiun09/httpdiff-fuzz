
import random
import copy
from util.helper_functions import _print_exception, random_choose_with_weights
from ats.input_tree_node import Node
from urllib.parse import quote
# 语义变换
# param ats
# param seed
# return ats(改)
# 只做一次
class Fuff:
    fuff_types = {0, # num fuff
                     1,# string fuff
                     2}# header fuff 

    
    def __init__(self, fuzzer, _input, seed=0, reproduce_mode = False):
        self.fuzzer = fuzzer
        self.input = _input
        random.seed(seed)
        self.reproduce_mode = reproduce_mode
        self.mutation_messages = []
        self.headers_node = self.get_headers_node()

    def fuff_input(self):
        try:
            if(not self.fuzzer.fuff_enable):
                print("not fuff")
                return 
            node_to_fuff_pool = [node for node in self.input.nonterminal_node_list.values() if node.symbol in self.fuzzer.symbol_fuff_types]
            if node_to_fuff_pool == []:
                print("no node can fuff")
                return
            node_to_fuff = random.choice(node_to_fuff_pool)
            fuffs = []

            sp_fuffs = {
                "<uri>":['absolute_uri','uri_path_tras',],
                "<authority-value>":['absolute_uri','uri_path_tras',],
                "<Range-value>":['range_zero_split'],
            }
            common_fuffs = [
                'char_url_encode',
                'str_url_encode'
            ]
            num_done_fuff = 0
            num_fuff = 1
  
            if self.reproduce_mode:
                self.input_initial_state = copy.deepcopy(self.input)
                self.fuffs = []

            while num_done_fuff < num_fuff:
                node_to_fuff_pool = [node for node in self.input.nonterminal_node_list.values() if node.symbol in self.fuzzer.symbol_fuff_types]
                if node_to_fuff_pool == []:
                    break
                node_to_fuff = random.choice(node_to_fuff_pool)
    
                if self.fuzzer.symbol_fuff_types[node_to_fuff.symbol] == 1: #string fuff
                    fuffs = [
                        'char_to_upper',
                        'char_to_lower',
                        'str_to_upper',
                        'str_to_lower'
                    ]
                if self.fuzzer.symbol_fuff_types[node_to_fuff.symbol] == 0: # int fuff
                    fuffs = [
                        'num_to_float',
                        'num_to_hex',
                    ]
                if self.fuzzer.symbol_fuff_types[node_to_fuff.symbol] == 2: # header fuff
                    fuffs = [
                        'first_line_header',
                        'header_double_value',
                        'header_fold',
                        'header_name_fix',
                    ]
                if node_to_fuff.symbol in fuffs:
                    fuffs.append(item for item in sp_fuffs[node_to_fuff.symbol])

                fuffs = fuffs + common_fuffs
                chosen_fuff = random_choose_with_weights(fuffs)
                if self.reproduce_mode:
                    self.mutations.append([chosen_fuff, node_to_fuff, random.getstate()])
                if self.fuzzer.verbose:
                    print(node_to_fuff.symbol,len(node_to_fuff.children))
               
                self.__getattribute__(chosen_fuff)(node_to_fuff, self.fuzzer.verbose)
                
            
                num_done_fuff += 1

        except Exception as exception: 
            _print_exception() 
            raise(exception)


    def char_to_upper(self,node,verbose=False):
        s = node.children[0].symbol
        if s:
            pos = random.randint(0, len(s) - 1)
            c = s[pos]
            if(is_lower_char(c)):
                c = c.upper()
                node.children[0].symbol = s[:pos] +c + s[pos+1:]
                if verbose:
                    print("Upper character {} at pos {} with {}.".format(repr(s), pos, node.symbol))
                else:
                    self.mutation_messages.append("Removing character {} at pos {} with {}.".format(repr(s), pos, node.symbol)) 

    def char_to_lower(self,node,verbose=False):
        s = node.children[0].symbol
        if s:
            pos = random.randint(0, len(s) - 1)
            c = s[pos]
            if(is_upper_char(c)):
                c = c.lower()
                node.children[0].symbol = s[:pos] +c + s[pos+1:]
                if verbose:
                    print("Lower character {} at pos {} with {}.".format(repr(s), pos, node.symbol))
                else:
                    self.mutation_messages.append("Lower character {} at pos {} with {}.".format(repr(s), pos, node.symbol)) 
           
        pass

    def str_to_upper(self,node,verbose=False):
        s = node.children[0].symbol
        pos = '*'
        if s:
            tmp_array = [c.upper() if is_lower_char(c) else c for c in s]
            node.children[0].symbol = ''.join(tmp_array)
            if verbose:
                print("Upper character {} at pos {} of {}.".format(repr(s), pos, node.symbol))
            else:
                self.mutation_messages.append("Upper character {} at pos {} of {}.".format(repr(s), pos, node.symbol)) 
        pass

    def str_to_lower(self,node,verbose=False):
        s = node.children[0].symbol
        pos = '*'
        if s:
            tmp_array = [c.lower() if is_upper_char(c) else c for c in s]
            node.children[0].symbol = ''.join(tmp_array)
            if verbose:
                print("Lower character {} at pos {} of {}.".format(repr(s), pos, node.symbol))
            else:
                self.mutation_messages.append("Lower character {} at pos {} of {}.".format(repr(s), pos, node.symbol)) 
    def num_to_float(self,node,verbose=False):
        s = node.children[0].symbol
        num = str_to_num(s)
        pos = '*'
        if num:
            node.children[0].symbol = str(float(num))
            if verbose:
                print("Float number {} at pos {} with {}.".format(repr(s), pos, node.symbol))
            else:
                self.mutation_messages.append("Float number {} at pos {} with {}.".format(repr(s), pos, node.symbol)) 
        

    def num_to_hex(self,node,verbose=False):
        s = node.children[0].symbol
        num = str_to_num(s)
        pos = '*'
        if num:
            node.children[0].symbol = hex(num)
            if verbose:
                print("Hex number {} at pos {} with {}.".format(repr(s), pos, node.symbol))
            else:
                self.mutation_messages.append("Hex number {} at pos {} with {}.".format(repr(s), pos, node.symbol)) 
  

    def first_line_header(self,node,verbose=False):
        # <headers>-><header-1><header-2>,
        # self.headers_node.children = [node]
        pos = 1
        if self.headers_node:
            headers_node_childrens =  self.headers_node.children
            for i in range(len(headers_node_childrens)):
                if headers_node_childrens[i].id == node.id:
                    pos = i
                    print('find node')
            self.headers_node.children = [node]+headers_node_childrens[:pos]+headers_node_childrens[pos+1:]
            if verbose:
                print("Move Header {} at pos {} of {}.".format(node.id, pos, self.headers_node.symbol))
            else:
                self.mutation_messages.append("Move Header {} at pos {} of {}.".format(node.id, pos, self.headers_node.symbol))

        pass
    def header_double_value(self,node,verbose=False):
        # <Content-Length> -> <Content-Length-name><colon><space><Content-Length-value><newline>
        split_chars = [',',";"]
        split_char = random.choice(split_chars)
        pos = "*"
        value_node = node.children[-2]
        if('-value>' in value_node.symbol):
            s = value_node.children[0].symbol
            value_node.children[0].symbol = s + split_char + s
            if verbose:
                print("Double Value {} at pos {} of {}.".format(value_node.id, pos, node.symbol))
            else:
                self.mutation_messages.append("Double Value {} at pos {} of {}.".format(value_node.id, pos, node.symbol))
        pass


    def header_fold(self,node,verbose=False):
        pos = "*"
        value_node = node.children[-2]
        if('-value>' in value_node.symbol):
            s = value_node.children[0].symbol
            pos = random.randint(0, len(s) - 1)
            value_node.children[0].symbol = s[:pos]+"\r\n" +' '+s[pos:]
            if verbose:
                print("Fold Header Value {} at pos {} of {}.".format(s, pos, node.symbol))
            else:
                self.mutation_messages.append("Fold Header Value {} at pos {} of {}.".format(s, pos, node.symbol))

    def header_name_fix(self,node,verbose=False):
        pos = "*"
        header_name_node = self.get_header_name_node(node)
        if header_name_node:
            s =  header_name_node.children[0].symbol
            header_name_node.children[0].symbol = s.replace("-","_",1)
            if verbose:
                print("Fix Header Name  {} at pos {} of {}.".format(s, pos, node.symbol))
            else:
                self.mutation_messages.append("Fold Header {} at pos {} of {}.".format(s, pos, node.symbol))
        pass

    def absolute_uri(self,node,verbose=False):
        # <uri> -> /
        # <authority-value> -> /
        pos = "*"
    
        s =  node.children[0].symbol
        if '/' == s[0]:
            # protocol 
            node.children[0].symbol = 'http://' + self.input.host_header + s
            if verbose:
                print("Abosulte URI  {} at pos {} of {}.".format(s, pos, node.symbol))
            else:
                self.mutation_messages.append("Abosulte URI {} at pos {} of {}.".format(s, pos, node.symbol))
        pass

    def uri_path_tras(self,node,verbose=False):
                # <authority-value> -> /
        pos = "*"
    
        s =  node.children[0].symbol
        # /../[\s]{1,5}+/
        num = random.randint(1,5)
        
        tmp_uri = ''
        for i in range(num):
            tmp_pos = random.randint(0, len(self.fuzzer.char_pool) - 1)
            tmp_uri +='/../'+self.fuzzer.char_pool[tmp_pos]
        # '/' 
        if '/' == s[0]:
            tmp_uri = tmp_uri + s
        elif 'http' == s[:4]:
            # https://host/ss
            tmp_uri_parts = s.split('/',3)
            tmp_uri = '/'.join(tmp_uri_parts[:3])+tmp_uri+'/'+tmp_uri_parts[3]
        else:
            tmp_uri = s
            # protocol 
        node.children[0].symbol = tmp_uri
        if verbose:
            print("URI PATH TRAS  {} at pos {} of {}.".format(s, pos, node.symbol))
        else:
            self.mutation_messages.append("URI PATH TRAS {} at pos {} of {}.".format(s, pos, node.symbol))



    def range_zero_split(self,node,verbose=False):
        # bytes=0-
        # bytes=0-1000 --> bytes=0-0,0-10000
        s = node.children[0].symbol
        range_parts = s.split('-',1)
        pos = len(range_parts[0])
        if 2 == len(range_parts):
            if '' == range_parts[1]:
                node.children[0].symbol = range_parts[0]+'-0,0-'+"*"

            else:
                node.children[0].symbol = range_parts[0]+'-0,0-'+range_parts[1]
            
            if verbose:
                print("Range Right *  {} at pos {} of {}.".format(s, pos, node.symbol))
            else:
                self.mutation_messages.append("Range Right * {} at pos {} of {}.".format(s, pos, node.symbol))
        pass


    def char_url_encode(self,node,verbose=False):
        s = node.children[0].symbol
        if s:
            pos = random.randint(0, len(s) - 1)
            c = s[pos]
            c = quote(c)
            node.children[0].symbol = s[:pos] +c + s[pos+1:]
            if verbose:
                print("URLEncode character {} at pos {} of {}.".format(repr(s[pos]), pos, node.symbol))
            else:
                self.mutation_messages.append("URLEncode character {} at pos {} of {}.".format(repr(s[pos]), pos, node.symbol)) 
        pass

    def str_url_encode(self,node,verbose=False):
        s = node.children[0].symbol
        pos = '*'
        if s:
            node.children[0].symbol = quote(s)
            if verbose:
                print("URLEncode character {} at pos {} of {}.".format(repr(s), pos, node.symbol))
            else:
                self.mutation_messages.append("URLEncode character {} at pos {} of {}.".format(repr(s), pos, node.symbol)) 
        pass

    def get_headers_node(self):
        try:
            headers_node = self.input.nonterminal_node_list["<headers>-1"]
            return headers_node
        except Exception as e:
            _print_exception(e)
            print('grammar error')
    def get_header_name_node(self,header_node):
        try:
            # <header> -> <header-name><colon><space><header-value><newline>
            header_name_node = header_node.children[0]
            if '-name>' in header_name_node.symbol:
                return header_name_node
            return None
        except Exception as e:
            _print_exception(e)
            print('can not find header_name_node')
    def get_header_value_node(self,header_node):
        try:
            # <header> -> <header-name><colon><space><header-value><newline>
            header_value_node = header_node.children[-2]
            if '-value>' in header_value_node.symbol:
                return header_value_node
            return None
        except Exception as e:
            _print_exception(e)
            print('can not find header_value_node')




def is_lower_char(c):
    min_char_value = ord('a')
    max_char_value = ord('z')
    if ord(c) >= min_char_value and ord(c) <= max_char_value:
        return True
    
    return False

def is_upper_char(c):
    min_char_value = ord('A')
    max_char_value = ord('Z')
    if ord(c) >= min_char_value and ord(c) <= max_char_value:
        return True
    
    return False


def str_to_num(s):
    try:
        num = int(s)
        return num
    except Exception as e:
        _print_exception(e)
        return None
