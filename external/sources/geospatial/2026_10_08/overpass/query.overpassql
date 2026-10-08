[out:json][timeout:180];(
way[highway~"^(motorway|trunk|primary|secondary)(_link)?$"](-35.5,12.5,-20,34);
way[railway=rail](-35.5,12.5,-20,34);way[man_made=pipeline](-35.5,12.5,-20,34);
relation[type=restriction](-35.5,12.5,-20,34);
nwr[name~"Vopak|Natref|Secunda",i](-35.5,12.5,-20,34);
node[barrier=border_control](-35.5,12.5,-20,34););out body geom;