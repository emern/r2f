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
        self.valid = valid
        self.tilenum = tilenum

class Restaurant:
    def __init__(self, lat, long, address, tilenum, categories, name, price, score, placeid, total_ratings, recommends):
        self.ref_lat = lat
        self.ref_long = long
        self.address = address
        self.tilenum = tilenum
        self.categories = categories
        self.name = name
        self.price = price
        self.score = score
        self.placeid = placeid
        self.total_ratings = total_ratings
        self.recommends = recommends

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
                CATEGORIES VARCHAR(255),
                TOTAL_USER_RATINGS REAL,
                LAT REAL,
                LONG REAL,
                RECOMMENDS INT,
                TILENUM INT,
                UNIQUE(PLACEID));""")
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
    Update restaurant by placeid
    """
    def update_restaurant_recommends_by_placeid(self, placeid):
        conn = sqlite3.connect(self.restaurant_db)
        conn.execute("UPDATE RESTAURANTS set RECOMMENDS = RECOMMENDS + 1 where PLACEID = '" + str(placeid) + "'")
        conn.commit()
        conn.close()

    """
    Update a tiles data by inserting new restaurant entries - takes array of Restaurants
    """
    def update_tile_data(self, number, data):
        # first update internal tile record
        conn = sqlite3.connect(self.tile_db)
        conn.execute("UPDATE TILES set VALID = 1 where TILE_NUM = " + str(number))
        conn.commit()
        conn.close()
        # second update restaurant database data
        for entry in range(len(data)):
            conn = sqlite3.connect(self.restaurant_db)
            cursor = conn.cursor()

            insert_entry = "INSERT OR IGNORE INTO RESTAURANTS (NAME,PLACEID,USER_RATING,ADDRESS,PRICE,CATEGORIES,TOTAL_USER_RATINGS,LAT,LONG,RECOMMENDS,TILENUM)\
                VALUES (?,?,?,?,?,?,?,?,?,?,?)"

            insert_entry_data = (data[entry].name,
                                data[entry].placeid,
                                data[entry].score,
                                data[entry].address,
                                data[entry].price,
                                str(data[entry].categories),
                                data[entry].total_ratings,
                                data[entry].ref_lat,
                                data[entry].ref_long,
                                data[entry].recommends,
                                self.get_tile_number_from_lat_long(data[entry].ref_lat, data[entry].ref_long))

            cursor.execute(insert_entry, insert_entry_data)
            conn.commit()
            cursor.close()
            conn.close()

    """
    Get all restaurants within a specific tile
    """
    def get_restaurant_data_from_tile(self, tilenum):
        tile_rs = []
        conn = sqlite3.connect(self.restaurant_db)
        cursor = conn.execute("SELECT NAME,PLACEID,USER_RATING,ADDRESS,PRICE,CATEGORIES,TOTAL_USER_RATINGS,LAT,LONG,RECOMMENDS,TILENUM FROM RESTAURANTS WHERE TILENUM = " + str(tilenum))
        for row in cursor:
            new_r = Restaurant(lat=row[7],
                                name=row[0],
                                address=row[3],
                                long=row[8],
                                tilenum=row[10],
                                categories=row[5],
                                price=row[4],
                                score=row[2],
                                placeid=row[1],
                                total_ratings=row[6],
                                recommends=row[9])
            tile_rs.append(new_r)
        cursor.close()
        conn.close()
        return tile_rs

    """
    Return list of restaurants based on name search (lowercase characters matched)
    """
    def search_for_restaurants_by_name(self, search_string):
        found_rs = []
        conn = sqlite3.connect(self.restaurant_db)
        cursor = conn.execute("SELECT NAME,PLACEID,USER_RATING,ADDRESS,PRICE,CATEGORIES,TOTAL_USER_RATINGS,LAT,LONG,RECOMMENDS,TILENUM from RESTAURANTS")
        for row in cursor:
            if (search_string.lower() in row[0].lower()):
                new_r = Restaurant(lat=row[7],
                                    name=row[0],
                                    address=row[3],
                                    long=row[8],
                                    tilenum=row[10],
                                    categories=row[5],
                                    price=row[4],
                                    score=row[2],
                                    placeid=row[1],
                                    total_ratings=row[6],
                                    recommends=row[9])
                found_rs.append(new_r)
        cursor.close()
        conn.close()
        return found_rs

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
    Gets chunk of tiles in a specific radius ->
    This tile chunk system only works for 500m and below chunks and will need to be improved in future
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

    """
    get the top results in some radius
    """
    def get_top_results_in_radius(self, lat, long, num_results, radius):
        # get and parse tiles
        tiles = self.get_tile_chunk(lat, long, radius)
        print("getting top " + str(num_results) + " for tiles " + str(tiles))
        all_restaurants = []
        if len(tiles) < 10: # safety measure for now to not ruin my API access lol
            for tile in tiles:
                # collect tile
                tile_info = self.get_tile_by_number(tile)
                # update the tiles record if it is old
                if (tile_info.valid == "0"):
                    print("updating tile " + str(tile))
                    adjusted_lat = tile_info.ref_lat + LAT_PER_TILE/2
                    adjusted_long = tile_info.ref_long - LONG_PER_TILE/2
                    data = self.__google_places_nearby_search_api_call(radius, adjusted_lat, adjusted_long)
                    self.update_tile_data(tile, data)
                all_restaurants.extend(self.get_restaurant_data_from_tile(tile))
        # Score by popularity (because that is the idea of the app), however if the quality score is very low we scale a restaurants placement down
        # In-app recommends are worth 1000 regular Google ratings (will changle later)
        all_restaurants.sort(key=lambda x: (x.total_ratings + (1000*x.recommends) if (x.score > 3.5) else (x.total_ratings * 0.6)), reverse=True)
        return all_restaurants[:num_results]
                
    def __google_places_nearby_search_api_call(self, radius, lat, long):

        # build api query
        lat_long = str(lat) + "%2C" + str(long)
        keyword = "restaurant"
        radius = str(radius)
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + lat_long + "&radius=" + radius + "&keyword=" + keyword + "&key=" + self.key
        payload={}
        headers = {}
        print("sending places api query " + url)
        response = requests.request("GET", url, headers=headers, data=payload)
        PLAIN_TEXT_FILE = open("temp.json", "w", encoding="utf-8")
        PLAIN_TEXT_FILE.writelines(response.text)
        PLAIN_TEXT_FILE.close()
      
        IN_FILE = open("temp.json", "r", encoding="utf-8")
        data = json.load(IN_FILE)

        # hold frame data in order
        frame_data = []

        for i in data["results"]:
            name = i["name"]
            rating = i["rating"]
            types = i["types"]
            lat = i["geometry"]["location"]["lat"]
            long = i["geometry"]["location"]["lng"]
            addr = i["vicinity"]
            place_id = i["place_id"]
            user_ratings_total = i["user_ratings_total"]
            try:
                price = i["price_level"]
            except:
                price = -1
            # produce new restaurant, 0 recommends by default
            new_establishment = Restaurant(lat=lat,
                                            name=name,
                                            address=addr,
                                            long=long,
                                            tilenum=self.get_tile_number_from_lat_long(lat, long),
                                            categories=types,
                                            price=price,
                                            score=rating,
                                            placeid=place_id,
                                            total_ratings=user_ratings_total,
                                            recommends=0)
            frame_data.append(new_establishment)

        return frame_data


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

