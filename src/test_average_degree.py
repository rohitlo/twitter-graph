import average_degree
import unittest
import json

from io import StringIO
from unittest.mock import patch


class TestFunctions(unittest.TestCase):

    def setUp(self):
        self.json_1 =  '{"created_at":"Thu Nov 05 05:05:39 +0000 2015"}'
        self.json_2 =  '{"created_at":"Thu Nov 05 05:06:39 +0000 2015"}'
        self.json_3 =  '{"created_at":"Thu Nov 05 05:06:39 +0000 2015", "entities":{"hashtags":[{"text":"ABCD"}, {"text":"EFGH"}]}}'
        self.json_invalid_time =  '{"created_at":"Thu Nov 05"}'
        self.json_limit = '{"limit":{"track":262,"timestamp_ms":"1459231487897"}}'

    def tearDown(self):
        pass

    def test_get_tweet(self):
        """Should correctly recognize the created_at"""
        tweet1 = average_degree.get_tweet(self.json_1)
        self.assertEqual(tweet1['ctime'], 1446728739)

        tweet2 = average_degree.get_tweet(self.json_2)
        self.assertEqual(tweet2['ctime'] - tweet1['ctime'],  60)

    def test_get_tweet_invalid_time(self):
        """Should correctly identify invalid time format"""
        with patch('sys.stderr', new=StringIO()) as fakeOutput:
            tweet = average_degree.get_tweet(self.json_invalid_time)
            self.assertIsNone(tweet)
            self.assertEqual(fakeOutput.getvalue().strip(), 'EXCEPTION: {"created_at":"Thu Nov 05"}')

    def test_get_tweet_limit(self):
        """Should correctly identify limit records"""
        tweet = average_degree.get_tweet(self.json_limit)
        self.assertIsNone(tweet)

    def test_main_tweet(self):
        """Should correctly determine vertex degree of tweet in string"""
        with patch('sys.stdin', StringIO(self.json_3)), patch('sys.stdout', new=StringIO()) as fakeOutput:
            average_degree.main()
            self.assertEqual(fakeOutput.getvalue().strip(), '1.00')

    def test_main_limit(self):
        """Should correctly discard limit"""
        with patch('sys.stdin', StringIO(self.json_limit)), patch('sys.stdout', new=StringIO()) as fakeOutput:
            average_degree.main()
            self.assertEqual(fakeOutput.getvalue().strip(), '')


