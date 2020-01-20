import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.models import (HoverTool,
                          BoxSelectTool,
                          PanTool,
                          WheelZoomTool,
                          BoxZoomTool)
from bokeh.palettes import Category20c

import holoviews as hv
import hvplot.pandas

import panel as pn

from data import df_total, conteos_mensuales, conteos_activos, meses, origenes
from pie_chart import create_pie_chart


# Set HoloViews renderer for Bokeh:
renderer = hv.renderer("bokeh").instance(mode='server')


# Helper function to map bar indices to months
# in the first chart we will create below:
def filtrar_por_indice(df, meses, indices):
    mapeo_indices_meses = pd.Series(dict(enumerate(meses)))
    
    if len(indices) > 0:
        df_filtrado = df[df["mes"].isin(mapeo_indices_meses[indices].values)]
    else:
        df_filtrado = df
    return df_filtrado


## FIRST WIDGET: a simple month selector.
## Created with Panel widgets:
month_selector = pn.widgets.CheckButtonGroup(name="Months",
                                             value=[], 
                                             options=meses,
                                             margin=(5,0),
                                             css_classes=["buttons-custom"]
                                             )


## FIRST PLOT: Bar + Line plot with HvPlot + custom Bokeh tools and
## styles:

# barplot:
barplot_hover = HoverTool(tooltips=[("Mes", "@{mes}"),
                                    ("Nuevos clientes (total)", "@{nuevos}")
                                    ]
                          )

barplot_range_select = BoxSelectTool(dimensions="width")

barplot = conteos_mensuales.hvplot(kind="bar",
                                   x="mes",
                                   y="nuevos",
                                   label="Nuevos clientes (total)",
                                   tools=["tap", barplot_hover, barplot_range_select]
                                   )

# We generate a HoloViews stream to keep track of what
# bars are selected:
barplot_selection_stream = hv.streams.Selection1D(source=barplot)

# lineplot:
barplot_line_hover = HoverTool(tooltips=[("Mes", "@{mes}"),
                                         ("Nuevos clientes (activos)", "@{activos}")
                                        ]
                               )

lineplot = conteos_activos.hvplot(kind="line",
                                  x="mes",
                                  y="activos",
                                  cmap="Pastel2",
                                  label="Nuevos clientes (activos)",
                                  tools=[barplot_line_hover])

# overlay both glyphs:
bars_and_lines = (barplot * lineplot)

bars_and_lines.opts(ylim=(0.0, conteos_mensuales["nuevos"].max()*1.5),
                    legend_position="top_right",
                    toolbar="above",
                    xlabel="Mes",
                    ylabel="Clientes",
                    height=400,
                    responsive=True
                    )

# render plot as Bokeh to make further modifications:
bars_and_lines_bokeh = renderer.get_plot(bars_and_lines).state

bars_and_lines_bokeh.toolbar.autohide = True
bars_and_lines_bokeh.toolbar.active_drag = [i for i in bars_and_lines_bokeh.tools 
                                            if isinstance(i, BoxSelectTool)][0]
bars_and_lines_bokeh.tools = [tool for tool in bars_and_lines_bokeh.tools
                              if not (isinstance(tool, PanTool) or
                                      isinstance(tool, WheelZoomTool) or
                                      isinstance(tool, BoxZoomTool))
                             ]


## SECOND PLOT: histogram with HvPlot.
## This histogram is generated from selected data
## in the bar+line pot defined above. Every time
## some data is filtered in that chart, this
## histogram is re-generated showing only data
## for selected bars. The update is managed
## by Panel:

@pn.depends(barplot_selection_stream.param.index)
def create_histogram(indices_meses):
    df_filtrado = filtrar_por_indice(df_total, meses, indices_meses)
        
    hist = df_filtrado.hvplot(kind="hist", 
                              y="saldo", 
                              bins=50, 
                              height=400, 
                              responsive=True)
    
    return hist


## THIRD PLOT: pie chart (yeah, hate me if you want).
## Just as the histogram above, this chart is re-generated
## every time the bar+line plot selection is updated.
## The pie chart itself is done in pure Bokeh using the
## pie_chart.py module, and it is inspired by 
## https://docs.bokeh.org/en/latest/docs/gallery/pie_chart.html

@pn.depends(barplot_selection_stream.param.index)
def create_piechart(indices_meses):
    
    df_filtrado = filtrar_por_indice(df_total, meses, indices_meses)
    
    if len(indices_meses) == 0:
        titulo = "Origen (total)"
    elif len(indices_meses) == 1:
        titulo = "Origen: mes %s" % meses[indices_meses[0]]
    else:
        meses_titulo = np.array(meses)[sorted(indices_meses)]
        titulo = "Origen: meses %s" % ", ".join(meses_titulo)

    pie_plot_bokeh, _ = create_pie_chart(df_filtrado, titulo, Category20c)

    return pie_plot_bokeh


## CALLBACKS

def mark_selection_in_month_widget(*events):
    mapping = pd.Series({k:v for k, v in list(enumerate(meses))})
    for event in events:
        seleccionado = event.new
        seleccionados = list(mapping.loc[seleccionado].values)
        month_selector.value = seleccionados

def mark_selection_in_barplot(*events):
    mapping = pd.Series({v:k for k, v in list(enumerate(meses))})
    for event in events:
        seleccionado = event.new
        seleccionados = list(mapping.loc[seleccionado].values)
        bars_and_lines_bokeh.renderers[0].data_source.selected.indices = seleccionados
        # Replacing the previous line with the following one will also work (will trigger 
        # new hist and pie plot), but it won't update visually what is selected in 
        # the barplot:
        #barplot_selection_stream.event(index=seleccionados)


## LINK CALLBACKS ABOVE TO ELEMENTS

barplot_selection_stream.param.watch(fn=mark_selection_in_month_widget, 
                                     parameter_names=["index"]
                                    )

month_selector.param.watch(fn=mark_selection_in_barplot, 
                           parameter_names=["value"]
                          )


## BIND ELEMENTS (WIDGETS + CHARTS)
## TO PANEL SERVER AND HTML UI

pane_month_selector = pn.Row(month_selector,
                             name="month_selector_widget",
                             css_classes=["buttons-custom"])

pane_barplot = pn.pane.Bokeh(bars_and_lines_bokeh,
                             name="bar_line_plot")

pane_histogram = pn.panel(create_histogram,
                          name="histogram_plot")

pane_pie = pn.panel(create_piechart,
                    name="pie_plot")


## SERVE ELEMENTS:

pane_month_selector.servable()
pane_barplot.servable()
pane_histogram.servable()
pane_pie.servable()

## CHANGE PAGE TITLE:

curdoc().title = "Dashboard de Panel"
