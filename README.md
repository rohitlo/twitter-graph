# Running the solution

The language used is `python`. It requires at least version `3.5` for it
to run.

## Additional libraries required.

This solution makes use of [heapdict](https://pypi.python.org/pypi/HeapDict)
which can be installed by

    pip3.5 install heapdict

If you would like to execute unit tests, it can be accomplished by

    python3 src/test_average_degree.py -v

To run it, use the `Makefile` as

    make unittest

A colorized version with coverage can be obtained if the library `green` is
installed.

    pip3.5 install green

And to run it:

    python3 -m green -r 

