import os
import ntpath
import tkinter.messagebox as messagebox

# list all directories
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def UTM_EPSG(zone_no):
    switcher = {
        41: 'EPSG::32641',
        42: 'EPSG::32642',
        43: 'EPSG::32643',
        44: 'EPSG::32644',
        45: 'EPSG::32645',
        46: 'EPSG::32646',
        47: 'EPSG::32647',
        48: 'EPSG::32648'
    }
    return switcher.get(zone_no, 'Invalid Zone: Please check the Exif data of Images')


def get_epsg(lat, long):
    import utm
    projected = utm.from_latlon(lat, long)
    zone_no = projected[2]
    epsg_code = UTM_EPSG(zone_no)
    return epsg_code


def booldialogbox(message):
    result = messagebox.askquestion(
        'Provide you input', message, icon='warning')
    if result == 'yes':
        return 1
    else:
        return 0


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

