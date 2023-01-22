"""
Some utilities for calculating geographic offsets
"""
import math
import geopy.distance


"""
Find the minimum radius needed to fully cover a square tile with the side length defined by tile_size
Use pythagorean theorem from centerpoint -> sqrt((side_length/2)^2 + (side_length/2)^2)
"""
def min_tile_radius(tile_size):
    return math.sqrt(2* (tile_size/2) * (tile_size/2))

def distance_between_lat_long(lat1, long1, lat2, long2):
    coords_1 = (lat1, long1)
    coords_2 = (lat2, long2)
    return geopy.distance.geodesic(coords_1, coords_2).km