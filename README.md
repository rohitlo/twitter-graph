# The coding challenge.

The main source file is `src/average_degree.py` and its tests are in
`src/test_average_degree.py`.

## Language requirement

The language used is `python`. It requires at least version `3.5` for it
to run.

## Additional libraries required.

This solution makes use of [heapdict](https://pypi.python.org/pypi/HeapDict)
which can be installed by

    pip3 install heapdict

If you would like to execute unit tests, it can be accomplished by

    python3 src/test_average_degree.py -v

It may be useful to add coverage information to unit tests (99% statement, 98%
branch). It may be accomplished with 

    pip3 install coverage

You can install all the dependencies with

    make prereq

To run unittests with coverage, execute

    make unittest

The code quality may be checked with linters with

    make lint

To run the code on data-gen/tweets.txt, use

    make run

or alternatively

    make run W=data-gen/tweets.txt


## Notes on implementation

Noticing that a large amount of tweets (95%) did not contain at least two hash
tags in `data-gen/tweets.txt`, I built an initial data pipeline using ruby
(`bin/cleanit.rb`, `bin/online-graph.rb`) and python for comparison
(`bin/cleanit.py`, `bin/online-graph.py`) where `bin/cleanit.*`
removed the invalid records and piped out the creation time and nodes
as records. I hoped that this would help when there are multiple CPUs.
The problem with that approach was that even records that did not contain
more than two records needed to trigger eviction of older records. Further,
on profiling, I found that the code can easily process data at a much faster
rate than what the twitter API can provide even if no cleanup is done before.

Hence my submission `src/average_degree.py` is a single stage application. It
expects tweets in the `stdin` and prints out the rolling average to `stdout`.
This is hooked up correctly in `run.sh` to process `./tweet_input/tweets.txt`
and output in `./tweet_output/output.txt`.

