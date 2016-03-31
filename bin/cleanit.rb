#!/usr/bin/env ruby

# The cleanup is separated out into its own program for the simple reason
# that it is mostly independent of others, and we really want to remove
# as much data as possible before it enters into the main program.
# As per the given data-gen/tweets.txt example, less than 5% of the
# tweets will be useful.
#
# More importantly, because it is a _hot_ loop, and relatively simple
# with a consistent interface, it can be replaced by a C program if necessary.

require 'json'
require 'set'
require 'time'
require 'bindata'
require './bin/tweet.rb'

# Do not produce wrong results using the wrong interpreter
throw "Require at least 2.2" if RUBY_VERSION =~ /^(1[.]|2[.][01])/

def process(my_hash)
  begin
    # Only handle tweets (not the limit and any other kind of json).
    created_at = my_hash['created_at']
    return nil unless created_at
    ctime = Time.parse(created_at).to_i

    # How many hash tags did we get?
    entities =  my_hash['entities']
    return nil unless entities

    htags = entities['hashtags']
    return nil unless htags && !htags.empty?

    # We need the unique counts of hash tags to be > 2
    hset = Set.new(htags.map {|hm| hm['text']})
    return nil unless hset.length >= 2

    # IMPORTANT: The hash is inconsistent across invocations because
    # ruby uses a random seed before generating them. However, they
    # are guaranteed to be unique within a single process.
    # This is OK for us because we are computing _online_, and are
    # not worried about persistance of graph nodes.
    # DEBUG: nodes = hset.to_a.map(&:to_s).sort
    nodes = hset.to_a.map(&:hash).sort
    return {:ctime => ctime, :nodes => nodes}
  rescue
    # we only want to discard the record in case of any error
    # in the stream. It may be worthwhile to log this record
    # but that may be counter productive when we are dealing
    # with a large amount of data, as we expect with twitter.
    return nil
  end
end

$binary = if ARGV[0] == '-a' then false else true end

STDIN.each do |line|
  v = process(JSON.parse(line))
  next unless v
  if $binary
    # Rather than printing the created_at and nodes directly in the STDOUT as
    # strings separated by newline, we output binary records. This allows us
    # to reduce the data being written. (28k -> 16k for tweets.txt)
    to_tweet(v[:ctime], v[:nodes]).write(STDOUT)
  else
    # print the record directly which is the simplest, and easiest to debug.
    puts [v[:ctime], v[:nodes]].join(',')
  end
  STDOUT.flush
end
