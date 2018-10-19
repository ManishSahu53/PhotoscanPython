import exifread

def eval_frac(value):
    try:
        return float(value.num) / float(value.den)
    except ZeroDivisionError:
        return None

def gps_to_decimal(values, reference):
    sign = 1 if reference in 'NE' else -1
    degrees = eval_frac(values[0])
    minutes = eval_frac(values[1])
    seconds = eval_frac(values[2])
    return sign*(degrees + minutes / 60 + seconds / 3600)

def get_exif(file):
    f = open(file, 'rb')
    tags = exifread.process_file(f, details=False)
    camera = tags['Image Model'].values
    ref_lat = tags['GPS GPSLatitudeRef'].values
    ref_long = tags['GPS GPSLongitudeRef'].values
    lat = gps_to_decimal(tags["GPS GPSLatitude"].values, ref_lat)
    long = gps_to_decimal(tags["GPS GPSLongitude"].values, ref_long)
    ele = eval_frac(tags["GPS GPSAltitude"].values[0])
    return lat, long, ele
