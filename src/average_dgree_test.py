import average_degree
import unittest
import json

from io import StringIO
from unittest.mock import patch


class TestFunctions(unittest.TestCase):
    def test_get_tweet(self):
        myjson = '{"created_at":"Thu Nov 05 05:05:39 +0000 2015"}'
        tweet = average_degree.get_tweet(myjson)
        self.assertEqual(tweet['ctime'], 1446728739)

        myjson = '{"created_at":"Thu Nov 05 05:06:39 +0000 2015"}'
        tweet = average_degree.get_tweet(myjson)
        self.assertEqual(tweet['ctime'],  1446728799)

    def test_get_tweet_invalid_time(self):
        with patch('sys.stderr', new=StringIO()) as fakeOutput:
            myjson = '{"created_at":"Thu Nov 05"}'
            tweet = average_degree.get_tweet(myjson)
            self.assertIsNone(tweet)
            self.assertEqual(fakeOutput.getvalue().strip(), 'EXCEPTION: {"created_at":"Thu Nov 05"}')

    def test_get_tweet_limit(self):
        myjson = '{"limit":{"track":262,"timestamp_ms":"1459231487897"}}'
        tweet = average_degree.get_tweet(myjson)
        self.assertIsNone(tweet)

    def test_trim_tweet(self):
        myjson = '{"ctime":100}'
        j = json.loads(myjson)
        tweet = average_degree.trim_tweet(j)
        self.assertEqual(tweet, (100, []))

    def test_trim_tweet_entities(self):
        myjson = '{"ctime":100, "entities":{"hashtags":[{"text":"ABCD"}, {"text":"EFGH"}]}}'
        j = json.loads(myjson)
        ctime, htags = average_degree.trim_tweet(j)
        self.assertEqual(ctime, 100)
        self.assertEqual(len(htags), 2)

class TestTweetGraph(unittest.TestCase):
    def test_in_window(self):
        tg = average_degree.TweetGraph(1060, 60)
        self.assertEqual(tg.in_window(999), False)
        self.assertEqual(tg.in_window(1000), False)
        self.assertEqual(tg.in_window(1001), True)

    def test_add_edge(self):
        tg = average_degree.TweetGraph(0, 60)
        tg.edges = {(1,2): 1001, (1,3): 1002}
        for k in tg.edges.keys():
            tg.queue[k] = tg.edges[k]

        tg.add_edge(1003,(2,3))
        self.assertEqual(tg.edges, {(1,2): 1001, (1,3): 1002, (2,3): 1003})
        self.assertEqual(tg.queue.peekitem(), ((1, 2), 1001))
        self.assertEqual(tg.queue[(2,3)], 1003)
        self.assertEqual(tg.queue[(1,2)], 1001)
        tg.add_edge(1060,(2,3))
        self.assertEqual(tg.edges, {(1,2): 1001, (1,3): 1002, (2,3): 1060})
        tg.add_edge(1000,(2,3))
        self.assertEqual(tg.edges, {(1,2): 1001, (1,3): 1002, (2,3): 1060})

    def test_avg_vdegree(self):
        tg = average_degree.TweetGraph(0, 60)
        self.assertEqual(tg.avg_vdegree, 0)
        tg.edges = {(1,2): 1001, (1,3): 1002, (2,3):1003}
        for k in tg.edges.keys():
           tg.queue[k] = tg.edges[k]
        self.assertEqual(tg.avg_vdegree, 2)
    
    def test_collect_garbage(self):
        tg = average_degree.TweetGraph(0, 60)
        try: tg.collect_garbage()
        except: self.fail("collect_grabage() raised unexpectedly!")
        tg.edges = {(1,2): 999, (1,3): 1000, (2,3):1001}
        for k in tg.edges.keys():
           tg.queue[k] = tg.edges[k]
        
        # This should be noop.
        self.assertEqual(len(tg.edges.keys()), 3)
        tg.collect_garbage()
        self.assertEqual(len(tg.edges.keys()), 3)

        # this should remove both 999 and 1000
        tg.latest = 1060
        tg.collect_garbage()
        self.assertEqual(len(tg.edges.keys()), 1)

        # This should remove all.
        tg.latest = 1070
        tg.collect_garbage()
        self.assertEqual(len(tg.edges.keys()), 0)

    def test_gc_complete(self):
        tg = average_degree.TweetGraph(0, 60)
        self.assertEqual(tg.gc_complete(), True)
        tg.edges = {(1,2): 999, (1,3): 1000, (2,3):1001}
        for k in tg.edges.keys():
           tg.queue[k] = tg.edges[k]
        tg.latest = 1070
        self.assertEqual(tg.gc_complete(), False)
        tg.collect_garbage()
        self.assertEqual(tg.gc_complete(), True)

    def test_update_hashtags(self):
        tg = average_degree.TweetGraph(0, 60)
        kv = {(1,2): 999, (1,3): 1000, (2,3):1001}
        for (k,v) in kv.items():
            tg.update_hashtags(v, k)
        self.assertEqual(len(tg.edges.keys()), 3)
        tg.update_hashtags(1060, (2, 3))
        self.assertEqual(len(tg.edges.keys()), 1)
        tg.update_hashtags(1061, (2, 3))
        self.assertEqual(len(tg.edges.keys()), 1)


if __name__ == '__main__':
    unittest.main()

