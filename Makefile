.DEFAULT_GOAL := all
.PHONY: all help
# thanks to http://marmelab.com for this idea.
all:
	  @awk 'BEGIN {FS = ":.*?## "} \
					/^[a-zA-Z_0-9-]+:.*?## / {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' \
		$(MAKEFILE_LIST)

help: ## Detailed help.
	@sed -ne 's,^## ,,gp' $(MAKEFILE_LIST) | \
		awk '/^>/{printf "\033[32m%s\033[0m\n", $$0} \
				!/^>/{print;}'

## Execute the program on a given tweet file
## >	make runit W=./data-gen/tweets.txt
W=data-gen/tweets.txt
runit: .prereq.heapdict ## Run the program on a given tweet (W=<tweet-file>)
	./src/average_degree.py < $(W)

# Using ascii data in the pipe. Not a rolling average
rb-ascii:
	./bin/cleanit.rb -a < $(W) | ./bin/online-graph.rb -a

# Using binary data in the pipe. Not a rolling average
rb-binary:
	./bin/cleanit.rb <$(W) | ./bin/online-graph.rb

# only ascii data transfer in the pipe for python. Not a rolling average
py-ascii:
	./bin/cleanit.py -a <$(W) | ./bin/online-graph.py -a

## Execute the run.sh
## >	make run
run: .prereq.heapdict ## Execute ./run.sh
	./run.sh
## 

## Run lint on the source
## >	make lint
lint: lint-flake8 lint-pylint ## Run linters on src/average_degree.py
	@echo done.

## Run flake8 on the source
## >	make lint-flake8
lint-flake8: | .prereq.flake8 ## Run flake8 (lint) on src/average_degree.py
	python3 -m flake8 ./src/average_degree.py

## Run pylint on the source
## >	make lint-pylint
# We disable `invalid-sequence-index` because it is a spurious warning
lint-pylint: | .prereq.pylint ## Run pylint (lint) on src/average_degree.py
	python3 -m pylint  --disable=E1126 ./src/average_degree.py
## 


## Generate a test for the insight test suite 
## The T parameter uses Mon Mar 28 23:23:12 +0000 2016 as the base time
## >	make gentest T=<seconds from base> H=<hashtags> N=<test name>
## e.g.
## >	make gentest T=0 H='A B C' N=test-eviction
## Each gentest invocation corresponds to a single tweet. You can use it
## multiple times to produce a test with multiple tweets if N is same.
## e.g. for a test with tweets coming at 999, 1000, 1001
## >	make gentest N=test-eviction T=999  H='A B C'
## >	make gentest N=test-eviction T=1000 H='B C D'
## >	make gentest N=test-eviction T=1001 H='C D E'
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

## To remove a generated test, use the same name but deltest
## >	make deltest N=test-eviction
## Be sure to use deltest with same parameters if you want to restart
## creating any test (because output.txt is not truncated).
## 
deltest: ## Remove an insight test case (N=<test case name>)
	rm -rf $(shell dirname $(dir $(INPUT)))

## Install all prerequisites
## >	make prereq
## Install all prerequisites on the user home
## >	make prereq U=--user
## 
O=--user
prereq: | .prereq.heapdict .prereq.coverage .prereq.flake8 .prereq.pylint ## Install all prerequisites
	@echo done.

i-%: .prereq.%
	@echo done

.prereq.%:
	pip3 install $* $(O)
	@touch $@


SRC=src/average_degree.py
TST=src/test_average_degree.py

## Run unittests and print statement and branch coverage
## >	make unittest-c
unittest-c: unittest-branch unittest-statement ## Run unittests and print branch and statement coverage
	@echo done.

## Run unittests and print branch coveage
## >	make unittest-branch
unittest-branch: .prereq.coverage .prereq.heapdict ## Run unittests and report branch coverage
	python3 -m coverage run --branch --source=$(SRC) $(TST)
	@python3 -m coverage report

## Run unittests and print statement coveage
## >	make unittest-statement
unittest-statement: .prereq.coverage .prereq.heapdict ## Run unittests and report statement coverage
	python3 -m coverage run --source=$(SRC) $(TST)
	@python3 -m coverage report

## Run unittests without collecting coverage
unittests: .prereq.heapdict  ## Run unittets without collecting coverage
	python3 $(TST) -v

## Report detailed coverage of previous unittests in html
## >	make coverage
coverage: ## Collect previously run unittest coverage detailed report in ./htmlcov
	@test -e .coverage || echo you have not executed unittest-statement or unittest-branch
	@test -e .coverage && python3 -m coverage html
	@echo Coverage report generated at $(PWD)/htmlcov/index.html
## 

## Run the insight test suite
## >	make test
## 
test: .prereq.heapdict ## Run the insight test suite
	@echo Executing `ls insight_testsuite/tests/ | wc -l` tests
	(cd insight_testsuite/ && ./run_tests.sh)
	@cat insight_testsuite/results.txt 

## Cleanup all the temporary files
## >	make clean
clean: ## Remove traces of previous execution such as coverage, tempfiles, touch files etc.
	@rm -rf htmlcov .coverage*
	@rm -rf insight_testsuite/results.txt 
	@rm -rf .prereq.*

## Generate plot from the data given.
## >	make plot
plot: analysis/plot.png ## Generate plot from the data
	@echo done.

analysis/plot.png: analysis/data.csv
	./analysis/plot.R
