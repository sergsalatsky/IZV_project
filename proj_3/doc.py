"""Generovani dat pro infografiku"""
import os

import geopandas as gpd
import pandas as pd
import numpy as np
import contextily as ctx
import matplotlib.pyplot as plt


def save_fig_to_location(fig_location: str, fig: plt.Figure):
    """An utilitary function for saving the figure to specified path

    Args:
        fig_location (str) - a path, where the graph will be saved
        fig (pyplot.Figure) - the figure where a graph has been plotted
    """
    *folder, _ = os.path.split(fig_location)
    folders = '/'.join(folder)
    if folders:
        os.makedirs(folders, exist_ok=True)

    fig.savefig(fig_location, bbox_inches='tight')


def get_dataframe(filename: str) -> pd.DataFrame:
    """Function will obtain the data about traffic accidents of Czech Republic
       from pickle file (which is specified by the given filename).

    Args:
        filename (str) - the filename of pickle file containing the data
        verbose (boolean) - this flag specifies if info of memory decreasing
                            the obtained data shall be shown

    Returns:
        data (pd.DataFrame) - the dataframe with all data about accidents
    """
    data = pd.read_pickle(filename)

    for col in data:
        if col == 'region':
            continue

        if data[col].dtype == np.dtype(str):
            data[col] = data.pop(col).astype("category")

    return data


def generate_table(df: pd.DataFrame):
    """Generovani tabulky o pricinach nehody"""
    df = df.loc[(df.p11 != 4) & (df.p11 != 5)]
    df['p11'] = (df['p11'] >= 7)

    bins_ctgs = {
        'Příčina nezaviněná řidičem': (100, 100),
        'Nepřiměřená rychlost jízdy': (201, 209),
        'Nesprávné předjíždění':      (301, 311),
        'Nedání přednosti v jízdě':   (401, 414),
        'Nesprávný způsob jízdy':     (501, 516),
        'Technická závada vozidla':   (601, 615)
    }
    causes_bins = pd.IntervalIndex.from_tuples(bins_ctgs.values()).set_closed('both')
    causes = pd.cut(df['p12'].to_list(), causes_bins)
    causes.categories = bins_ctgs.keys()

    rel_causes = pd.crosstab(causes, df['p11'], normalize='index')
    rel_causes = rel_causes[True].sort_values() * 100
    abs_causes = pd.crosstab(causes, df['p11'])
    abs_causes = abs_causes[True].sort_values()

    causes_tab = pd.concat([rel_causes, abs_causes], axis=1).transpose()
    causes_tab.index = ['Relativní, %', 'Absolutní, počet']
    print("Tabulka o pricinach nehod\n", causes_tab)

    rel_msg = "{} dochází castěji, pokud je u viníka nehody přítomen alkohol, relativně {:.2f}%"
    print(rel_msg.format(rel_causes.index[-1], rel_causes[-1]))
    abs_msg = ("{} je příčína, která vyskytla nejvíc při přítomném alkoholu "
               "u viníka nehody, celkem {} nehod")
    print(abs_msg.format(abs_causes.index[-1], abs_causes[-1]))


def generate_graph(df: pd.DataFrame):
    """Vykresleni grafu o mistach nehody"""
    df = df.loc[df.region == 'JHM']
    df = df.loc[(df.p11 != 4) & (df.p11 != 5)]
    df = df.loc[~(np.isnan(df.d) | np.isnan(df.e))]
    df['p11'] = (df['p11'] >= 7)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.d, df.e))
    gdf.set_crs(epsg=5514)

    fig, ax = plt.subplots(figsize=(16, 9))
    gdf.loc[gdf.p11 == True].plot(ax=ax, markersize=5)
    ctx.add_basemap(ax, crs='epsg:5514', source=ctx.providers.Stamen.TonerLite)

    ax.set_title('Mista havarii v Jihomoravskem kraji')
    ax.set_axis_off()

    save_fig_to_location('fig.png', fig)
    plt.close()

    df['p5a'] = (df['p5a'] == 1)
    cntr_alco = pd.crosstab(df['p5a'], df['p11'])[True]
    percentage = 100 * (cntr_alco[True] / cntr_alco.sum())
    print(f"Relativní počet nehod v obcích vůči nehod mimo obcí: {percentage:.2f}%")


if __name__ == "__main__":
    df = get_dataframe('accidents.pkl.gz')
    generate_table(df)
    generate_graph(df)