"""Pure geometric road-connectivity checks; not a tanker navigation profile."""
import heapq
import math

def directions(tags):
    access=next((tags[k] for k in ('motor_vehicle','vehicle','access') if k in tags),None)
    if access in {'no','private'}:return ()
    oneway=tags.get('oneway')
    if oneway=='-1':return (-1,)
    if oneway in {'yes','1','true'}:return (1,)
    if oneway in {'no','0','false'}:return (1,-1)
    if tags.get('junction')=='roundabout' or tags.get('highway')=='motorway':return (1,)
    return (1,-1)

def shortest_path(graph,start,end):
    queue=[(0.0,start)];cost={start:0.0};previous={}
    while queue:
        distance,u=heapq.heappop(queue)
        if distance!=cost[u]:continue
        if u==end:
            path=[end]
            while path[-1]!=start:path.append(previous[path[-1]])
            return distance,list(reversed(path))
        for v,length in graph.get(u,[]):
            if length<0 or not math.isfinite(length):raise ValueError('Invalid edge length')
            candidate=distance+length
            if candidate<cost.get(v,math.inf):
                cost[v]=candidate;previous[v]=u;heapq.heappush(queue,(candidate,v))
    return None,[]
