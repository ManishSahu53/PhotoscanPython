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
tk_project.directory = filedialog.askdirectory(
    initialdir='/', title='Select Location to save project')
project_path = tk_project.directory

# Project Name
project_name = PhotoScan.app.getExistingDirectory(
    'Enter name of the project: ')

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

Sub_Projects = gn.booldialogbox("Do you want to create sub-projects?")
Processing_area = gn.booldialogbox("Do you want to enter processing area?")

# Creating chucks
for i in range(num_shp):
    chunk = doc.addChunk()
    chunk.label = gn.path_leaf(str(i))


photo_list = []
for path, subdirs, files in os.walk(path_photos):
    for name in files:
        for k in range(len())
        if fnmatch(name, pattern):
            inside = cvh.conv_hull(os.path.join(path_photos, name), path_shp)

            for j in range(len(inside)):
                # If image lie outisde shape file then continue else
                if inside[j] == 0:
                    continue
                else:
                    # Activate chunk
                    doc.chunk = doc.chunks[j]

                    # Set Coordinate System
                    chunk.crs = geographic_projection
                    chunk.updateTransform()
                    chunk.addPhotos(os.path.join(path_photos, name))

# # Loop Start
# for k in range(0, no_of_folders):
#     directory = str(folders_in_images[k])

#     chunk = doc.addChunk()
#     chunk.label = gn.path_leaf(folders_in_images[k])
#     doc.chunk = doc.chunks[k]

#     # Set Coordinate System
#     chunk.crs = geographic_projection
#     chunk.updateTransform()
#     chunk.addPhotos(photo_list)

#     # Adding Exif data Lat, Long, Elevation to each Camera
#     for camera in chunk.cameras:
#         if camera.reference.location:
#             coord = camera.reference.location
#             camera.reference.location = PhotoScan.Vector(
#                 [coord[0], coord[1], coord[2]])

#     # Output Projection System
#     Output_projection = PhotoScan.CoordinateSystem(
#         gn.get_epsg(coord[1], coord[0]))  # UTM Projected Coordinate System

#     # ,boundary_type=PhotoScan.Shape.BoundaryType.OuterBoundary)
#     chunk.importShapes(path=path_shp)
#     counter = 0  # counter for making sure that smae shape has been selected
#     for i in chunk.shapes:
#         if i.type != PhotoScan.Shape.Type.Polygon:
#             continue
#         if counter == k:
#             shape = i
#         counter = counter + 1

#     shape.boundary_type = PhotoScan.Shape.BoundaryType.OuterBoundary

#     # PhotoScan.Shape.BoundaryType.OuterBoundary
#     doc.save()
#     print("Saving Agisoft Project")

#     # Align photos
#     chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, generic_preselection=True,
#                       filter_mask=False, keypoint_limit=max_keypoint, tiepoint_limit=max_tiepoint)
#     chunk.alignCameras()
#     chunk.optimizeCameras()
#     # save
#     doc.save()

#     # build dense cloud
#     chunk.buildDepthMaps(quality=PhotoScan.MediumQuality,
#                          filter=PhotoScan.AggressiveFiltering, reuse_depth=True)
#     chunk.buildDenseCloud()

#     # save
#     doc.save()

#     #chunk.exportPoints(project_path + project_name + ".las", binary=True, precision=6, colors=True, format=PhotoScan.PointsFormatLAS)
#     # build mesh
#     #chunk.buildModel(surface = PhotoScan.HeightField, interpolation = PhotoScan.EnabledInterpolation, face_count=PhotoScan.MediumFaceCount )

#     # Build DEM
#     chunk.buildDem(source=PhotoScan.DenseCloudData,
#                    interpolation=PhotoScan.EnabledInterpolation, projection=Output_projection)

#     # save
#     doc.save()

#     #chunk.exportDem(project_path + project_name + "_DEM.tif", image_format=PhotoScan.ImageFormatTIFF, raster_format = PhotoScan.RasterFormatTiles, nodata=-9999, write_kml=False, write_world=True)

#     # Build Ortho
#     chunk.buildOrthomosaic(surface=PhotoScan.ElevationData, blending=PhotoScan.MosaicBlending,
#                            fill_holes=True, dx=resolution_raster, dy=resolution_raster)

#     # If all the images are present in one folder then process all images at once and export ortho mosaic according to shapefile defined
#     if no_of_folders == 1:
#         doc.save()
#         shape.boundary_type = PhotoScan.Shape.BoundaryType.NoBoundary
#         counter_1 = 0
#         del shape  # Deleting Previously defined chunk.shape

