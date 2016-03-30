
data/mytweets.txt:
	cat data-gen/tweets.txt | ./bin/cleanit.rb > data/mytweets.txt

avg:
	cat data/mytweets.txt | ./bin/online-graph.rb

data:
	mkdir -p data

