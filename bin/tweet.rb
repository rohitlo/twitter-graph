class Tweet < BinData::Record
  uint64be :created_at
  int8  :len, :value => lambda { nodes.length }
  array :nodes, :type => :int64be, :initial_length => :len
end

def to_tweet(ctime,nodes)
  tweet = Tweet.new
  tweet.created_at = ctime
  tweet.nodes = nodes
  return tweet
end
