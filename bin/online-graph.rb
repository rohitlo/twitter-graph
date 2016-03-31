#!/usr/bin/env ruby

require 'priority_queue'
require 'bindata'
require './bin/tweet.rb'
require 'set'

# Do not produce wrong results using the wrong interpreter
throw "Require at least 2.2" if RUBY_VERSION =~ /^(1[.]|2[.][01])/

WINDOW = 60

class Processor
  attr_accessor :latest
  def initialize
    @latest = 0
    @edges = {}
    @queue = PriorityQueue.new()
  end

  def add_edge(ctime, edge)
    edge_key = edge.join(' ')
    # does the edge already exist?
    old_ctime = @edges[edge_key]
    if old_ctime.nil? || ctime > old_ctime
      # update the priority if not exist, or larger.
      @queue[edge_key] = ctime
      @edges[edge_key] = ctime
    end
  end

  def process!(ctime, nodes)
    # ignore if too old.
    return if (@latest - ctime) > WINDOW

    # Update the latest if it is a new tweet.
    if ctime > @latest
      @latest = ctime
    end
    # GC should be called _before_ addition of
    # new nodes.
    gc()
    nodes.combination(2).each do |edge|
      add_edge(ctime, edge)
    end
  end

  def gc_complete?()
    minkval = @queue.min
    return true unless minkval
    mink,minv = minkval
    v = (@latest - minv) > WINDOW
    return !v
  end

  def gc()
    while !gc_complete?
      min_edge, prio = @queue.min
      @queue.delete(min_edge)
      @edges.delete(min_edge)
    end
  end

  def avg()
    nodes = Set.new
    @edges.keys.each do |l_r|
      nodes.merge(l_r.split(' '))
    end
    return (2.0 * @edges.length)/nodes.length
  end
end

def binread
  while !STDIN.eof? do
    t = Tweet.read(STDIN)
    yield t.created_at, t.nodes.to_a
  end
end

def textread
  STDIN.each do |l|
    case l
    when /^@/   # For debug.
      puts l,"\n"
      next
    when /^#/
      next
    end
    created, *nodes = l.split(/,/).map(&:to_i)
    yield created, nodes
  end
end

$binary = if ARGV[0] == '-a' then false else true end

$current = Processor.new
if $binary
  binread do |created, nodes|
    $current.process!(created, nodes)
    puts $current.avg
  end
else
  textread do |created, nodes|
    $current.process!(created, nodes)
    puts $current.avg
  end
end
