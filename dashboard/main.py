import panel as pn
import numpy as np
import pandas as pd
import hvplot.pandas
import holoviews as hv
from bokeh.io import curdoc

renderer = hv.renderer("bokeh").instance(mode='server')


tabla = pd.DataFrame({"Ventas": (list(np.random.normal(500, 20, 300)) +
                                 list(np.random.chisquare(32, 450) + 450)),
                      "Ciudad": ["Madrid"] * 300 + ["Barcelona"] * 450
                      })

tabla_conteos = tabla.groupby("Ciudad").size().to_frame().reset_index()
tabla_conteos.columns = ["Ciudad", "Conteo"]
tabla_conteos["y"] = [1] * len(tabla_conteos)
tabla_conteos["Tamaño punto"] = tabla_conteos["Conteo"] * 4

burbujas = tabla_conteos.hvplot(kind="scatter",
                                x="Ciudad",
                                y="y",
                                size="Tamaño punto",
                                c="Ciudad",
                                legend=False,
                                tools=["tap"],
                                height=400,
                                responsive=True)

selection = hv.streams.Selection1D(source=burbujas)

@pn.depends(selection.param.index)
def histograma(indices_ciudades):
    mapeo_indices_ciudades = pd.Series({0: "Barcelona", 1: "Madrid"})
    mapeo_ciudades_colores = pd.Series({"Barcelona": "blue", "Madrid": "orange"})
    
    hist = hv.render(tabla.hvplot(kind="hist", by="Ciudad", bins=40, height=400, responsive=True))
    
    if len(indices_ciudades) > 0:
        for i, renderer in enumerate(hist.renderers):
            if i not in indices_ciudades:
                hist.renderers[i].muted=True    
    return hist

pane_one = pn.pane.Bokeh(renderer.get_plot(burbujas).state, name="lineas_1")
pane_two = pn.panel(histograma, name="scatter_1")

pane_one.servable()
pane_two.servable()

curdoc().title = "Dashboard de Panel"