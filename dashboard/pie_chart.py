import numpy as np

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import Figure
from bokeh.transform import cumsum as bokeh_cumsum

def create_pie_chart(dataframe, title, palette):

    radio_tarta = 0.4

    df_pie_plot = dataframe.groupby("origen").size().sort_values(ascending=False).reset_index()
    df_pie_plot.columns = ["origen", "conteo"]

    df_pie_plot["porcentaje"] = df_pie_plot["conteo"]/df_pie_plot["conteo"].sum() * 100
    df_pie_plot["porcentaje"] = df_pie_plot["porcentaje"].apply(lambda x: "{0:.2f}%".format(x))
    df_pie_plot["porcentaje_texto"] = df_pie_plot["origen"] + "\n" + df_pie_plot["porcentaje"]
    
    df_pie_plot["angulo"] = df_pie_plot["conteo"]/df_pie_plot["conteo"].sum() * 2 * np.pi
    df_pie_plot["angulo_acumulado"] = df_pie_plot["angulo"].cumsum()
    df_pie_plot["angulo_bisectriz"] = df_pie_plot["angulo_acumulado"] - df_pie_plot["angulo"] / 2.0
    df_pie_plot["posicion_x_texto"] = radio_tarta * 0.6 * np.cos(df_pie_plot["angulo_bisectriz"])
    df_pie_plot["posicion_y_texto"] = radio_tarta * 0.6 * np.sin(df_pie_plot["angulo_bisectriz"])

    df_pie_plot["color"] = palette[:len(df_pie_plot)]

    df_pie_plot_source = ColumnDataSource(data=df_pie_plot)

    pie_plot_bokeh = Figure(title=title,
                            #toolbar_location=None,
                            x_range=(-0.45, 0.45),
                            y_range=(-0.45, 0.45))

    sectores = pie_plot_bokeh.wedge(x=0, 
                                    y=0, 
                                    radius=radio_tarta,
                                    start_angle=bokeh_cumsum("angulo", include_zero=True), 
                                    end_angle=bokeh_cumsum('angulo'),
                                    line_color="white", 
                                    line_width=3,
                                    fill_color='color',
                                    #legend_field="origen",
                                    alpha=0.8,
                                    hover_color="color",
                                    hover_alpha=1.0,
                                    source=df_pie_plot_source)
    
    textos = pie_plot_bokeh.text(x='posicion_x_texto', 
                                 y='posicion_y_texto', 
                                 text="porcentaje_texto",
                                 text_color="white",
                                 text_font_style="bold",
                                 text_align="center",
                                 text_baseline="middle",
                                 source=df_pie_plot_source)

    # Old hover:
    #hover_pie = HoverTool(tooltips="@{origen}: @{conteo}",
    #                      renderers=[sectores])

    # New hover:
    hover_pie = HoverTool(tooltips=[("Origen", "@{origen}"),
                                    ("Clientes", "@{conteo}"),
                                    ("Porcentaje", "@{porcentaje}")],
                          renderers=[sectores])

    pie_plot_bokeh.add_tools(hover_pie)

    pie_plot_bokeh.axis.axis_label=None
    pie_plot_bokeh.axis.visible=False
    pie_plot_bokeh.grid.grid_line_color = None
    
    return pie_plot_bokeh, df_pie_plot_source

