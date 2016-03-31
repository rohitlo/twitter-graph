#!/usr/bin/env python3
"""
This module computes the rolling average indegree of a twitter
tweet hashtag graph.
"""
import sys
import json
import time
import itertools
from heapdict import heapdict

WINDOW = 60
TIME_FMT = "%a %b %d %H:%M:%S +0000 %Y"


class TweetProcessor:
    """
    Process the tweet, and keeps track of the time.
    """
    def __init__(self, curtime):
        self.latest = curtime
        self.edges = {}
        self.queue = heapdict()

    def in_window(self, ctime):
        """
        Is the passed in creation time within the window?
        """
        return False if (self.latest - ctime) >= WINDOW else True

    def add_edge(self, ctime, edge):
        """
        Add or update the given edge with the given time to
        our database of edges.
        """
        edge_key = ' '.join(map(str, edge))
        old_ctime = self.edges.get(edge_key, None)
        if (not old_ctime) or (ctime > old_ctime):
            self.queue[edge_key] = ctime
            self.edges[edge_key] = ctime

    def process(self, ctime, nodes):
        """
        Process the given set of hashtags for the given time.
        """
        if not self.in_window(ctime):
            return

        if ctime > self.latest:
            self.latest = ctime

        self.dogc()

        for edge in itertools.combinations(nodes, 2):
            self.add_edge(ctime, edge)

    def gc_complete(self):
        """
        Check if the GC can be stopeed (Does any edge remain
        that can be removed?)
        """
        if len(self.queue) == 0:
            return True
        _, ctime = self.queue.peekitem()
        return self.in_window(ctime)

    def dogc(self):
        """
        Perform garbage collection.
        """
        while not self.gc_complete():
            min_edge, _ = self.queue.popitem()
            del self.edges[min_edge]

    def average(self):
        """
        Compute the average degree of a vertex.
        """
        if not self.edges:
            return 0
        nodes = set()
        for l_r in self.edges.keys():
            nodes.update(l_r.split(' '))
        return (2.0 * len(self.edges))/len(nodes)


def check_json(my_hash):
    """
    Initial processing of the json line.
    """
    created_at = my_hash.get('created_at', None)
    if not created_at:
        return None
    ctime = int(time.mktime(time.strptime(created_at, TIME_FMT)))

    entities = my_hash.get('entities', None)
    if not entities:
        return None

    htags = entities.get('hashtags', None)
    if not htags:
        return None

    hset = set(hm['text'] for hm in htags)
    if len(hset) < 2:
        return None

    nodes = sorted(hash(a) for a in hset)
    return {'ctime': ctime, 'nodes': nodes}


def main():
    """
    The entry point.
    """
    tweeter = TweetProcessor(0)
    for line in sys.stdin:
        jhash = check_json(json.loads(line))
        if not jhash:
            print(tweeter.average())
            continue

        tweeter.process(jhash['ctime'], jhash['nodes'])
        print(tweeter.average())

if __name__ == "__main__":
    main()
