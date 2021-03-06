import socket
import time
from math import radians, cos, sin, asin, sqrt
import urllib.request
import json

REPLICA_1 = 'p5-http-a.5700.network'
REPLICA_2 = 'p5-http-b.5700.network'
REPLICA_3 = 'p5-http-c.5700.network'
REPLICA_4 = 'p5-http-d.5700.network'
REPLICA_5 = 'p5-http-e.5700.network'
REPLICA_6 = 'p5-http-f.5700.network'
REPLICA_7 = 'p5-http-g.5700.network'

REPLICA_HOST = {
    REPLICA_1: socket.gethostbyname(REPLICA_1),  # 50.116.41.109
    REPLICA_2: socket.gethostbyname(REPLICA_2),  # 45.33.50.187
    REPLICA_3: socket.gethostbyname(REPLICA_3),  # 194.195.121.150
    REPLICA_4: socket.gethostbyname(REPLICA_4),  # 172.104.144.157
    REPLICA_5: socket.gethostbyname(REPLICA_5),  # 172.104.110.211
    REPLICA_6: socket.gethostbyname(REPLICA_6),  # 88.80.186.80
    REPLICA_7: socket.gethostbyname(REPLICA_7),  # 172.105.55.115
}


def convert(ip):
    lon, lat = get_ip_geolocation(ip)
    return [float(lon), float(lat)]


def get_ip_geolocation(ip):
    # Use ip-api to get geolocation, try until success
    while True:
        try:
            response = urllib.request.urlopen('http://ip-api.com/json/' + ip)
            response_json = json.load(response)
            break
        except:
            continue
    return response_json['lon'], response_json['lat']


# mapping: domain name <-> [longitude, latitude]
REPLICA_IP_LOCATION = {
    REPLICA_1: convert(REPLICA_1),  # Atlanta
    REPLICA_2: convert(REPLICA_2),  # Fremont/LA
    REPLICA_3: convert(REPLICA_3),  # Sydney
    REPLICA_4: convert(REPLICA_4),  # Frankfurt/Germany
    REPLICA_5: convert(REPLICA_5),  # Tokyo
    REPLICA_6: convert(REPLICA_6),  # London
    REPLICA_7: convert(REPLICA_7),  # India
}


ip_cache = {}


def get_physical_distance_to_client(client_ip):
    # get the client location
    client_long, client_lat = get_ip_geolocation(client_ip)
    replica_distance = []

    # use for loop to get each ec2 host's ip then cal the distance and put it into queue
    for host, coords in REPLICA_IP_LOCATION.items():
        dest_long = coords[0]
        dest_lat = coords[1]
        dis = get_distance(client_lat, dest_lat, client_long, dest_long)
        replica_distance.append((host, dis))

    return replica_distance


def get_distance(srcLat, destLat, srcLong, destLong):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    srcLong = radians(srcLong)
    destLong = radians(destLong)
    srcLat = radians(srcLat)
    destLat = radians(destLat)

    # Haversine formula
    # Reference: https://www.geeksforgeeks.org/program-distance-two-points-earth/#:~:text=For%20this%20divide%20the%20values,is%20the%20radius%20of%20Earth.
    distanceLong = radians(destLong - srcLong)
    distanceLat = radians(destLat - srcLat)

    a = sin(distanceLat / 2) ** 2 + cos(srcLat) * cos(destLat) * sin(distanceLong / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of earth in km
    r = 6371

    return c * r


EXPIRY = 60 * 5


def get_nearest_replica(client_ip):
    current_time = int(time.time())
    if client_ip in ip_cache.keys() and ip_cache[client_ip][1] >= current_time - EXPIRY:
        return ip_cache[client_ip][0]
    replica_distance = get_physical_distance_to_client(client_ip)
    distance_tuple_list = sorted(replica_distance, key=lambda x: x[1])
    nearest_ip = REPLICA_HOST[distance_tuple_list[0][0]]
    ip_cache[client_ip] = (nearest_ip, int(time.time()))
    return nearest_ip
