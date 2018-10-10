import os
import ntpath
import tkinter.messagebox as messagebox
import logging
import sys
import math
import utm
import PhotoScan
import json
import csv

def get_logger(name):
    return logging.getLogger(name)

def tocsv(dictA, file_csv):
    with open(file_csv,'wb') as f:
        w = csv.writer(f)
        w.writerows(dictA.items())


def tojson(dictA, file_json):
    with open(file_json, 'w') as f:
        json.dump(dictA, f, indent=4, separators=(',', ': '),
                  ensure_ascii=False)


def listdir_fullpath(d):  # list all directories
    return [os.path.join(d, f) for f in os.listdir(d)]


def path_leaf(path):  # Get base name
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def UTM_EPSG(zone_no):  # Zone number to EPSG code
    epsg_code = 'EPSG::326' + str(zone_no)
    return epsg_code


def get_epsg(lat, long):  # Lat long to EPSG
    projected = utm.from_latlon(lat, long)
    zone_no = projected[2]
    epsg_code = UTM_EPSG(zone_no)
    return epsg_code


def booldialogbox(message):  # Yes No Dialog box
    result = messagebox.askquestion(
        'Provide you input', message, icon='warning')
    if result == 'yes':
        return 1
    else:
        return 0


def create_dir(path):  # Creating directories
    if not os.path.exists(path):
        os.makedirs(path)


def log2file(project_path, project_name):  # Loggging to file
    # set up logging to file
    logging.basicConfig(
        filename=os.path.join(project_path, project_name + "_log.txt"),
        level=logging.DEBUG,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger(__name__)


def get_quality(chunk, force=False):  # Estimate image quality
    quality = []
    chunk.estimateImageQuality(chunk.cameras)
    for camera in chunk.cameras:
        quality.append(float(camera.photo.meta["Image/Quality"]))
    return quality


def get_reprojection_error(chunk):  # Return reprojection error

    cameras = chunk.cameras
    point_cloud = chunk.point_cloud
    points = point_cloud.points
    projections_per_camera = point_cloud.projections
    tracks = point_cloud.tracks
    point_squared_errors = [[] for i in range(len(points))]
    point_key_point_size = [[] for i in range(len(points))]
    track_cameras = [[] for i in range(len(tracks))]
    track_projections = [[] for i in range(len(tracks))]

    for camera_id, camera in enumerate(cameras):
        if camera not in projections_per_camera:
            continue

        projections = projections_per_camera[camera]
        for projection_id, projection in enumerate(projections):
            track_id = projection.track_id
            track_cameras[track_id].append(camera_id)
            track_projections[track_id].append(projection_id)

    for i, point in enumerate(points):
        if point.valid is False:
            continue

        track_id = point.track_id

        for idx in range(len(track_cameras[track_id])):
            camera_id = track_cameras[track_id][idx]
            projection_id = track_projections[track_id][idx]
            camera = cameras[camera_id]
            projections = projections_per_camera[camera]
            projection = projections[projection_id]
            key_point_size = projection.size
            error = camera.error(
                point.coord, projection.coord) / key_point_size
            point_squared_errors[i].append(error.norm() ** 2)
            point_key_point_size[i].append(key_point_size)

    total_squared_error = sum([sum(el) for el in point_squared_errors])
    total_errors = sum([len(el) for el in point_squared_errors])
    max_squared_error = max([max(el+[0])
                             for i, el in enumerate(point_squared_errors)])
    rms_reprojection_error = math.sqrt(total_squared_error/total_errors)
    max_reprojection_error = math.sqrt(max_squared_error)
    max_reprojection_errors = [math.sqrt(max(el+[0]))
                               for el in point_squared_errors]

    return rms_reprojection_error, max_reprojection_error, max_reprojection_errors


def get_key_point_size(chunk):

    cameras = chunk.cameras
    point_cloud = chunk.point_cloud
    points = point_cloud.points
    projections_per_camera = point_cloud.projections
    tracks = point_cloud.tracks
    key_point_size = [[] for i in range(len(points))]
    point_tracks = [None for i in range(len(tracks))]

    for i, point in enumerate(points):
        track_id = point.track_id
        point_tracks[track_id] = i

    for camera in cameras:
        if camera not in projections_per_camera:
            continue

        projections = projections_per_camera[camera]

        for projection in projections:
            track_id = projection.track_id
            point_id = point_tracks[track_id]

            if point_id is not None and points[point_id].valid is True:
                key_point_size[point_id].append(projection.size)

    total_key_point_size = sum([sum(el) for el in key_point_size])
    total_key_points = sum([len(el) for el in key_point_size])
    mean_key_point_size = total_key_point_size / total_key_points
    mean_key_point_sizes = [sum(el)/len(el) for el in key_point_size]

    return mean_key_point_size, key_point_size, mean_key_point_sizes


def get_overlap(chunk, only_points=False):

    cameras = chunk.cameras
    point_cloud = chunk.point_cloud
    points = point_cloud.points
    projections_per_camera = point_cloud.projections
    tracks = point_cloud.tracks
    track_idx = []

    if only_points is False:
        overlap = [0 for i in range(len(tracks))]

        for camera in cameras:
            if camera not in projections_per_camera:
                continue

            projections = projections_per_camera[camera]

            for projection in projections:
                track_id = projection.track_id
                overlap[track_id] += 1

    else:
        overlap = [0 for i in range(len(points))]
        point_tracks = [None for i in range(len(tracks))]

        for i, point in enumerate(points):
            track_id = point.track_id
            point_tracks[track_id] = i

        for camera in cameras:
            if camera not in projections_per_camera:
                continue

            projections = projections_per_camera[camera]

            for projection in projections:
                track_id = projection.track_id
                point_id = point_tracks[track_id]

                if point_id is not None and points[point_id].valid is True:
                    overlap[point_id] += 1

    effective_overlap = sum(overlap) / len(overlap)

    return effective_overlap, overlap


def show_points_info(chunk, only_points=False, verbose=False):

    rre, mre, mres = get_reprojection_error(chunk)
    mkps, kps, mkpss = get_key_point_size(chunk)
    eo, o = get_overlap(chunk, only_points=only_points)

    point_cloud = chunk.point_cloud
    points = point_cloud.points
    tracks = point_cloud.tracks

    npoints = len([True for point in points if point.valid is True])
    ntracks = len(tracks)

    width = 30
    print('-------------------------------------------------')
    print('Points'.ljust(width), '{:,}'.format(npoints),
          'of', '{:,}'.format(ntracks))
    print('RMS reprojection error'.ljust(width), '{:6g}'.format(rre))
    print('Max reprojection error'.ljust(width), '{:6g}'.format(mre))
    print('Mean key point size'.ljust(width), '{:6g}'.format(mkps), 'pix')
    print('Effective overlap'.ljust(width), '{:6g}'.format(eo))
    print('-------------------------------------------------')
