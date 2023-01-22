"""
Scrape and manage tiles (150m^2) from Google Maps platform API
"""

import requests
import json
import sqlite3
from math import trunc

FIXED_LAT_BOTTOM_RIGHT = 49.200496204642555
FIXED_LONG_BOTTOM_RIGHT = -123.02330267191682

# APPROXIMATE tile sized lat/long offsets -> TODO: make these more accurate
ONE_M_LAT = 0.000009
ONE_M_LONG = 0.00015

LAT_PER_TILE = 0.00135
LONG_PER_TILE = 0.00225

FRAME_SIZE_LAT_M = 10000
FRAME_SIZE_LONG_M = 15000

NUM_TILES_PER_COL = 67
NUM_TILES_PER_ROW = 100

TILE_SIZE_M = 150

TOTAL_NUMBER_TILES = 6700

TILE_DATABASE = "tiles.db"
RESTAURANT_DATABASE = "restaurant.db"
API_KEY_FILE = "secret_api_key.txt"

class Tile:
    def __init__(self, ref_lat, ref_long, valid, tilenum):
        self.ref_lat = ref_lat
        self.ref_long = ref_long
        self.refresh = valid
        self.tilenum = tilenum


class TileManager:
    def __init__(self, api_key_file_loc, tile_db, restaurant_db):
        f = open(api_key_file_loc, "r")
        self.key = f.read()
        self.tile_db = tile_db
        self.restaurant_db = restaurant_db

        # mount and generate the tile refresh database if needed
        conn = sqlite3.connect(tile_db)
        # if tile entries are not found in the db, create them
        listOfTables = conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='TILES'; """).fetchall()
        # create entry if it does not exist
        if listOfTables == []:
            conn.execute("""CREATE TABLE TILES(
                TILE_NUM INT,
                TILE_REF_LAT real,
                TILE_REF_LONG real,
                VALID VARCHAR(255),
                TIME_RETRIEVED VARCHAR(255));""")
            # generate the tile space in frame
            gen_tile_space(conn)
            conn.commit()
            conn.close()

        # initialize the restaurant database
        conn = sqlite3.connect(restaurant_db)
        listOfTables = conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='RESTAURANTS'; """).fetchall()
        # check if database has been initialized
        if listOfTables == []:
            conn.execute("""CREATE TABLE RESTAURANTS(
                NAME VARCHAR(255),
                PLACEID VARCHAR(255),
                USER_RATING real,
                ADDRESS VARCHAR(255),
                PRICE VARCHAR(255),
                TOTAL_USER_RATINGS REAL,
                RECOMMENDS INT);""")
            conn.commit()
            conn.close()
    
    """
    Get tile info by number
    """
    def get_tile_by_number(self, number):
        conn = sqlite3.connect(self.tile_db)
        cursor = conn.execute("SELECT TILE_NUM,TILE_REF_LAT,TILE_REF_LONG,VALID,TIME_RETRIEVED from TILES")
        for row in cursor:
            if row[0] == number:
                newtile = Tile(row[1], row[2], row[3], row[0])
                return newtile
        conn.close()

    """
    Get the tile number of any lat/long coordinates
    """
    def get_tile_number_from_lat_long(self, lat, long):
        delta_lat = lat - FIXED_LAT_BOTTOM_RIGHT
        delta_long = FIXED_LONG_BOTTOM_RIGHT - long
        row_num = trunc(delta_lat / LAT_PER_TILE)
        col_num = trunc(delta_long / LONG_PER_TILE)
        if (row_num >= 0 and row_num <= 100 and col_num >= 0 and col_num <= 67):
            return row_num + col_num * 67
        else:
            return -1

    """
    Gets chunk of tiles in a specific radius
    """
    def get_tile_chunk(self, lat, long, radius):
        own_tile = self.get_tile_number_from_lat_long(lat, long)
        tile_list = [own_tile]

        radius_tiles = round((radius - (TILE_SIZE_M / 2)) / (TILE_SIZE_M))
        south_b = own_tile
        west_b = own_tile
        north_b = own_tile
        east_b = own_tile

        # find "southmost tiles"
        for y in range(radius_tiles):
            tile = own_tile - y
            if (tile) >= 0 and (tile) <= NUM_TILES_PER_COL:
                tile_list.append(tile)
                south_b = tile
            else:
                # found boundary
                break

        # find "northmost tiles"
        for y in range(radius_tiles):
            tile = own_tile + y
            if (tile) >= 0 and (tile) <= NUM_TILES_PER_COL:
                tile_list.append(tile)
                north_b = tile
            else:
                # found boundary
                break

        # find "west tiles"
        for y in range(radius_tiles):
            tile = own_tile + y*NUM_TILES_PER_COL
            if (tile) >= 0 and (tile) <= TOTAL_NUMBER_TILES:
                tile_list.append(tile)
                west_b = tile
            else:
                # found boundary
                break

        # find "east tiles"
        for y in range(radius_tiles):
            tile = own_tile - y*NUM_TILES_PER_COL
            if (tile) >= 0 and (tile) <= TOTAL_NUMBER_TILES:
                tile_list.append(tile)
                east_b = tile
            else:
                # found boundary
                break

        # TODO: find a better way to generate inner portions of chunk -> This just works for 500 meter radius
        if (east_b < own_tile and south_b < own_tile):
            tile_list.append(own_tile - NUM_TILES_PER_COL - 1)

        if (north_b > own_tile and east_b < own_tile):
            tile_list.append(own_tile - NUM_TILES_PER_COL + 1)

        if (west_b > own_tile and south_b < own_tile):
            tile_list.append(own_tile + NUM_TILES_PER_COL - 1)

        if (west_b > own_tile and north_b > own_tile):
            tile_list.append(own_tile + NUM_TILES_PER_COL + 1)

        # drop duplicates
        tile_list = list(dict.fromkeys(tile_list))
        return tile_list


# private
def gen_tile_space(conn):
    # create tile space from empty table
    tile_num = 0
    for x in range(NUM_TILES_PER_ROW):
        for y in range(NUM_TILES_PER_COL):
            # referance point for any tile is the bottom right hand corner
            ref_lat = y*LAT_PER_TILE + FIXED_LAT_BOTTOM_RIGHT
            ref_long = FIXED_LONG_BOTTOM_RIGHT - x*LONG_PER_TILE
            vals_string = "(" + str(tile_num) + ", " + str(ref_lat) + ", " + str(ref_long) + ", False, 0)" 
            conn.execute("INSERT INTO TILES (TILE_NUM,TILE_REF_LAT,TILE_REF_LONG,VALID,TIME_RETRIEVED) \
                            VALUES" + vals_string)
            tile_num +=1


# public
def find_tile_number_for_point():
    pass

def get_tile_data():
    pass
    
