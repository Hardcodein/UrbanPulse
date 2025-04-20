QUERY_COEF = "1.0/cos(radians(ST_Y(ST_AsText(ST_Transform(ST_Centroid(geometry), 4326)))))"

NEIGHBOURS_DIST_METERES = 200.0
INFRASTRUCTURE_DIST_METERES = 1000.0
# Radius in meters around point.
ECOLOGY_R_METERES = 2000.0

ECOLOGY_LINE_SEGMENT_LEN_METERS = 10.0

# Hexagon edge or outer radius in meters:
HEX_R = 100