#!/usr/bin/env python3
import sys
import heapdict
import itertools

#heapq

WINDOW = 60

class Processor:
    def __init__(self):
        self.latest = 0
        self.edges = {}
        self.queue = heapdict.heapdict()

    def add_edge(self, ctime, edge):
        edge_key = ' '.join(map(str,edge))
        old_ctime = self.edges.get(edge_key, None)
        if (not old_ctime) or (ctime > old_ctime):
            self.queue[edge_key] = ctime
            self.edges[edge_key] = ctime

    def process(self, ctime, nodes):
        if (self.latest - ctime ) > WINDOW: return

        if ctime > self.latest:
            self.latest = ctime

        self.gc()

        for edge in itertools.combinations(nodes, 2):
            self.add_edge(ctime, edge)

    def gc_complete(self):
        if len(self.queue) == 0: return True
        edge, ctime = self.queue.peekitem()
        v = (self.latest - ctime) > WINDOW
        return (not v)

    def gc(self):
        while not self.gc_complete():
            min_edge, ctime = self.queue.popitem()
            del self.edges[min_edge]

    def avg(self):
        nodes = set()
        for l_r in self.edges.keys():
            nodes.update(l_r.split(' '))
        return (2.0 * len(self.edges))/len(nodes)


def textread():
    for l in sys.stdin:
        created, *nodes = map(int, l.rstrip('\n').split(','))
        yield (created, nodes)



binary = False if (len(sys.argv) > 1 and sys.argv[1] == '-a') else True

current = Processor()
if binary:
    pass
else:
    for (created, nodes) in textread():
        current.process(created, nodes)
        print(current.avg())
    pass

