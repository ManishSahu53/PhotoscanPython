""" Convex Hull Region of Interest """

import os
# import pexif
import shutil
import shapefile
import numpy as np
from src.exif import get_exif

def get_coordinates(points_list):
    """ Extract x and y point coordinates from
     a list of tuples.
    :param points_list: points as a list of tuples
    :return x and y point coordinates as separate lists
    """

    x = []
    y = []

    for ind in range(len(points_list)):
        x.append(points_list[ind][0])
        y.append(points_list[ind][1])

    return x, y


def convex_hull(points):
    """ Computation of a convex hull for a set of 2D points.
    :param points: sequence of (x, y) pairs representing
     the points.
    :return a list of vertices of the convex hull in
     counter-clockwise order, starting from the vertex with
     the lexicographically smallest coordinates.
    """
    # Sort the points lexicographically (tuples are compared
    # lexicographically).
    # Remove duplicates to detect the case we have just one
    # unique point.
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly
    # repeated multiple times.
    if len(points) <= 1:
        return points

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p)\
                <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) \
                <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives
    # the convex hull
    # The first point occurs in the list twice, since it's
    # at the same time the last point
    convex_hull_vertices = lower[:] + upper[:]
    return convex_hull_vertices


def cross(o, a, b):
    """ 2D cross product of OA and OB vectors,
     i.e. z-component of their 3D cross product.
    :param o: point O
    :param a: point A
    :param b: point B
    :return cross product of vectors OA and OB (OA x OB),
     positive if OAB makes a counter-clockwise turn,
     negative for clockwise turn, and zero
     if the points are colinear.
    """

    return (a[0] - o[0]) * (b[1] - o[1]) -\
           (a[1] - o[1]) * (b[0] - o[0])



def conv_hull(file, path_shp):
    sf = shapefile.Reader(path_shp)
    shp = sf.shapes()
    num_shp = len(shp)

    lat, long, ele = get_exif(file)
    # jpeg = pexif.JpegFile.fromFile(file)
    # cord = jpeg.get_geo()
    # lat = cord[0]
    # long = cord[1]
    inside = np.ones(num_shp)

    for k in range(0, num_shp):
        coord = shp[k].points
        coord = coord[:-1]
        hull_vertx = convex_hull(coord)

        for ind in range(1, len(hull_vertx)):
            res = cross(hull_vertx[ind-1],
                        hull_vertx[ind], (long, lat))
            # print 'cross res = ', res
            if res < 0:
                inside[k] = 0
                
        return inside
