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

### Data structure choice

There are two possible data structures one can use. A (heap), or
a dequeue kept sorted. A heap allows insertion and deletion in `O(log n)`
while for a sorted dequeue, insertion/deletion at either end is `O(1)` while
insertion or deletion in the middle may be `O(n)`. Note that we assume
a `decrease key` operation to be same as `remove + insert`.

With this in mind, the data structure with most performance is dependent on
the expected data. I have implemented both (see `deq-insert` branch for the
dequeue insertion algorithm and `deq-sort`, which is a slower (but simpler)
dequeue based implementation relying on sorting). To check which is better,
I profiled all the three

    $ head -1 data-gen/new-tweets.txt | cut -d, -f1
    {"created_at":"Sat Apr 02 20:20:41 +0000 2016"
    $ tail -1 data-gen/new-tweets.txt | cut -d, -f1
    {"created_at":"Sat Apr 02 20:53:11 +0000 2016"
    $ wc -l data-gen/new-tweets.txt 
    101436 data-gen/new-tweets.txt
    $ du -ksh data-gen/new-tweets.txt
    278M    data-gen/new-tweets.txt
    $ wc -l data-gen/new-tweets.1.txt 
    40216 data-gen/new-tweets.1.txt
    $ du -ksh data-gen/new-tweets.1.txt
    112M    data-gen/new-tweets.1.txt
    
#### dequeue-insert

    $ time make runit W=./data-gen/new-tweets.txt > out
    99.78s user 0.79s system 94% cpu 1:46.71 total
    100.48s user 0.77s system 98% cpu 1:43.27 total

    $ time make runit W=./data-gen/new-tweets.1.txt > out
    39.25s user 0.36s system 98% cpu 40.381 total
    39.19s user 0.35s system 97% cpu 40.455 total

#### dequeue-sort

    $ time make runit W=./data-gen/new-tweets.txt > out
    108.94s user 0.79s system 98% cpu 1:51.76 total
    108.71s user 0.86s system 98% cpu 1:51.60 total

    $ time make runit W=./data-gen/new-tweets.1.txt > out
    43.15s user 0.37s system 97% cpu 44.851 total
    42.77s user 0.33s system 98% cpu 43.896 total

#### heap

    $ time make runit W=./data-gen/new-tweets.txt > out
    91.44s user 0.80s system 98% cpu 1:33.98 total
    91.09s user 0.78s system 98% cpu 1:33.61 total

    $ time make runit W=./data-gen/new-tweets.1.txt > out
    35.83s user 0.35s system 98% cpu 36.904 total
    35.41s user 0.31s system 98% cpu 36.407 total

My results seem to indicate that a heap based implementation is has the best
performance. Hence I have used the heap based implementation in my submission
(also in the branch `heap`).

## Notes on test generation

See `gentest` target in Makefile.
