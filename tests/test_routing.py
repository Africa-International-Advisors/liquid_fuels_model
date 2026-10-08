from lfm.model.core.routing import directions,shortest_path

def test_direction_and_access():
    assert directions({'oneway':'-1'})==(-1,)
    assert directions({'junction':'roundabout'})==(1,)
    assert directions({'access':'private'})==()
    assert directions({'access':'no','motor_vehicle':'yes'})==(1,-1)

def test_shortest_path_and_disconnected():
    graph={1:[(2,9),(3,2)],3:[(2,2)],2:[(4,1)]}
    assert shortest_path(graph,1,4)==(5,[1,3,2,4])
    assert shortest_path(graph,4,1)==(None,[])

def test_crossing_without_shared_node_is_not_junction():
    assert shortest_path({1:[(2,1)],3:[(4,1)]},1,4)==(None,[])
