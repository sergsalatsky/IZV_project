#!/usr/bin/python3.8
# coding=utf-8
"""Project #3 for subject IZV"""
import os

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import sklearn.cluster
import numpy as np
# muzeze pridat vlastni knihovny


def _save_fig_to_location(fig_location: str, fig: plt.Figure):
    """An utilitary function for saving the figure to specified path

    Args:
        fig_location (str) - a path, where the graph will be saved
        fig (pyplot.Figure) - the figure where a graph has been plotted
    """
    *folder, _ = os.path.split(fig_location)
    folders = '/'.join(folder)
    if folders:
        os.makedirs(folders, exist_ok=True)

    fig.savefig(fig_location)


def make_geo(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """ Konvertovani dataframe do gpd.GeoDataFrame se spravnym kodovani"""
    df = df.loc[~(np.isnan(df.d) | np.isnan(df.e))]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.d, df.e))
    gdf.set_crs(epsg=5514)

    return gdf


def plot_geo(gdf: gpd.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s dvemi podgrafy podle lokality nehody """
    def subplot_geo(gdf, ax, place, title, color):
        gdf.loc[gdf.p5a == place].plot(ax=ax, markersize=5, color=color)
        ctx.add_basemap(ax, crs='epsg:5514', source=ctx.providers.Stamen.TonerLite, zoom=10)

        ax.set_title(title)
        ax.set_xlim((-680276.578125, -520931.825))
        ax.set_ylim((-1220801.7125, -1108740.0375))
        ax.set_axis_off()

    gdf = gdf.loc[gdf.region == 'JHM']  # select the chosen region for plotting

    fig, ax = plt.subplots(1, 2, figsize=(16, 9))
    subplot_geo(gdf, ax[0], 1, 'Nehody v JHM kraji: v obci', 'blue')
    subplot_geo(gdf, ax[1], 2, 'Nehody v JHM kraji: mimo obec', 'red')

    if show_figure:
        plt.show()

    if fig_location:
        _save_fig_to_location(fig_location, fig)


def plot_cluster(gdf: gpd.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    gdf = gdf.loc[gdf.region == 'JHM']

    # Vytvoreni shluku
    gdf_clusters = gdf.copy().set_geometry(gdf.centroid)
    coords = np.dstack([gdf_clusters.geometry.x, gdf_clusters.geometry.y]).reshape(-1, 2)
    db = sklearn.cluster.MiniBatchKMeans(n_clusters=15).fit(coords)

    gdf_clusters["cluster"] = db.labels_
    gdf_clusters = gdf_clusters.dissolve(
        by="cluster", aggfunc={"p1": "count"}
    ).rename(columns={'p1': "cnt"})
    gdf_coords = gpd.GeoDataFrame(geometry=gpd.points_from_xy(
        db.cluster_centers_[:, 0], db.cluster_centers_[:, 1]
    ))
    gdf_clusters = gdf_clusters.merge(
        gdf_coords, left_on="cluster", right_index=True
    ).set_geometry("geometry_y")

    # Vytvoreni grafu
    fig = plt.figure(figsize=(16, 9))
    ax = plt.gca()

    gdf.plot(ax=ax, markersize=1, color='grey')
    gdf_clusters.plot(ax=ax, markersize=gdf_clusters["cnt"], column="cnt", legend=True, alpha=0.5)
    ctx.add_basemap(ax, crs="epsg:5514", source=ctx.providers.Stamen.TonerLite, zoom=10)

    ax.set_title('Shlukování nehod v JHM')
    ax.set_xlim((-680276.578125, -520931.825))
    ax.set_ylim((-1220801.7125, -1108740.0375))
    ax.set_axis_off()

    if show_figure:
        plt.show()

    if fig_location:
        _save_fig_to_location(fig_location, fig)


if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    geo_df = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(geo_df, "geo1.png", True)
    plot_cluster(geo_df, "geo2.png", True)
