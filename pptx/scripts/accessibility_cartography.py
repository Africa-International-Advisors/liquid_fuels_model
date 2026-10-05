"""Illustrative map classification from schematic geometry; no fuel-model results.

This is a cartographic cost illustration, using authored rates without quoted
cost, operational capacity or customer-access claims. All settings live in story.
"""
import heapq
import math
from shapely.geometry import box

def distance_surface(roads, project, country, settings, origins=None):
    adjacency={}
    edges=[]
    for route in roads.values():
        points=[project.transform(*p) for p in route]
        for a,b in zip(points,points[1:]):
            length=math.dist(a,b)
            if not length:
                continue
            adjacency.setdefault(a,[]).append((b,length))
            adjacency.setdefault(b,[]).append((a,length))
            edges.append((a,b,length))
    def connection(point,edge):
        a,b,length=edge
        fraction=max(0,min(1,((point[0]-a[0])*(b[0]-a[0])+(point[1]-a[1])*(b[1]-a[1]))/length**2))
        nearest=(a[0]+fraction*(b[0]-a[0]),a[1]+fraction*(b[1]-a[1]))
        return math.dist(point,nearest),fraction*length
    origins=origins or {'Durban':(31.03,-29.88),'Lesedi':(28.39,-26.44)}
    distances={}
    for name,lonlat in origins.items():
        origin=project.transform(*lonlat)
        edge=min(edges,key=lambda e:connection(origin,e)[0])
        off,along=connection(origin,edge)
        a,b,length=edge
        best={a:off+along,b:off+length-along}
        queue=[(value,node) for node,value in best.items()]
        heapq.heapify(queue)
        while queue:
            value,node=heapq.heappop(queue)
            if value>best[node]:
                continue
            for other,length in adjacency[node]:
                proposal=value+length
                if proposal<best.get(other,math.inf):
                    best[other]=proposal
                    heapq.heappush(queue,(proposal,other))
        distances[name]=best
    cell=settings['grid_cell_km']*1000
    upper=settings['cost_class_upper_zar_per_litre']
    limit=settings['maximum_straight_line_connection_km']*1000
    xmin,ymin,xmax,ymax=country.bounds
    results=[]
    for ix in range(math.floor(xmin/cell),math.ceil(xmax/cell)):
        for iy in range(math.floor(ymin/cell),math.ceil(ymax/cell)):
            tile=box(ix*cell,iy*cell,(ix+1)*cell,(iy+1)*cell)
            if not country.intersects(tile):
                continue
            tile=tile.intersection(country)
            point=((ix+.5)*cell,(iy+.5)*cell)
            connections=[connection(point,e) for e in edges]
            nearest=min(c[0] for c in connections)
            if nearest>limit:
                results.append((tile,None,None))
                continue
            totals={}
            for name,best in distances.items():
                values=[off+min(best.get(a,math.inf)+along,best.get(b,math.inf)+length-along)
                    for (a,b,length),(off,along) in zip(edges,connections) if off<=limit]
                totals[name]=min(values,default=math.inf)
            name=min(totals,key=totals.get)
            distance=totals[name]
            if not math.isfinite(distance):
                results.append((tile,None,None))
                continue
            score=settings['illustrative_dispatch_zar_per_litre']+distance/1000*settings['illustrative_transport_zar_per_litre_km']
            category=next((i for i,threshold in enumerate(upper) if score<=threshold),len(upper))
            results.append((tile,category,name))
    return results
