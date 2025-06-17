import math

# In Mercator projection the scale factor is changed along the meridians as a function of latitude
# to keep the scale factor equal in all direction: k=sec(latitude)
# scale coefficient = 1.0 / math.cos(math.radians(55.69))
# To get it from PostgreSQL we use query:
QUERY_COEF = "1.0/cos(radians(ST_Y(ST_AsText(ST_Transform(ST_Centroid(geometry), 4326)))))"

NEIGHBOURS_DIST_M = 200.0
INFRASTRUCTURE_DIST_M = 1000.0
# Radius in meters around point.
ECOLOGY_R_M = 2000.0
ECOLOGY_LINE_SEGMENT_LEN_M = 10.0

# Hexagon edge or outer radius in meters:
HEX_R = 100

