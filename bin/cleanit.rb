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

def process(my_hash)
  begin
    # sanity check
    myid = my_hash['id']
    return nil unless myid

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
    return {:id => myid, :ctime => ctime, :nodes => nodes}
  rescue
    # we only want to discard the record in case of any error
    # in the stream.
    return nil
  end
end

case RUBY_VERSION
when /^1./
  puts "Require at least 2.2"
  exit 1
when /^2.[01]/
  puts "Require at least 2.2"
  exit 1
end

ARGF.each do |l|
  v = process(JSON.parse(l))
  next unless v

  # Generate edges with creating time attached.
  v[:nodes].combination(2).each do |n|
    # DEBUG p v
    print v[:id],',', v[:ctime],',',n.join(','), "\n"
  end
  STDOUT.flush
end

