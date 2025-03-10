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

if __name__ == "__main__":
   count = 10000
   for i in range(0,72):
    print(f"{i} init"+"-"*10)
    seed = f"{i*count+1}-{(i+1)*count}"
    file_path = f"data/baseAb/out{i}.json"
    fuzzer = Fuzzer(verbose=False,seed=seed,outfilename=file_path,seedfile=None,no_sending=False)
#    fuzzer.read_grammar(file_path)
    start = time.time()
    fuzzer.blackbox_fuzz_individual(filename=None,seeds=fuzzer.seed)
    print(time.time() - start)

   

