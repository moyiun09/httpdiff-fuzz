
import random
import re
import copy
import socket
import threading
from multiprocessing import Process, Queue
import time

from fuzz.mutator import Mutator
from fuzz.fuff import Fuff
from ats.input_tree_node import Node
from ats.input_tree import InputTree
from util.helper_functions import _print_exception, _parse_args,send
from util.file import read_json,save_json

class Fuzzer:

    def __init__(self, verbose, seed, outfilename, seedfile, no_sending):
        file_path = "./config"
        self.read_config(file_path)

        self.verbose = verbose
        self.seed = self.expand_seed(seed)
        self.lock = threading.Lock()
        self.outfilename = outfilename
        self.seedfile = seedfile
        self.no_sending = no_sending

    def read_config(self, configfile):
        config_content = open(configfile).read().replace('config.', 'self.')
        exec(config_content)
        if False in [item in self.__dict__ for item in ["target_urls", "target_host_headers", "min_num_mutations", "max_num_mutations","symbol_mutation_types"]]:
            print("Please make sure that the configuration is complete.")
            exit()

        self.target_hosts = {self.target_urls[i]:self.target_host_headers[i] for i in range(len(self.target_urls))}
 
    def expand_seed(self, seed_string):
        if seed_string == None:
            return None
        expanded_seeds = []
        for seed in seed_string.split(','):
            if '-' in seed:
                start, end = map(int, seed.split('-'))
                expanded_seeds.extend(range(start, end + 1))
            elif seed.isnumeric():
                expanded_seeds.append(int(seed))
        return expanded_seeds

    def send_fuzzy_data(self,url, inputdata, list_responses):
        response = send(url,inputdata)
        with self.lock:
            list_responses.append(response)
        

    def get_responses(self, seed, request):
        threads = []
        list_responses = []
        for target_url in self.target_urls:
            request.seed = seed
            request.url = target_url
            request.host_header = self.target_hosts[target_url]

            request_copy = copy.deepcopy(request)
            thread = threading.Thread(target=self.send_fuzzy_data, args=(request_copy, list_responses))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(5)

        return list_responses
    def blackbox_fuzz_individual(self, filename=None, seeds=None):
        if seeds == None:
            with open(filename, 'r') as _file:
                seeds = [int(line.strip()) for line in _file.readlines()]
        responses_list = []
        responses_list = self.run(seeds,None)
        if self.outfilename is None:
            print("\n".join(responses_list))
            print("\n")
        else:
            save_json(responses_list,self.outfilename)

    def run(self, seeds, _queue):
        responses_list = []
        for seed in seeds:
            base_input = InputTree(self.grammar, seed, "http://hostname/uri", False)
            base_input.build_tree(base_input.root)


            # fuff()
            mutator = Mutator(self, base_input, seed)
            mutator.mutate_input()
            if not self.no_sending:
                responses = self.get_responses(seed, base_input)
            else:
                responses = []
            tmp_result = {"seed":seed,"req":str(base_input.tree_to_request(),encoding="utf-8"),"resList":[item for item in responses],"fuff":','.join(fuff.mutation_messages),"mutate":",".join(mutator.mutation_messages)}
            responses_list.append(tmp_result)

        _queue.put(responses_list)

