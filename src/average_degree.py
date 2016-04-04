#!/usr/bin/env python3
"""
This module computes the rolling average vertex degree of a twitter
tweet hashtag graph.
"""
import itertools
import json
import sys
import time
import argparse
import logging
from typing import Dict, Tuple, List, Any, Optional, cast, Iterable

from heapdict import heapdict

TIME_FMT = "%a %b %d %H:%M:%S +0000 %Y"


class TweetGraph:
    """
    Process the tweet, and keeps track of the time. This implementation uses
    a priority queue (heap) containing a tuple (edge,created time) as the
    backbone.
    """
    def __init__(self, curtime: int, window: int) -> None:
        """
        Initialize the TweetGraph
        :param curtime: The starting time
        :param window: The sliding window
        """
        self.latest = curtime
        self.edges = {}  # type: Dict[Tuple[str, str], int]
        self.queue = heapdict()
        self.window = window

    def in_window(self, ctime: int) -> bool:
        """
        Is the passed in time within the window? Note that the formula is
        `(self.latest - ctime) >= window`
        :param ctime: The time which has to be checked.
        :return: boolean indicating whether passed
        """
        return False if (self.latest - ctime) >= self.window else True

    def add_edge(self, ctime: int, edge: Tuple[str, str]) -> None:
        """
        Add or update the given edge with the given time to
        our database of edges.
        :param ctime: The creation time of the tweet
        :param edge: A tuple containing two hash tags
        """
        old_ctime = self.edges.get(edge, None)
        if (not old_ctime) or (ctime > old_ctime):
            self.queue[edge] = ctime
            self.edges[edge] = ctime

    def update_hashtags(self, ctime: int, hashtags: List[str]) -> None:
        """
        Process the given set of hashtags for the given time.
        :param ctime: The creation time of the tweet
        :param hashtags: The unique hashtags associated with this tweet.
        """
        if not self.in_window(ctime):
            return
        if ctime > self.latest:
            self.latest = ctime

        # Ensure that we perform gc _before_ checking if the
        # prerequisite number of hashtags are present.
        self.collect_garbage()

        # very nicely, we do not need to check for hashtags being
        # atleast two because itertools.combinations() will not
        # produce an item in that case.
        for edge in cast(Iterable, itertools.combinations(hashtags, 2)):
            self.add_edge(ctime, edge)

    def gc_complete(self) -> bool:
        """
        Check if the gc is complete.
        """
        if len(self.queue) == 0:
            return True
        _, ctime = self.queue.peekitem()
        return self.in_window(ctime)

    def collect_garbage(self) -> None:
        """
        Perform garbage collection.
        """
        while not self.gc_complete():
            min_edge, _ = self.queue.popitem()
            del self.edges[min_edge]

    @property
    def avg_vdegree(self) -> float:
        """
        Compute the average degree of a vertex using the formula 2*edges/nodes.
        """
        if not self.edges:
            return 0
        # Our edge.keys are tuples of hashtags. We flatten them.
        nodes = set(itertools.chain.from_iterable(self.edges.keys()))
        return (2.0 * len(self.edges)) / len(nodes)

    def process_tweet(self, tweet: Dict[str, Any]) -> float:
        """
        Process a tweet and return the current average vertex degree
        :param tweet: the dict containing the stripped tweet.
        :return: The current vertex degree
        """
        ctime, htags = self.trim_tweet(tweet)
        self.update_hashtags(ctime, htags)
        # We have to print average each time a new tweet makes its
        # appearance irrespective of whether it can be ignored or not.
        return self.avg_vdegree

    @staticmethod
    def trim_tweet(my_hash: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Initial processing of the json line. Remove all the fluf
        except created_at, and hashtags.
        :param my_hash: The tweet dict to be de-fluffed
        :return: A tuple containing ctime and hashtags if
        the number of unique hashtags is at least two. None otherwise.
        """

        htags = my_hash.get('entities', {}).get('hashtags', [])
        # We sort to make sure that any two
        # keys always have a well defined edge name.
        hashtags = sorted(set(h['text'] for h in htags))
        return my_hash['ctime'], hashtags


def get_tweet(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse the line into json, and check that it is a valid tweet
    and not a limit message.
    :param line: The json line to be parsed.
    :return: If this is a valid tweet, the dict containing creation
    time and hashtags. None otherwise.
    """
    try:
        j = json.loads(line)
        created_at = j.get('created_at', None)
        if not created_at:
            return None

        # We validate the creation time here. If the creation time
        # is in invalid format, it is an invalid tweet.
        ctime = int(time.mktime(time.strptime(created_at, TIME_FMT)))
        j['ctime'] = ctime
        return j
    except ValueError:
        # We do not expect any records to be malformed. However, if there
        # are any, it is important not to abort the whole process, and
        # instead, just discard the record and let the user know through
        # another channel.
        logging.warning('malformed: %s', line)
        return None


def main():
    """
    The entry point. We require a single parameter: the window length.
    We also accept tweets in stdin, and write to stdout.
    """
    pcmd = argparse.ArgumentParser()
    pcmd.add_argument('window', type=int, help='window for rolling average')
    args = pcmd.parse_args()
    tweetgraph = TweetGraph(0, args.window)
    for line in sys.stdin:
        tweet = get_tweet(line)
        # Do not print rolling average in case this is not a valid tweet
        if tweet:
            print('{:0.2f}'.format(tweetgraph.process_tweet(tweet)))

if __name__ == "__main__":
    main()
