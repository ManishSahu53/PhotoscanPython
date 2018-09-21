from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, GMapOptions
from bokeh.plotting import gmap
import numpy as np
import bokeh.plotting
import bokeh.layouts

fig1 = bokeh.plotting.figure()
fig1.sizing_mode = 'scale_width'

fig2 = bokeh.plotting.figure()
fig2.sizing_mode = 'scale_width'

column = bokeh.layouts.column([fig1, fig2])
column.sizing_mode = 'scale_width'


def im2map(lat, long, project_name):
    output_file(project_name + '.html')
    _lat = np.asarray(lat)
    _long = np.asarray(long)

    avg_lat = np.mean(_lat)
    avg_long = npp.mean(_long)

    map_options = GMapOptions(
        lat=avg_lat, lng=avg_long, map_type="roadmap", zoom=11)

    # For GMaps to function, Google requires you obtain and enable an API key:
    #
    #     https://developers.google.com/maps/documentation/javascript/get-api-key
    #
    # Replace the value below with your personal API key:
    p = gmap("AIzaSyBsOQ-g23ZFMkl9_pkiZxOoqgslpSB4bfA",
             map_options, title=project_name)

    p.add_tools(HoverTool(
        tooltips=[('lat', '@lat',
                   'long', '@long')]
    ))

    source = ColumnDataSource(
        data=dict(lat=list(_lat),
                  lon=list(_long))
    )

    p.circle(x="lon", y="lat", size=15, fill_color="blue",
             fill_alpha=0.8, source=source)
