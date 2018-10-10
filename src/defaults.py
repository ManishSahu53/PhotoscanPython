''' Default settings'''
import os

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Format of output deliverables
def export_format():
    format_im = ['.JPG', '.jpg', '.png', '.PNG', '.jpeg', '.JPEG']
    format_ortho = ['.tif', '.png']
    format_dsm = ['.tif']
    format_pc = ['.ply', '.las']
    format_mesh = ['.ply', '.obj']
    return [format_im, format_ortho, format_dsm, format_pc, format_mesh]

# Resolution of outputs
def export_res():
    res_ortho = 0.05
    res_dsm = 0.10
    return res_ortho, res_dsm

# Photoscan geo-coordinates
def epsg_4326():
    return 'EPSG::4326'

# Exporting paths
def export_path(output_path):
    path_ortho = os.path.join(output_path, 'ortho')
    path_dsm = os.path.join(output_path, 'dsm')
    path_pc = os.path.join(output_path, 'pointcloud')
    path_mesh = os.path.join(output_path, 'mesh')
    path_report = os.path.join(output_path,'report.pdf')
    path_timing = output_path
    path_imlocation = os.path.join(output_path, 'image.html')

    create_dir(path_ortho)
    create_dir(path_dsm)
    create_dir(path_pc)
    create_dir(path_mesh)
    return [path_ortho, path_dsm, path_pc, path_mesh, path_report, path_timing, path_imlocation]

def def_keypoints():
    max_keypoint = 40000
    max_tiepoint = 4000
    return max_keypoint, max_tiepoint