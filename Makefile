
data/mytweets.txt: mytweets

mytweets:
	cat data-gen/tweets.txt | ./bin/cleanit.rb > data/mytweets.txt

avg:
	cat data/mytweets.txt | ./bin/online-graph.rb

full.rb.a:
	cat data-gen/tweets.txt | ./bin/cleanit.rb -a | ./bin/online-graph.rb -a

full.py.a:
	cat data-gen/tweets.txt | ./bin/cleanit.py -a | ./bin/online-graph.py -a

full:
	cat data-gen/tweets.txt | ./bin/tweetview.py

data:
	mkdir -p data

lint:
	python3 -m flake8 ./bin/tweetview.py
	python3 -m pylint ./bin/tweetview.py | head

T=data/test.txt
test:
	cat $(T) | ./bin/online-graph.py -a
