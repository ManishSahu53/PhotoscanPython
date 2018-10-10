import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import os
import exifread
from src import table as tb


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


def get_geo(photo_list):
    # Asking for photos location

    _lat = []
    _long = []
    _name = []
    _ele = []

    # looking inside the folder for jpg or JPG file formats
    for im in photo_list:
        f = open(im, 'rb')
        tags = exifread.process_file(f, details=False, debug=False)
        if len(tags) == 0:
            continue
        else:
            camera = tags['Image Model'].values
            ref_lat = tags['GPS GPSLatitudeRef'].values
            ref_long = tags['GPS GPSLongitudeRef'].values
            lat_ = gps_to_decimal(tags["GPS GPSLatitude"].values, ref_lat)
            long_ = gps_to_decimal(tags["GPS GPSLongitude"].values, ref_long)
            height = tags["EXIF ExifImageLength"].values[0]
            width = tags["EXIF ExifImageWidth"].values[0]
            capture_time = str(tags["EXIF DateTimeOriginal"])
            focal = float(tags["EXIF FocalLength"].values[0].num) / \
                tags["EXIF FocalLength"].values[0].den
            _lat.append(lat_)
            _long.append(long_)
            _name.append(os.path.basename(im))

    return _lat, _long, _name


def gen_map_plotly(photo_list, path_html):
    mbox_secret = 'sk.eyJ1IjoibWFuaXNoNTNzYWh1IiwiYSI6ImNqbXE4eG1jZjE4NnMzcHFjYnB2cGE0dmcifQ.iy6e7k0HGww42OfP1sj6lA'
    mapbox_access_token = 'pk.eyJ1IjoibWFuaXNoNTNzYWh1IiwiYSI6ImNpeThlZW9xbTAwMjIycXAzaXA1dHliNHcifQ.1pBBXrD8ZyUpfuIzMxT7kQ'
    plotly_key = 'n29UQNU3AfoL6qn7FczC'

    plotly.tools.set_credentials_file(
        username='ManishSahu', api_key=plotly_key)
    # mapbox_access_token = 'ADD_YOUR_TOKEN_HERE'
    _lat, _long, _name = get_geo(photo_list)

    # Saving exif data to table in html
    path_table = os.path.join(os.path.dirname(path_html), 'exif_table.html')
    tb.exif_table(_name, _lat, _long, path_table)

    data=[
        go.Scattermapbox(
            lat=_lat,
            lon=_long,
            mode='markers',
            text=_name,
            hoverinfo='text',
            marker=dict(
                size=14
            ),
            # text=['Manish'],
        )
    ]

    layout=go.Layout(
        title='Image location',
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=_lat[0],
                lon=_long[0]
            ),
            pitch=0,
            style='mapbox://styles/mapbox/satellite-v9',
            zoom=15
        ),
    )

    fig=dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename=path_html)

# plot(fig)  # , filename='Montreal Mapbox')
