import plotly.plotly as py
import plotly.graph_objs as go
import plotly

def exif_table(name, lat, long, path_html):
    trace = go.Table(
        header=dict(values=['Image Name', 'Latitude', 'Longitude'],
                    line = dict(color='#7D7F80'),
                    fill = dict(color='#a1c3d1'),
                    align = ['left'] * 5),
        cells=dict(values=[name, lat, long],
                line = dict(color='#7D7F80'),
                fill = dict(color='#EDFAFF'),
                align = ['left'] * 5))

    layout = dict(width=1000, height=3000)
    data = [trace]
    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename=path_html)