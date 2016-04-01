all:
	@echo "The following commands are provided:"
	@echo "Execute the run.sh"
	@echo ">	make run"
	@echo "Execute the program on a given tweet file"
	@echo ">	make runit W=./data-gen/tweets.txt"
	@echo "Install all prerequisites"
	@echo ">	make prereq"
	@echo "Install all prerequisites on the user home"
	@echo ">	make prereq U=--user"
	@echo "Run lint on the source"
	@echo ">	make lint"
	@echo "Run unittests and extract coverage"
	@echo ">	make unittest"
	@echo "Run the insight test suite"
	@echo ">	make test"
	@echo "Generate a test for the insight test suite (see makefile for examples)"
	@echo "The T parameter uses Mon Mar 28 23:23:12 +0000 2016 as the base time"
	@echo ">	make gentest T=<time> H=<hashtags> N=<name>"
	@echo "e.g."
	@echo ">	make gentest T=0 H='A B C' N=test-eviction"
	@echo "Each gentest invocation corresponds to a single tweet. You can use it"
	@echo "multiple times to produce a test with multiple tweets"
	@echo "e.g. for a test with tweets coming at 999, 1000, 1001"
	@echo ">	make gentest N=test-eviction T=999  H='A B C'"
	@echo ">	make gentest N=test-eviction T=1000 H='B C D'"
	@echo ">	make gentest N=test-eviction T=1001 H='C D E'"
	@echo "To remove a generated test, use the same name but deltest"
	@echo ">	make deltest N=test-eviction"

# Using ascii data in the pipe
full.rb.a:
	cat data-gen/tweets.txt | ./bin/cleanit.rb -a | ./bin/online-graph.rb -a

# Using binary data in the pipe
full.rb:
	cat data-gen/tweets.txt | ./bin/cleanit.rb | ./bin/online-graph.rb

# only ascii data transfer in the pipe for python
full.py.a:
	cat data-gen/tweets.txt | ./bin/cleanit.py -a | ./bin/online-graph.py -a

W=data-gen/tweets.txt
runit: .prereq.heapdict
	./src/average_degree.py < $(W)

run: .prereq.heapdict
	./run.sh

# lint: do linting with two linters.
lint: | .prereq.flake8 .prereq.flake8
	python3 -m flake8 ./src/average_degree.py
	python3 -m pylint ./src/average_degree.py

# gentest: Produces insight tests. To produce tests with multiple tweets,
# invoke the gentest for each tweet but keep the N same. 
# base time is Mon Mar 28 23:23:12 +0000 2016
# usage:
#    make gentest T=<time in seconds from base> H=<hashtags> N=<name of test>
#
# e.g. To produce a three tweet combination, such that the last tweet evicts
# the first,
#
# 	make gentest T=0 H="A B C" N=test-eviction
# 	make gentest T=1 H="B C D" N=test-eviction
# 	make gentest T=61 H="C D E" N=test-eviction
#
# Be sure to use deltest with same parameters if you want to restart
# creating any test (because output.txt is not truncated).
T=0
H=my hash tags
N=use-the-test-name-here
INPUT=insight_testsuite/tests/$(N)/tweet_input/tweets.txt
OUTPUT=insight_testsuite/tests/$(N)/tweet_output/output.txt
gentest:
	mkdir -p $(dir $(INPUT)) $(dir $(OUTPUT))
	./bin/gen-tweet.py $(T) $(H) >> $(INPUT)
	cat $(INPUT) | ./src/average_degree.py > $(OUTPUT)
	cat $(OUTPUT)

deltest:
	rm -rf $(shell dirname $(dir $(INPUT)))

# prereq: Install all prerequisites for running.
U=
prereq: | .prereq.heapdict .prereq.coverage .prereq.flake8 .prereq.pylint
	@echo done.

.prereq.%:
	pip3 install $* $(U)
	@touch $@

# unittest: Run unit tests, and produce both branch and statement coverage. Due
# to the limitations of coverage.py, the detailed html report produced is only
# that of statement coverage. Both branch and statement coverage summary is
# printed on the console.
unittest: unittest-branch unittest-statement
	@echo done.

unittest-branch: .prereq.coverage
	rm -rf .coverage*
	python3 -m coverage run --branch --source=src/average_degree.py src/test_average_degree.py
	python3 -m coverage report
	python3 -m coverage html

unittest-statement: .prereq.coverage
	rm -rf .coverage*
	python3 -m coverage run --source=src/average_degree.py src/test_average_degree.py
	python3 -m coverage report
	python3 -m coverage html

# test: Run the insight_testsuite
test:
	@echo Executing `ls insight_testsuite/tests/ | wc -l` tests
	(cd insight_testsuite/ && ./run_tests.sh)
	@cat insight_testsuite/results.txt 

