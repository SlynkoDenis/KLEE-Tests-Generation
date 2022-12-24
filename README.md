# KLEE-based tests generation for C libraries

Draft of a tool for automatic unit tests generation for C source code. The tool uses `KLEE` execution engine to generate test vectors for each single input function, which must correspond some constraints (see below).

# Current limitations

* Tool can only process simple functions with primitive arguments types (no pointers, arrays or structs)
* Most source files are discarded due to absent headers
* Low coverage as long as no input data limitations are applied

# Run instructions

## Local run

* Install `KLEE` and all its dependencies, including `clang-11`
* Instal python packages: `python3 -m pip install --user -r requirements.txt`
* Specify paths to `KLEE` binary applications directory and `include` directory in `config.yaml`
* Run with `python3 main.py`

## Run in docker

* In project's root directory: `docker build -t klee-test-gen .`
* `docker run klee-test-gen`

After run one can see results in `vectors` directory of container. To copy them to host, do the following:
* Obtain container ID `CID` via `docker ps -a`
* `docker cp ${CID}:/klee-test-gen/vectors .`
