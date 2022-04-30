
from math import radians, cos, sin, asin, sqrt
import urllib
import json

REPLICA_HOST = {
    'p5-http-a.5700.network': '50.116.41.109',
}
# mapping: domain name <-> [longitude, latitude]
REPLICA_IP_LOCATION = {
    "p5-http-a.5700.network": [-77.4874, 33.844],
    "p5-http-b.5700.network": [-122.0004, 37.5625],
    "p5-http-c.5700.network": [151.2006, -33.8715],
    "p5-http-d.5700.network": [8.6843, 50.1188],
    "p5-http-e.5700.network": [139.6899, 35.6893],
    "p5-http-f.5700.network": [-0.0955, 51.5095],
    "p5-http-g.5700.network": [72.8856, 19.0748],
}


def get_ip_geolocation(ip):
    # Use ip-api to get geolocation, try until success
    while True:
        try:
            response = urllib.urlopen('http://ip-api.com/json/' + ip)
            response_json = json.load(response)
            break
        except:
            continue
    return response_json['lon'], response_json['lat']


def get_physical_distance_to_client(client_ip):
    # get the client location
    client_long, client_lat = get_ip_geolocation(client_ip)
    replica_distance = []

    # use for loop to get each ec2 host's ip then cal the distance and put it into queue
    for host, coords in REPLICA_IP_LOCATION.values():
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
    distanceLong = destLong - srcLong
    distanceLat = destLong - srcLat

    a = sin(distanceLat / 2) ** 2 + cos(srcLat) * cos(destLat) * sin(distanceLong / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of earth in km
    r = 6371

    return c * r


MAX_NEAREST_REPLICAS_SELECTED = 1


def get_nearest_replicas(replica_distance):
    distance_tuple_list = sorted(replica_distance, key=lambda x: x[1])
    sorted_hosts = map(lambda x: x[0], distance_tuple_list)
    return sorted_hosts[0]
