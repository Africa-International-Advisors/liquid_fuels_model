"""Check the illustrative map's distance logic and unknown-area treatment."""
from pathlib import Path
import sys
import pytest
pytest.importorskip('shapely',reason='Presentation map checks require pptx/requirements.txt')
from shapely.geometry import box
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pptx/scripts'))
from accessibility_cartography import distance_surface

class IdentityProjection:
    def transform(self,x,y):
        return x,y

SETTINGS={
 'grid_cell_km':30,'cost_class_upper_zar_per_litre':[.75,1.25,1.75,2.25],
 'maximum_straight_line_connection_km':100,
 'illustrative_dispatch_zar_per_litre':.15,
 'illustrative_transport_zar_per_litre_km':.002,
}

def test_cost_follows_network_detour_instead_of_straight_line():
    country=box(285000,285000,315000,315000)
    cells=distance_surface({'U':[(0,0),(0,300000),(300000,300000)]},
        IdentityProjection(),country,SETTINGS,{'Terminal':(0,0)})
    assert cells
    # The route detour produces roughly R1.35/L, above the straight-line class.
    assert all(category==2 for _,category,_ in cells)
    assert all(country.covers(geometry) for geometry,_,_ in cells)

def test_distant_areas_stay_unassessed():
    cells=distance_surface({'road':[(0,0),(300000,0)]},IdentityProjection(),
        box(900000,900000,930000,930000),SETTINGS,{'Terminal':(0,0)})
    assert cells and all(category is None and origin is None for _,category,origin in cells)

def test_lower_cost_terminal_is_selected():
    cells=distance_surface({'road':[(0,0),(600000,0)]},IdentityProjection(),
        box(570000,0,600000,30000),SETTINGS,{'Far':(0,0),'Near':(600000,0)})
    assert cells and all(origin=='Near' and category==0 for _,category,origin in cells)
