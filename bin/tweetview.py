#!/usr/bin/env python3
"""
This module computes the rolling average vertex degree of a twitter
tweet hashtag graph. The given window is 60 seconds.
"""
import sys
import json
import time
import itertools
from heapdict import heapdict

WINDOW = 60
TIME_FMT = "%a %b %d %H:%M:%S +0000 %Y"


class TweetGraph:
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

        # Since edges are tuples, they are immutable and can be used as keys.
        old_ctime = self.edges.get(edge, None)
        if (not old_ctime) or (ctime > old_ctime):
            self.queue[edge] = ctime
            self.edges[edge] = ctime

    def update_hashtags(self, ctime, hashtags):
        """
        Process the given set of hashtags for the given time.
        """
        if not self.in_window(ctime):
            return

        if ctime > self.latest:
            self.latest = ctime

        self.collect_garbage()

        for edge in itertools.combinations(hashtags, 2):
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

    def collect_garbage(self):
        """
        Perform garbage collection.
        """
        while not self.gc_complete():
            min_edge, _ = self.queue.popitem()
            del self.edges[min_edge]

    def avg_vdegree(self):
        """
        Compute the average degree of a vertex.
        """
        if not self.edges:
            return 0

        # Our edge.keys are tuples of hashtags. We flatten them.
        nodes = set(itertools.chain(*self.edges.keys()))
        return (2.0 * len(self.edges))/len(nodes)


def strip_json(my_hash):
    """
    Initial processing of the json line. Remove all the fluf
    except created_at, and hashtags. Discard any tweet that
    do not contain these, or contains insufficient hash tags
    to make an edge.
    """

    # There are elements like limits that do not represent
    # tweets.
    created_at = my_hash.get('created_at', None)
    if not created_at:
        return None
    ctime = int(time.mktime(time.strptime(created_at, TIME_FMT)))

    htags = my_hash.get('entities', {}).get('hashtags', None)
    if not htags:
        return None

    # Discard any tweet that does not contain at least two distinct
    # hash tags, which is necessary to make at least one edge.
    hset = set(h['text'] for h in htags)
    if len(hset) < 2:
        return None

    # We convert the strings to their hash, which makes it simpler
    # and faster to process (especially if we want to do this part
    # in another process). We also sort to make sure that any two
    # keys always have a well defined edge name.
    hashtags = sorted(hash(a) for a in hset)
    return {'ctime': ctime, 'hashtags': hashtags}


def main():
    """
    The entry point.
    """
    tweeter = TweetGraph(0)
    for line in sys.stdin:
        try:
            jhash = strip_json(json.loads(line))
            if jhash:
                tweeter.update_hashtags(jhash['ctime'], jhash['hashtags'])
            # We have to print average each time a new tweet makes its
            # appearance irrespective of whether it can be ignored or not.
            print(tweeter.avg_vdegree())
        except:
            # We do not expect any records to be malformed. However, if there
            # are any, it is important not to abort the whole process, and
            # instead, just discard the record and let the user know through
            # another channel.
            print('EXCEPTION:', line, file=sys.stderr)

if __name__ == "__main__":
    main()
