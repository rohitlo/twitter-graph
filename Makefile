.DEFAULT_GOAL := all

# thanks to http://marmelab.com for this idea.
all:
	  @awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_0-9-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help: ## Full Help.
	@echo "The following commands are provided:"
	@echo "Execute the run.sh"
	@echo ">	make run"
	@echo
	@echo "Execute the program on a given tweet file"
	@echo ">	make runit W=./data-gen/tweets.txt"
	@echo
	@echo "Install all prerequisites"
	@echo ">	make prereq"
	@echo
	@echo "Install all prerequisites on the user home"
	@echo ">	make prereq U=--user"
	@echo
	@echo "Run lint on the source"
	@echo ">	make lint"
	@echo
	@echo "Run unittests and extract coverage"
	@echo ">	make unittest"
	@echo
	@echo "Report detailed coverage of previous unittests in html"
	@echo ">	make coverage"
	@echo
	@echo "Run the insight test suite"
	@echo ">	make test"
	@echo
	@echo "Generate a test for the insight test suite (see Makefile for examples)"
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
	@echo
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
runit: .prereq.heapdict ## Run the program on a given tweet (W=<tweet-file>)
	./src/average_degree.py < $(W)

run: .prereq.heapdict ## Execute ./run.sh
	./run.sh

# We disable `invalid-sequence-index` because it is a spurious warning
lint: lint-flake8 lint-pylint ## Run linters on src/average_degree.py
	@echo done.

lint-flake8: | .prereq.flake8 ## Run flake8 (lint) on src/average_degree.py
	python3 -m flake8 ./src/average_degree.py

lint-pylint: | .prereq.pylint ## Run pylint (lint) on src/average_degree.py
	python3 -m pylint  --disable=E1126 ./src/average_degree.py

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
gentest: ## Generate an insight test case (see make help for examples).
	mkdir -p $(dir $(INPUT)) $(dir $(OUTPUT))
	./bin/gen-tweet.py $(T) $(H) >> $(INPUT)
	cat $(INPUT) | ./src/average_degree.py > $(OUTPUT)
	cat $(OUTPUT)

deltest: ## Remove an insight test case (N=<test case name>)
	rm -rf $(shell dirname $(dir $(INPUT)))

# prereq: Install all prerequisites for running.
U=
prereq: | .prereq.heapdict .prereq.coverage .prereq.flake8 .prereq.pylint ## Install all prerequisites
	@echo done.

.prereq.%:
	pip3 install $* $(U)
	@touch $@

# Due to the limitations of coverage.py, the detailed html report produced is
# only that of statement coverage. Both branch and statement coverage summary is
# printed on the console.
unittest: unittest-branch unittest-statement ## Run unittests and print branch and statement coverage
	@echo done.

unittest-branch: .prereq.coverage ## Run unittests and report branch coverage
	python3 -m coverage run --branch --source=src/average_degree.py src/test_average_degree.py
	@python3 -m coverage report

unittest-statement: .prereq.coverage ## Run unittests and report statement coverage
	python3 -m coverage run --source=src/average_degree.py src/test_average_degree.py
	@python3 -m coverage report

coverage: ## Collect previously run unittest coverage detailed report in ./htmlcov
	python3 -m coverage html

test: ## Run the insight test suite
	@echo Executing `ls insight_testsuite/tests/ | wc -l` tests
	(cd insight_testsuite/ && ./run_tests.sh)
	@cat insight_testsuite/results.txt 

clean: ## Remove traces of previous execution such as coverage, tempfiles
	@rm -rf htmlcov .coverage*
	@rm -rf insight_testsuite/results.txt 