class TestTweetGraph(unittest.TestCase):
    def setUp(self):
        self.cjson_1 = '{"ctime":100}'
        self.cjson_2 = '{"ctime":1060, "entities":{"hashtags":[{"text":"ABCD"}, {"text":"EFGH"}]}}'

        self.etg = average_degree.TweetGraph(1060, 60)
        self.mytg = average_degree.TweetGraph(1000, 60)

        edges = {('A','B'): 999, ('A','C'): 1000, ('B','C'):1001}
        self.mytg.edges = edges
        for k in edges.keys():
            self.mytg.queue[k] = edges[k]

    def set_current_edges(self, edges):
        self.etg.edges = edges
        for k in edges.keys():
            self.etg.queue[k] = edges[k]

    def test_in_window(self):
        """Should correctly determine if passed time is within window."""
        self.etg.latest = 1060
        self.etg.window = 60
        self.assertEqual(self.etg.in_window(999), False)
        self.assertEqual(self.etg.in_window(1000), False)
        self.assertEqual(self.etg.in_window(1001), True)

    def test_add_edge(self):
        """Should add a new edge correctly on both queue and dict"""
        self.set_current_edges({('A','B'): 1001, ('A','C'): 1002})

        self.etg.add_edge(1003,('B','C'))
        self.assertEqual(self.etg.edges, {('A','B'): 1001, ('A','C'): 1002, ('B','C'): 1003})
        self.assertEqual(self.etg.queue.peekitem(), (('A','B'), 1001))
        self.assertEqual(self.etg.queue[('B','C')], 1003)
        self.assertEqual(self.etg.queue[('A','B')], 1001)

    def test_add_edge_update(self):
        """Should update if an edge exists, and later time."""
        self.mytg.add_edge(1060,('B','C'))
        self.assertEqual(self.mytg.edges, {('A','B'): 999, ('A','C'): 1000, ('B','C'): 1060})


    def test_add_edge_no_expired(self):
        """Should not add an expired edge."""
        self.mytg.add_edge(1000,('B','C'))
        self.assertEqual(self.mytg.edges, {('A','B'): 999, ('A','C'): 1000, ('B','C'): 1001})


    def test_avg_vdegree_zero(self):
        """Should correctly return zero average vertex degree for empty"""
        self.assertEqual(self.etg.avg_vdegree, 0)

    def test_avg_vdegree_for_line(self):
        """Should correctly return 1 as average vertex degree for line"""
        self.set_current_edges({('A','B'): 1001})
        self.assertEqual(self.etg.avg_vdegree, 1)

    def test_avg_vdegree_for_triangle(self):
        """Should correctly return 2 as average vertex degree for triangle"""
        self.assertEqual(self.mytg.avg_vdegree, 2)

    def test_collect_garbage_empty(self):
        """Should not error out on gc of empty graph"""
        try: self.etg.collect_garbage()
        except: self.fail("collect_grabage() raised unexpectedly!")

    def test_collect_garbage_noop(self):
        """Should correctly exit gc when there is nothing to collect"""
        self.mytg.latest = 1003
        self.mytg.collect_garbage()
        self.assertEqual(len(self.mytg.edges.keys()), 3)

    def test_collect_garbage_1(self):
        """Should correctly garbage collect"""
        self.mytg.latest = 1060
        # this should remove both 999 and 1000
        self.mytg.collect_garbage()
        self.assertEqual(len(self.mytg.edges.keys()), 1)

    def test_collect_garbage_all(self):
        """Should correctly garbage collect all expired"""
        self.mytg.latest = 1070
        # this should remove all
        self.mytg.collect_garbage()
        self.assertEqual(len(self.mytg.edges.keys()), 0)

    def test_gc_complete_empty(self):
        """Should correctly identify GC exit on empty graph"""
        self.assertEqual(self.etg.gc_complete(), True)

    def test_gc_complete(self):
        """Should correctly identify if GC should continue"""
        self.tg.latest = 1070
        self.assertEqual(self.tg.gc_complete(), False)

    def test_gc_complete(self):
        """Should correctly identify if GC should exit after one GC is done"""
        self.mytg.latest = 1070
        self.mytg.collect_garbage()
        self.assertEqual(self.mytg.gc_complete(), True)

    def test_update_hashtags(self):
        """Should correctly update hashtags when tweets arrive"""
        self.mytg.latest = 1000
        self.mytg.update_hashtags(1004, ('B','C'))
        self.assertEqual(len(self.mytg.edges.keys()), 3)

    def test_update_hashtags(self):
        """Should correctly ignore expired hashtags"""
        self.mytg.latest = 1003
        self.mytg.update_hashtags(800, ('B','C'))
        self.assertEqual(len(self.mytg.edges.keys()), 3)

    def test_update_hashtags_with_gc(self):
        """Should correctly start garbage collection on new tweet"""
        self.mytg.latest = 1000
        self.mytg.update_hashtags(1061, ('B','C'))
        self.assertEqual(len(self.mytg.edges.keys()), 1)

    def test_trim_tweet(self):
        """Should correctly extract the ctime field"""
        j = json.loads(self.cjson_1)
        tweet = self.etg.trim_tweet(j)
        self.assertEqual(tweet, (100, []))

    def test_trim_tweet_entities(self):
        """Should correctly extract the hashtags"""
        j = json.loads(self.cjson_2)
        ctime, htags = self.etg.trim_tweet(j)
        self.assertEqual(ctime, 1060)
        self.assertEqual(len(htags), 2)

    def test_process_tweet(self):
        j = json.loads(self.cjson_2)
        vdegree = self.etg.process_tweet(j)
        self.assertEqual(vdegree, 1)

if __name__ == '__main__':
    unittest.main()

