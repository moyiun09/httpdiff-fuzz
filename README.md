## httpdiff-fuzz
httpdiff-fuzz, developed based on the prototype system t-reqs, is used to test the semantic inconsistency of the HTTP protocol.
### Overall system architecture
![System architecture diagram](./bg.png)

### Improved work:
1. Message construction method based on key headers
httpdiff-fuzz proposes the concept of key headers. In a specific environment, only test messages with some headers are meaningful. Determining these headers that can express semantics as key headers can reduce the space of test messages and retain semantic features.
The key header selection algorithm is implemented in the ./normal-test.py file. By observing the changes in the header semantics, whether the test results change, and then determining whether the header is a key header.

2. Mutation strategy based on field semantics
httpdiff-fuzz extends the mutation based on the syntax tree in t-reqs, expands the node definition to numeric type, character type, header type and special type, and provides a directional mutation method based on the node type.
The fuzz/fuff.py file implements the mutation methods corresponding to various nodes, based on the syntax tree mutation, and formats and processes the message fields according to specific requirements.

3. Extended message analysis angle
httpdiff-fuzz extends the message analysis angle, observing the messages of the entire communication process (fields of request messages and response messages), covering existing scenarios with semantic inconsistency problems (URI-based access control bypass, Double Hosts, HRS, CPDoS, traffic asymmetry problems)
The extended message difference analysis algorithm is implemented in the diff/diff_tmp.py file

### Run

#### Environment setup
python sets up the system running environment requirements
If the test object is in reverse proxy mode, the request message needs to be forwarded to echo_server.py
If the test object is in server mode, the php script needs to be configured to map ./index.php to the default interface of the server
The system does not support other working modes

#### Preliminary work (optional, syntax file configuration)
- The collected field information is already in rfc/*.json, which can be expanded by yourself
- Specify the test target in the config file
- ./normal-test.py Key header test, input the header information obtained by the test into - grammar/grammarGen.py to regenerate the grammar file, and replace the existing grammar in config with the generated grammar
- Adjust the declaration of node type in config file based on your own experience (not recommended)

#### Difference problem test (core)
- Specify the test target in config file
- ./fuzz-test.py specifies the size of random seeds, and builds test messages from 1-seeds for testing. You can specify the file to save the server results in the fuzz-test.py parameters.
- diff/diff_tmp.py analyzes the results of server tests and obtains the difference information between test results

#### Manual analysis of semantic inconsistency problems (to be improved)
From the difference information, it can be determined whether there is a problem with the behavior of server processing, but there is currently no good classification method to find specific semantic inconsistency problems from the difference information.
Locate the difference in specific fields, such as the difference in the processing of Content-Length or Transfer-Encoding headers to find possible request smuggling problems.
Further improvements will be made in the future.