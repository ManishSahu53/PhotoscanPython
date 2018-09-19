''' Default settings'''
import os

# Format of output deliverables
def export_format():
    format_im = ['.JPG', '.jpg', '.png', '.PNG', '.jpeg', '.JPEG']
    format_ortho = ['.tif', '.png']
    format_dsm = ['.tif']
    format_pc = ['.ply', '.las']
    format_mesh = ['.ply', '.obj']
    return format_im, format_ortho, format_dsm, format_pc, format_mesh

# Resolution of outputs
def export_res():
    res_ortho = 0.05
    res_dsm = 0.10
    return res_ortho, res_dsm

# Photoscan geo-coordinates
def epsg_4326(): 
    return 'EPSG::4326'

# Exporting paths
def export_path(path):
    path_im = os.path.join(path,'im')
    path_ortho = os.path.join(path,'ortho')
    path_dsm = os.path.join(path,'dsm')
    path_pc = os.path.join(path,'pointcloud')
    path_mesh = os.path.join(path,'mesh')
    return path_im, path_ortho, path_dsm, path_pc, path_mesh

max_keypoint = 40000
max_tiepoint = 4000
