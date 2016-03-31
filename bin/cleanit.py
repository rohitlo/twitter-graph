#!/usr/bin/env python3
import sys
import json
import time

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

binary = False if (len(sys.argv) > 1 and sys.argv[1] == '-a') else True


for line in sys.stdin:
    v = process(json.loads(line))
    if not v: continue
    if binary:
        #print('binary')
        pass

    else:
        print(v['ctime'], end=',')
        print(','.join(map(str,v['nodes'])))
