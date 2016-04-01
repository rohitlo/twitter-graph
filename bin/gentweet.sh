
input="insight_testsuite/tests/$1/tweet_input"
output="insight_testsuite/tests/$1/tweet_output"
mkdir -p $input $output
shift
t=$1
shift
echo $input $output
echo time = $t
echo nodes = $@
./bin/gen-tweet.py $t $@ >> $input/tweets.txt
cat $input/tweets.txt | ./src/average_degree.py > $output/output.txt
cat $output/output.txt
