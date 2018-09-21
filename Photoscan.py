def log2file(project_path, project_name):
    logging.basicConfig(filename=os.path.join(
        project_path, project_name + "_log.txt"))
    stderrLogger = logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrLogger)


import logging
import PhotoScan
import os
from fnmatch import fnmatch
import shapefile
from tkinter import filedialog
from tkinter import *
import tkinter.messagebox as messagebox
import ntpath
import gdal
import shutil
import argparse
from src import defaults
from src import general as gn
from src import exif as exf
from src import convhull as cvh
from collections import defaultdict
import argparse


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

# Set tkinter and variables
tk_project = Tk()
tk_shp = Tk()
tk_photos = Tk()
resolution_raster = 0.05  # In Metres
pattern = ['.JPG', '.jpg', '.png', '.PNG', '.jpeg', '.JPEG']
max_keypoint = 40000
max_tiepoint = 4000

# Defining CoordinateSystem
geographic_projection = PhotoScan.CoordinateSystem(
    'EPSG::4326')  # WGS Geographic Coordinatee System

# Project Directory
project_path = filedialog.askdirectory(
    initialdir='/', title='Select Location to save project')

# Project Name
project_name = PhotoScan.app.getExistingDirectory(
    'Enter name of the project: ')

# Logging to file
log2file(project_path, project_name)

# Output Directory
gn.create_dir(os.path.join(project_path, 'output', project_name))
gn.create_dir(os.path.join(project_path, 'output', 'orthomosaic'))

# Reading Photos Location
path_photos = filedialog.askdirectory(
    initialdir='/', title='Select photos location')

doc.save(os.path.join(project_path, project_name+'.psx'))

# Reading Shapefiles
path_shp = filedialog.askopenfilename(
    initialdir='/', title='Select shapefile', filetypes=(('shapefile', '*.shp'), ('all files', '*.*')))

sf = shapefile.Reader(path_shp)

num_shp = len(sf.shapes())

# Sub_Projects=gn.booldialogbox("Do you want to create sub-projects?")
Processing_area = gn.booldialogbox("Do you want to enter processing area?")

# photo_list = defaultdict(list)
photo_list = []

for path, subdirs, files in os.walk(path_photos):
    for name in files:
        for k in range(len(pattern)):
            fileExt = os.path.splitext(name)[-1]
            if fileExt == pattern[k]:
                image = os.path.join(path_photos, name)
                photo_list.append(image)

chunk = doc.addChunk()
chunk.label = '1'

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

# ,boundary_type=PhotoScan.Shape.BoundaryType.OuterBoundary)
chunk.importShapes(path=path_shp)

if not chunk.shapes:
    chunk.shapes = PhotoScan.Shape()

PhotoScan.Shape.BoundaryType.OuterBoundary

# PhotoScan.Shape.BoundaryType.OuterBoundary
doc.save()
print("Saving Agisoft Project")

# Align photos
chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, generic_preselection=True,
                  filter_mask=False, keypoint_limit=max_keypoint, tiepoint_limit=max_tiepoint)
chunk.alignCameras()
chunk.optimizeCameras()

# saving images
doc.save()

# build dense cloud
chunk.buildDepthMaps(quality=PhotoScan.MediumQuality,
                     filter=PhotoScan.AggressiveFiltering, reuse_depth=True)
chunk.buildDenseCloud()

# save
doc.save()

# build mesh
# chunk.buildModel(surface = PhotoScan.HeightField, interpolation = PhotoScan.EnabledInterpolation, face_count=PhotoScan.MediumFaceCount )

# Build DEM
chunk.buildDem(source=PhotoScan.DenseCloudData,
               interpolation=PhotoScan.EnabledInterpolation, projection=output_projection)

# save
doc.save()

# Build Ortho
chunk.buildOrthomosaic(surface=PhotoScan.ElevationData, blending=PhotoScan.MosaicBlending,
                       fill_holes=True, dx=resolution_raster, dy=resolution_raster)


doc.save()


# Defining Directories
output_path = os.path.join(project_path, 'output', project_name)

gn.create_dir(output_path)

# Exporting
if cond_exp_ortho == 1:
    print('exporting orthomosaic')
    chunk.exportOrthomosaic(os.path.join(output_path ,"ortho.tif"), image_format=PhotoScan.ImageFormatTIFF, format=PhotoScan.RasterFormatTiles,
                            raster_transform=PhotoScan.RasterTransformNone, tiff_big=True,
                            write_kml=False, write_world=True, write_alpha=True, tiff_compression=PhotoScan.TiffCompressionLZW,
                            tiff_overviews=True, jpeg_quality=80, projection=output_projection)

if cond_exp_pc == 1:
    print('exporting point cloud')
    chunk.exportPoints(os.path.join(output_path, "PC.las"), binary=True,
                       precision=6, colors=True, format=PhotoScan.PointsFormatLAS)

if cond_exp_dsm == 1:
    print('exporting dsm')
    chunk.exportDem(os.path.join(output_path, "DSM.tif"), image_format=PhotoScan.ImageFormatTIFF, tiff_big=True, nodata=-9999, write_kml=False, write_world=True)

# Export to PNG
# shutil.copy(output_ortho + str(counter_1) +'.tfw', output_orthomosaic_PNG_path + str(counter_1)  +'.pgw');
# gdal_translate = gdal.Translate(output_orthomosaic_PNG_path + str(counter_1) +".png", output_orthomosaic_tiff_path + str(counter_1) + ".tif", creationOptions = ['COMPRESS=JPEG','TILED=YES'])
# shape.boundary_type = PhotoScan.Shape.BoundaryType.NoBoundary
doc.save()

print("Finished")

#################################################################################################
PhotoScan.app.quit()
