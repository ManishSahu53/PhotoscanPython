import PhotoScan
import os
import sys
import shapefile
from tkinter import filedialog
from tkinter import *
import tkinter.messagebox as messagebox
import ntpath
# import gdal
import shutil
import argparse
from src import defaults as dft
from src import general as gn
# from src import exif as exf
from src import convhull as cvh
from src import map_plotly as mapplot
from collections import defaultdict
import argparse
import numpy as np
import time
import csv

logger = gn.get_logger('Processing')
# Started timing
st_time = time.time()

parser = argparse.ArgumentParser(
    'This is used to run Agisoft"s photogrammetric processing. Output will be in UTM format only')

parser.add_argument('-or', '--ortho', help='Process and output orthomosaic',
                    required=False, default=1,  type=int)
parser.add_argument('-dsm', '--dsmodel', help='Process and output Digital Surface Model',
                    required=False, default=1,  type=int)
parser.add_argument('-pc', '--pointcloud', help='Process and output Point Cloud',
                    required=False, default=0,  type=int)

args = parser.parse_args()

# Parameters
cond_exp_ortho = args.ortho
cond_exp_dsm = args.dsmodel
cond_exp_pc = args.pointcloud

# Initialising photoscan project
doc = PhotoScan.app.document

# Default formats
dft_format = dft.export_format()

format_im = dft_format[0]
format_ortho = dft_format[1]
format_dsm = dft_format[2]
format_pc = dft_format[3]
format_mesh = dft_format[4]


# Set tkinter and variables
tk_project = Tk()
tk_shp = Tk()
tk_photos = Tk()
resolution_raster = 0.05  # In Metres
max_keypoint, max_tiepoint = dft.def_keypoints()
timing = {}

# Defining CoordinateSystem
geographic_projection = PhotoScan.CoordinateSystem(
    'EPSG::4326')  # WGS Geographic Coordinatee System

# Project Directory
project_path = filedialog.askdirectory(
    initialdir='/', title='Select Location to save project')

# project_path = 'E:/Testing/output'
logger.debug('Project path : ' + project_path)

# Project Name
project_name = PhotoScan.app.getExistingDirectory(
    'Enter name of the project: ')

# project_name = 'test'
logger.debug('Project name : ' + project_name)

# Reading Photos Location
path_photos = filedialog.askdirectory(
    initialdir='/', title='Select photos location')

# path_photos = 'E:/Testing/Images'
logger.debug('Project image location is : ' + path_photos)

doc.save(os.path.join(project_path, project_name+'.psx'))

# Sub_Projects=gn.booldialogbox("Do you want to create sub-projects?")
Processing_area = gn.booldialogbox("Do you want to enter processing area?")

# Processing area if given
if Processing_area == 1:
    # Reading Shapefiles
    path_shp = filedialog.askopenfilename(
        initialdir='/', title='Select shapefile',
        filetypes=(('shapefile', '*.shp'), ('all files', '*.*')))

    sf = shapefile.Reader(path_shp)
    num_shp = len(sf.shapes())
    if num_shp == 0:
        logger.debug('No shape available in shapefile')
        sys.exit()

# Output paths
dft_output_path = dft.export_path(
    os.path.join(project_path, 'output', project_name))

path_ortho = dft_output_path[0]
path_dsm = dft_output_path[1]
path_pc = dft_output_path[2]
path_mesh = dft_output_path[3]
path_report = dft_output_path[4]
path_timing = dft_output_path[5]
path_imlo = dft_output_path[6]

# Logging to file
gn.log2file(project_path, project_name)

# photo_list = defaultdict(list)
photo_list = []

# Reading images time
st_read_image = time.time()

for path, subdirs, files in os.walk(path_photos):
    for name in files:
        for k in range(len(format_im)):
            fileExt = os.path.splitext(name)[-1]
            if fileExt == format_im[k]:
                image = os.path.join(path_photos, name)
                photo_list.append(image)

mapplot.gen_map_plotly(photo_list, path_imlo)
logger.debug('Map Plotted')

chunk = doc.addChunk()
chunk.label = '1'

# Ended reading images time
end_read_image = time.time()
timing['Reading Images'] = str(
    round(end_read_image - st_read_image, 0)) + ' sec'

# # Activate chunk
# doc.chunk = doc.chunks

# Set Coordinate System
chunk.crs = geographic_projection
chunk.updateTransform()
chunk.addPhotos(photo_list)

doc.save()

# Loop Start

# Adding Exif data Lat, Long, Elevation to each Camera
for camera in chunk.cameras:
    if camera.reference.location:
        coord = camera.reference.location
        camera.reference.location = PhotoScan.Vector(
            [coord[0], coord[1], coord[2]])

# Output Projection System
output_projection = PhotoScan.CoordinateSystem(
    gn.get_epsg(coord[1], coord[0]))  # UTM Projected Coordinate System

if Processing_area == 1:
    # ,boundary_type=PhotoScan.Shape.BoundaryType.OuterBoundary)
    chunk.importShapes(path=path_shp)

    print(chunk.shapes)
    for shape in chunk.shapes:
        if shape.type == PhotoScan.Shape.Type.Polygon:
            shape.boundary_type = PhotoScan.Shape.BoundaryType.OuterBoundary

# PhotoScan.Shape.BoundaryType.OuterBoundary
doc.save()
logger.debug("Saving Agisoft Project")

