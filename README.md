# The coding challenge.

The main source file is `src/average_degree.py` and its tests are in
`src/test_average_degree.py`.

## Language requirement

The language used is `Python`. It requires at least version `3.5` for it
to run.


## Basic invocation and tests

The `run` target executes `./run.sh` after installing prerequisite libraries in
the user home.

    make run

or to allow installation of libraries in the system path

    make run O=

To execute the _insight_ test suite, (installing prerequisites in user home) use

    make test

or

    make test O=

which installs the required libraries in the system path.

## Additional libraries required.

This solution makes use of [heapdict](https://pypi.python.org/pypi/HeapDict)
which can be installed by (takes O= variable)

    make i-heapdict

You can install all the dependencies (takes O= variable)

    make prereq

### Unit tests

If you would like to execute unit tests without coverage, it can be done by

    make unittests

If you would like coverage information, it requires coverage to be installed (included in `prereq`).

    make i-coverage

To collect branch coverage, the `unittest-branch`  target is used, followed by
extracting coverage. The project has 98% branch coverage.

    make unittest-branch
    make coverage

To collect statement coverage, the `unittest-statement` target is used, followed
by extracting coverage. The project has 99% statement coverage.

    make unittest-statement
    make coverage

### Linters

The project uses two linters: `flake8` and `pylint` (included in `prereq`) They can also
be installed separately (takes O= variable)


    make i-flake8 i-pylint

The lint can be checked for both tools at once using the `lint` target

    make lint

or 

    make lint-flake8 lint-pylint

They can also be separately invoked

    make lint-flake8
    make lint-pylint

### Executing the program.

To run the code on `data-gen/tweets.txt`, use

    make runit

or alternatively

    make runit W=data-gen/tweets.txt


## Additional help

The set of targets exposed by `Makefile` can be obtained by

    make

The detailed help is provided by the `help` target

    make help

## Notes on implementation

Noticing that a large amount of tweets (95%) did not contain at least two hash
tags in `data-gen/tweets.txt`, I built an initial data pipeline using Ruby
(`bin/cleanit.rb`, `bin/online-graph.rb`) and Python for comparison
(`bin/cleanit.py`, `bin/online-graph.py`) where `bin/cleanit.*`
removed the invalid records and piped out the creation time and nodes
as records. I hoped that this would help when there are multiple CPUs. I
experimented with binary data transfer through pipes (see `rb-binary`
target of Makefile). However, on profiling, the binary transfer of time
and integer hashes of hashtags was slightly more costly (perhaps due to the
inefficient binary packing library in Ruby) than the ASCII transfer of creation
time and hashtags (see `rb-ascii` target in make file).

A problem with that approach was that even records that did not contain
more than two records needed to trigger eviction of older records. Further,
on profiling, I found that the code can easily process data at a much faster
rate than what the twitter API can provide, even if no cleanup is done before.

Hence my submission `src/average_degree.py` is a single stage application. It
expects tweets in the `stdin` and prints out the rolling average to `stdout`.
This is hooked up correctly in `run.sh` to process `./tweet_input/tweets.txt`
and output in `./tweet_output/output.txt`.

## Notes on test generation

See `gentest` target in Makefile.
