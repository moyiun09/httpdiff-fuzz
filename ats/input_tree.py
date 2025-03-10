#! /bin/bash/env python3
# -*- coding:UTF-8 -*-

from ats.input_tree_node import Node
import sys
from util.helper_functions import _parse_url, random_choose_with_weights
import random
from collections import deque
import re
import copy

class InputTree:

    def __init__(self, grammar, seed, url, verbose):
        """ Constructs a request object.
            
        Args:
          grammar: input grammar for describing the structure
          seed: a value based on which random number is
            generated. It is used for reproducability.

          url: address of the target endpoint
          verbose: a parameter to decide whether messages
            should be displayed.

        Returns:
          the constructed object
        """
        self.nonterminal_node_list = {}
        Node.symbol_counts = {}
        self.root = Node('<start>')
        self.grammar = grammar
        self.seed = seed
        random.seed(seed)
        self.url = url
        self.verbose = verbose
        self.host_header = None
        # protocol http| https

    def build_tree(self, start_node):
        self.nonterminal_node_list[start_node.id] = start_node

        node_queue = deque([start_node])
        while node_queue:
            current_node = node_queue.pop()

            possible_expansions = self.grammar[current_node.symbol]
            chosen_expansion = random_choose_with_weights(possible_expansions)

            for symbol in re.split(Node.RE_NONTERMINAL, chosen_expansion):
                if len(symbol) > 0:
                    new_node = Node(symbol)

                    current_node.children.append(new_node)

                    if not new_node.is_terminal:
                        node_queue.appendleft(new_node)
                        self.nonterminal_node_list[new_node.id] = new_node

        return start_node


    def build_trees(self, root_node):
        current_node = root_node
        grammar_que = deque([root_node])
        tree_queue = deque([{"root_node":root_node,"grammar_que":grammar_que}])
        tree_lst = []
        while tree_queue:
            current_tree = tree_queue.pop()
            grammar_que = current_tree["grammar_que"]
            current_node = grammar_que.pop()
            current_node_id = current_node.id
            current_node_symbol = current_node.symbol
            possible_expansions = self.grammar[current_node_symbol]
            for chosen_expansion in possible_expansions:
                tmp_tree = copy.deepcopy(current_tree)
                tmp_root_node = tmp_tree["root_node"]
                tmp_grammar_que = tmp_tree["grammar_que"]
                current_node = self.find_node_by_id(tmp_root_node,current_node_id)
                
                for symbol in re.split(Node.RE_NONTERMINAL, chosen_expansion):
                    if len(symbol) > 0:
                        new_node = Node(symbol)
                        current_node.children.append(new_node)

                        if not new_node.is_terminal:
                            tmp_grammar_que.appendleft(new_node)
                            self.nonterminal_node_list[new_node.id] = new_node
                # print(tmp_grammar_que)
                if tmp_grammar_que:
                    tree_queue.appendleft(tmp_tree)
                else:
                    tree_lst.append(tmp_root_node)
        return tree_lst
    
    def find_node_by_id(self,root_node,node_id):
        # 不递归了，用队列写吧     
        if root_node is None:
            return
        else:
            node_lst = [root_node]
            while len(node_lst) > 0:
                node = node_lst.pop()
                if node.id == node_id:
                    return node
                else:
                    if len(node.children) > 0:
                        for item in node.children:
                            if not item.is_terminal:
                                node_lst.append(item)
    def find_nodes_by_symbol(self,root_node,symbol):
         # 不递归了，用队列写吧
        result = []     
        if root_node is None:
            return
        else:
            node_lst = [root_node]
            while len(node_lst) > 0:
                node = node_lst.pop()
                if node.symbol == symbol:
                    result.append(node)
                else:
                    if len(node.children) > 0:
                        for item in node.children:
                            if not item.is_terminal:
                                node_lst.append(item)
        return result

    def remove_subtree_from_nodelist(self, start_node):
        """ This function updates the node_list dictionary
            when a node (and as a result its children) are removed.
        """
        if not start_node.is_terminal:
            self.nonterminal_node_list.pop(start_node.id)
            for child in start_node.children:
                self.remove_subtree_from_nodelist(child)

    # http1
    # http2
    def tree_to_request(self, partial=False):
        """ This function converts the request 
            object into bytes. 
        """
        self.request = b""
        self.expand_node(self.root)
        if partial:#request in its most basic form -- with placeholder values.
            return self.request

        self.host, self.port, self.authority, self.uri = _parse_url(self.url)
        if self.host_header is None:
            self.host_header = self.authority

        return self.request.replace(b'_URI_', self.uri.encode('utf-8')).replace(b'_HOST_', self.host_header.encode('utf-8')).replace(b'_REQUEST_ID_', str(self.seed).encode('utf-8'))

    def expand_node(self, node):
        if node.is_terminal:
            self.request += node.symbol.encode('utf-8')
        else:
            for child in node.children:
                self.expand_node(child)
    
    def tree_to_str(self,node):
        self.request = b""
        self.expand_node(node)
        return self.request