# Start Aligning photos time
st_align = time.time()

# Align photos
chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, generic_preselection=True,
                  filter_mask=False, keypoint_limit=max_keypoint, tiepoint_limit=max_tiepoint)
chunk.alignCameras()
chunk.optimizeCameras()

# End Aligning photos time
end_align = time.time()
timing['SFM'] = str(round(end_align - st_align, 0)) + ' sec'
logger.debug('SFM Completed in : ' + timing['SFM'])

# gn.show_points_info(chunk)
# Image Quality
# print(gn.get_quality(chunk))

# saving images
doc.save()

# starting MVS time
st_dense = time.time()

# build dense cloud
chunk.buildDepthMaps(quality=PhotoScan.MediumQuality,
                     filter=PhotoScan.AggressiveFiltering, reuse_depth=True)
chunk.buildDenseCloud()

# Ending Dense PC
end_dense = time.time()
timing['PointCloud'] = str(round(end_dense - st_dense, 0)) + ' sec'
logger.debug('Dense Point Cloud Completed in : ' + timing['PointCloud'])

# save
doc.save()

# build mesh
# chunk.buildModel(surface = PhotoScan.HeightField, interpolation = PhotoScan.EnabledInterpolation, face_count=PhotoScan.MediumFaceCount )

# Starting DEM
st_dem = time.time()

# Build DEM
chunk.buildDem(source=PhotoScan.DenseCloudData,
               interpolation=PhotoScan.EnabledInterpolation, projection=output_projection)
# Ending DEM
end_dem = time.time()
timing['DEM'] = str(round(end_dem - st_dem, 0)) + ' sec'
logger.debug('DEM Completed in : ' + timing['DEM'])

# save
doc.save()

# Starting ortho
st_ortho = time.time()

# Build Ortho
chunk.buildOrthomosaic(surface=PhotoScan.ElevationData, blending=PhotoScan.MosaicBlending,
                       fill_holes=True, dx=resolution_raster, dy=resolution_raster)

# Ending Orthomosaic
end_ortho = time.time()
timing['OrthoMosaic'] = str(round(end_ortho - st_ortho, 0)) + ' sec'
logger.debug('OrthoMosaic Completed in : ' + timing['OrthoMosaic'])

doc.save()


# # Defining Directories
# output_path = os.path.join(project_path, 'output', project_name)

# gn.create_dir(output_path)

# Exporting
if cond_exp_ortho == 1:
    logger.debug('exporting orthomosaic')

    # starting exporting time
    st_export_ortho = time.time()

    chunk.exportOrthomosaic(os.path.join(path_ortho, "ortho.tif"), image_format=PhotoScan.ImageFormatTIFF, format=PhotoScan.RasterFormatTiles,
                            raster_transform=PhotoScan.RasterTransformNone, tiff_big=True,
                            write_kml=False, write_world=True, write_alpha=True, tiff_compression=PhotoScan.TiffCompressionLZW,
                            tiff_overviews=True, jpeg_quality=80, projection=output_projection)

    # Ending exporting time
    end_export_ortho = time.time()
    timing['Export_Ortho'] = str(
        round(end_export_ortho - st_export_ortho, 0)) + ' sec'
    logger.debug('Export_Ortho Completed in : ' + timing['Export_Ortho'])


if cond_exp_pc == 1:
    logger.debug('exporting point cloud')

    # starting exporting time
    st_export_pc = time.time()

    chunk.exportPoints(os.path.join(path_pc, "PC.las"), binary=True,
                       precision=6, colors=True, format=PhotoScan.PointsFormatLAS,
                       projection=output_projection)

    # Ending exporting time
    end_export_pc = time.time()
    timing['Export_PointCloud'] = str(
        round(end_export_pc - st_export_pc, 0)) + ' sec'
    logger.debug('Export_PointCloud Completed in : ' +
                 timing['Export_PointCloud'])


if cond_exp_dsm == 1:
    logger.debug('exporting dsm')

    # starting exporting time
    st_export_dem = time.time()

    chunk.exportDem(os.path.join(path_dsm, "DSM.tif"), image_format=PhotoScan.ImageFormatTIFF,
                    tiff_big=True, nodata=-9999, write_kml=False, write_world=True)

    # Ending exporting time
    end_export_dem = time.time()
    timing['Export_DEM'] = str(
        round(end_export_dem - st_export_dem, 0)) + ' sec'
    logger.debug('Export_DEM Completed in : ' + timing['Export_DEM'])

# Export to PNG
# shutil.copy(output_ortho + str(counter_1) +'.tfw', output_orthomosaic_PNG_path + str(counter_1)  +'.pgw');
# gdal_translate = gdal.Translate(output_orthomosaic_PNG_path + str(counter_1) +".png", output_orthomosaic_tiff_path + str(counter_1) + ".tif", creationOptions = ['COMPRESS=JPEG','TILED=YES'])
# shape.boundary_type = PhotoScan.Shape.BoundaryType.NoBoundary
doc.save()

# Exporting timings to file
print(timing)
logger.debug(timing)

gn.tojson(timing, os.path.join(path_timing, 'Timing.json'))

# Export report
chunk.exportReport(path=path_report, title='Processing Report')
print("Finished")
logger.debug('Finished')

#################################################################################################
PhotoScan.app.quit()
sys.exit()
