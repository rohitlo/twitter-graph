#!/usr/bin/env ruby

require 'priority_queue'
require 'set'

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
    if old_ctime.nil? || ctime < old_ctime
      # update the priority if not exist, or larger.
      @queue[edge_key] = ctime
      @edges[edge_key] = ctime
    end
  end

  def process(ctime, nodes)
    if ctime > @latest
      @latest = ctime
    end
    nodes.combination(2).each do |edge|
      add_edge(ctime, edge)
      gc()
    end
  end

  def gc()
    while (@latest - (@queue[@queue.min] || @latest)) > WINDOW
      min_edge = @queue.min
      @queue.delete_min
      @edges.delete(min_edge)
    end
  end

  def avg()
    nodes = Set.new
    @edges.keys.each do |l_r|
      nodes.merge(l_r.split(' '))
    end
    # sum vertex degree = 2*edges
    return (2 * @edges.length)/nodes.length
  end
end

WINDOW = 60
$current = Processor.new
ARGF.each do |l|
  created, *nodes = l.split(/,/).map(&:to_i)

  # Dont bother to process it if the tweet is irrelevant
  next if ($current.latest - created) > WINDOW
  $current.process(created, nodes)
  puts $current.avg
  STDOUT.flush
end

