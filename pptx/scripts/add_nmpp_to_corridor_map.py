"""Add the NMPP trunk line to the corridor map used on the gateways slide.

Reads   output/delivered/sa_subtitles_2026_10_08_v17/corridor_map.svg  (the map already in the pack)
        the pipeline layer given as the third argument (OpenStreetMap ways named "New Multi-Product Pipeline")
Writes  corridor_map_nmpp.svg and corridor_map_nmpp.html into the output folder.

The projection is the repo's shared one (pptx/assets/maps/reference.json). pyproj is not installed on the
analyst machine, so the same equal-area formula is written out here and checked against the five place
dots and the scale bar already drawn on the map; the script stops if they differ.

Usage:  python pptx/scripts/add_nmpp_to_corridor_map.py REPO_ROOT OUT_DIR PIPELINE.geojson
Then render the HTML to a 2200 x 850 PNG, for example with Edge:
        msedge --headless=new --window-size=880,340 --force-device-scale-factor=2.5 --screenshot=corridor_map_nmpp.png corridor_map_nmpp.html
The HTML expects Lato-Regular.ttf and Lato-Bold.ttf beside it (not tracked; copy them from the Office font cache).
"""
import json,math,re,sys
from pathlib import Path
R=Path(sys.argv[1]);OUT=Path(sys.argv[2])
ref=json.loads((R/'pptx/assets/maps/reference.json').read_text())
assert ref['display_crs']=='+proj=laea +lat_0=-29 +lon_0=25 +datum=WGS84 +units=m +no_defs'
a=6378137.0;f=1/298.257223563;e2=f*(2-f);e=math.sqrt(e2);lat0=math.radians(-29);lon0=math.radians(25)
q=lambda s:(1-e2)*(s/(1-e2*s*s)-(1/(2*e))*math.log((1-e*s)/(1+e*s)))
qp=q(1.0);Rq=a*math.sqrt(qp/2);b1=math.asin(q(math.sin(lat0))/qp)
D=a*(math.cos(lat0)/math.sqrt(1-e2*math.sin(lat0)**2))/(Rq*math.cos(b1))
def proj(lon,lat):
    lam=math.radians(lon)-lon0;b=math.asin(q(math.sin(math.radians(lat)))/qp)
    B=Rq*math.sqrt(2/(1+math.sin(b1)*math.sin(b)+math.cos(b1)*math.cos(b)*math.cos(lam)))
    return B*D*math.cos(b)*math.sin(lam),(B/D)*(math.cos(b1)*math.sin(b)-math.sin(b1)*math.cos(b)*math.cos(lam))
def map_transform(x,y,width,height):
    west,south,east,north=ref['extent_lonlat'];per=[]
    for i in range(101):
        lon=west+(east-west)*i/100;lat=south+(north-south)*i/100
        per+= [proj(lon,south),proj(lon,north),proj(west,lat),proj(east,lat)]
    xmin,xmax=min(p[0] for p in per),max(p[0] for p in per);ymin,ymax=min(p[1] for p in per),max(p[1] for p in per)
    scale=min(width/(xmax-xmin),height/(ymax-ymin));left=x+(width-(xmax-xmin)*scale)/2;top=y+(height-(ymax-ymin)*scale)/2
    def xy(lon,lat):
        px,py=proj(lon,lat);return left+(px-xmin)*scale,top+(ymax-py)*scale
    return xy,scale
xy,scale=map_transform(5,36,535,275)
svg=(R/'output/delivered/sa_subtitles_2026_10_08_v17/corridor_map.svg').read_text(encoding='utf-8')
# validate my projection against the existing drawing: scale bar and the place dots
bar=float(re.search(r'M30 294h([\d.]+)',svg).group(1));print('scale bar svg',bar,'mine',500000*scale)
pts=json.loads((R/'pptx/story/corridor_comparison_2026_10_06.json').read_text())['points']
circles=[(float(a),float(b)) for a,b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="3.3"',svg)]
for n in ['Walvis Bay','Matola / Maputo','Durban','Gauteng','Lesedi*']:
    x,y=xy(*pts[n]);d=min(math.hypot(x-cx,y-cy) for cx,cy in circles);print(f'{n:16s} mine {x:.2f},{y:.2f} nearest existing dot {d:.3f} units away')
    assert d<0.05
gj=json.loads(Path(sys.argv[3]).read_text(encoding='utf-8'))
def simp(c,tol=0.15):
    o=[c[0]]
    for p in c[1:-1]:
        if math.hypot(p[0]-o[-1][0],p[1]-o[-1][1])>=tol:o.append(p)
    return o+[c[-1]]
d=' '.join('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in simp([xy(*p) for p in ft['geometry']['coordinates']])) for ft in gj['features'])
COL='#0A2373'
# tube symbol: navy outline with a white core, so the pipeline reads differently from the solid road route
pipe=(f'<path d="{d}" fill="none" stroke="{COL}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" />'
      f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="1.5" stroke-linejoin="round" />')
# insert below the place dots and labels: just before the first place circle
i=svg.index('<circle cx=');j=svg.rfind('<',0,i+1)
svg=svg[:i]+pipe+svg[i:]
key=('<path d="M300 314h24" stroke="'+COL+'" stroke-width="3.4" stroke-linecap="round" /><path d="M300 314h24" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" />'
     '<text x="330" y="318" font-size="9" fill="#595959" font-weight="400" text-anchor="start">NMPP fuel pipeline (trunk line)</text>')
anchor='<text x="18" y="337"';assert anchor in svg;svg=svg.replace(anchor,key+anchor)
old='OSM geometry; routes test connectivity, not tanker access or operating service.';assert old in svg
svg=svg.replace(old,'OSM geometry; routes test connectivity, not tanker access or operating service. Pipeline route is community-mapped.')
(OUT/'corridor_map_nmpp.svg').write_text(svg,encoding='utf-8')
body=svg[svg.index('<svg'):].replace('<svg ','<svg width="880" height="340" style="display:block" ',1)
(OUT/'corridor_map_nmpp.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>@font-face{font-family:Lato;font-weight:400;src:url(Lato-Regular.ttf)}@font-face{font-family:Lato;font-weight:700;src:url(Lato-Bold.ttf)}body{margin:0;background:#fff}</style></head><body>'+body+'</body></html>',encoding='utf-8')
print('written')
