#!/usr/bin/env python3
import sys
import json
import time
from heapdict import heapdict
import itertools

WINDOW = 60

class Processor:
    def __init__(self):
        self.latest = 0
        self.edges = {}
        self.queue = heapdict()

    def is_valid(self, ctime):
        return False if (self.latest - ctime ) >= WINDOW else True


    def add_edge(self, ctime, edge):
        edge_key = ' '.join(map(str,edge))
        old_ctime = self.edges.get(edge_key, None)
        if (not old_ctime) or (ctime > old_ctime):
            self.queue[edge_key] = ctime
            self.edges[edge_key] = ctime

    def process(self, ctime, nodes):
        if not self.is_valid(ctime): return

        if ctime > self.latest:
            self.latest = ctime

        self.gc()

        for edge in itertools.combinations(nodes, 2):
            self.add_edge(ctime, edge)

    def gc_complete(self):
        if len(self.queue) == 0: return True
        edge, ctime = self.queue.peekitem()
        return self.is_valid(ctime)

    def gc(self):
        while not self.gc_complete():
            min_edge, ctime = self.queue.popitem()
            del self.edges[min_edge]

    def avg(self):
        if not self.edges: return 0
        nodes = set()
        for l_r in self.edges.keys():
            nodes.update(l_r.split(' '))
        return (2.0 * len(self.edges))/len(nodes)

def process(my_hash):
    created_at = my_hash.get('created_at', None)
    if not created_at: return None
    ctime = int(time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y")))

    entities = my_hash.get('entities', None)
    if not entities: return None
    
    htags = entities.get('hashtags', None)
    if not htags: return None
    
    hset = set([hm['text'] for hm in  htags])
    if len(hset) < 2: return None

    nodes = sorted(hash(a)  for a in hset)
    return {'ctime':ctime, 'nodes':nodes}

current = Processor()
for line in sys.stdin:
    v = process(json.loads(line))
    if not v:
        print(current.avg())
        continue

    current.process(v['ctime'], v['nodes'])
    print(current.avg())


