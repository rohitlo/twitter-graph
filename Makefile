
data/mytweets.txt: mytweets

mytweets:
	cat data-gen/tweets.txt | ./bin/cleanit.rb > data/mytweets.txt

avg:
	cat data/mytweets.txt | ./bin/online-graph.rb

full.rb.a:
	cat data-gen/tweets.txt | ./bin/cleanit.rb -a | ./bin/online-graph.rb -a

full.py.a:
	cat data-gen/tweets.txt | ./bin/cleanit.py -a | ./bin/online-graph.py -a

W=data-gen/tweets.txt
run:
	./src/average_degree.py < $(W)

data:
	mkdir -p data

lint:
	python3 -m flake8 ./src/average_degree.py
	python3 -m pylint ./src/average_degree.py

T=data/test.txt
mytest:
	cat $(T) | ./bin/online-graph.py -a

prereq:
	pip3 install heapdict
	pip3 install coverage
	pip3 install flake8
	pip3 install pylint

unittest:
	rm -rf .coverage*
	python3 -m coverage run --branch --source=src/average_degree.py src/test_average_degree.py
	python3 -m coverage report
	python3 -m coverage run --source=src/average_degree.py src/test_average_degree.py
	python3 -m coverage report
	python3 -m coverage html

test:
	cd insight_testsuite/; ./run_tests.sh