#         for shape in chunk.shapes:  # Iterating of shapes to clip output
#             if shape.type != PhotoScan.Shape.Type.Polygon:
#                 continue
#             shape.boundary_type = PhotoScan.Shape.BoundaryType.OuterBoundary

#             # Defining Directories
#             output_orthomosaic_tiff_path = Orthomosaic_path + "tiff/"
#             output_orthomosaic_KMZ_path = Orthomosaic_path + "KMZ/"
#             output_orthomosaic_PNG_path = Orthomosaic_path + "PNG/"
#             create_dir(output_orthomosaic_tiff_path)
#             create_dir(output_orthomosaic_KMZ_path)
#             create_dir(output_orthomosaic_PNG_path)

#             # Export to Tiff
#             #chunk.exportOrthomosaic(output_orthomosaic_tiff_path + str(counter_1) + ".tif", image_format=PhotoScan.ImageFormatTIFF, format = PhotoScan.RasterFormatTiles, raster_transform=PhotoScan.RasterTransformNone, write_kml=False, write_world=True,write_alpha=True,tiff_compression=PhotoScan.TiffCompressionPackbits,tiff_overviews=True,jpeg_quality=80,projection=Output_projection)

#             # Export to KML
#             #chunk.exportOrthomosaic(output_orthomosaic_KMZ_path  + str(counter_1) + ".kmz", image_format=PhotoScan.ImageFormatPNG, format = PhotoScan.RasterFormatKMZ, tiff_compression=PhotoScan.TiffCompressionJPEG,write_kml=True,jpeg_quality=80,write_alpha=True)

#             # Export to PNG
#             #shutil.copy(output_orthomosaic_tiff_path + str(counter_1) +'.tfw', output_orthomosaic_PNG_path + str(counter_1)  +'.pgw');
#             #gdal_translate = gdal.Translate(output_orthomosaic_PNG_path + str(counter_1) +".png", output_orthomosaic_tiff_path + str(counter_1) + ".tif", creationOptions = ['COMPRESS=JPEG','TILED=YES'])
#             #shape.boundary_type = PhotoScan.Shape.BoundaryType.NoBoundary
#             counter_1 = counter_1 + 1
#             doc.save()

#     else:
#         # Defining Directories
#         output_orthomosaic_tiff_path = Orthomosaic_path + "tiff/"
#         output_orthomosaic_KMZ_path = Orthomosaic_path + "KMZ/"
#         output_orthomosaic_PNG_path = Orthomosaic_path + "PNG/"
#         create_dir(output_orthomosaic_tiff_path)
#         create_dir(output_orthomosaic_KMZ_path)
#         create_dir(output_orthomosaic_PNG_path)

#         doc.save()

#         # Export to Tiff
#         #chunk.exportOrthomosaic(output_orthomosaic_tiff_path + str(k) + ".tif", image_format=PhotoScan.ImageFormatTIFF, format = PhotoScan.RasterFormatTiles, raster_transform=PhotoScan.RasterTransformNone,tiff_big=True, write_kml=False, write_world=True,write_alpha=True,tiff_compression=PhotoScan.TiffCompressionJPEG,tiff_overviews=True,jpeg_quality=80,projection=Output_projection)

#         # Export to KML
#         #chunk.exportOrthomosaic(output_orthomosaic_KMZ_path + str(k) + ".kmz", image_format=PhotoScan.ImageFormatPNG, format = PhotoScan.RasterFormatKMZ, tiff_compression=PhotoScan.TiffCompressionJPEG,write_kml=True,jpeg_quality=80,write_alpha=True)

#         # Export to PNG
#         #shutil.copy(output_orthomosaic_tiff_path + str(k) +'.tfw', output_orthomosaic_PNG_path + str(k) +'.pgw');
#         #gdal_translate = gdal.Translate(output_orthomosaic_PNG_path + str(k) + ".png",output_orthomosaic_tiff_path + str(k) + ".tif", creationOptions = ['COMPRESS=JPEG','TILED=YES'])

#         # Resetting the boundary
#         #shape.boundary_type = PhotoScan.Shape.BoundaryType.NoBoundary
#         del i
#         # save
#         doc.save()

#     print("Finished")

#     ################################################################################################
# PhotoScan.app.quit()
