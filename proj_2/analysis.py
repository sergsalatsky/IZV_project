#!/usr/bin/env python3.8
# coding=utf-8
"""Project #2 for subject IZV"""

import os
from sys import getsizeof
from copy import deepcopy

from matplotlib import pyplot as plt
import pandas as pd


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

    fig.savefig(fig_location, bbox_inches='tight')


def _get_region_data(df: pd.DataFrame) -> pd.DataFrame:
    """An utilitary function for getting predefined regions data"""
    regions = ['HKK', 'JHM', 'PHA', 'PLK']
    return df.loc[df['region'].isin(regions)]


def _subplot_damage(damage_df: pd.DataFrame, ax: plt.Axes, region: str):
    """Function will plot a graph about damage caused by the accidents
       for specified region.

    Args:
        damage_df (pd.DataFrame) - the given dataframe with the data about damage
        ax (pyplot.Axes) - the subplot where the graph will be plotted
        region (str) - the specified region
    """
    damage_df = damage_df.loc[lambda df: df['region'] == region]
    damage_df = pd.crosstab(damage_df['fine'], damage_df['cause'])

    with plt.style.context('seaborn-paper'):
        damage_df.plot.bar(
            ax=ax, logy=True, ylim=[10**-1, 10**5],
            width=0.6, bottom=0, align='center',
            title=region, legend=False, rot=0,
            xlabel='Škoda [tisic Kč]', ylabel='Počet',
        )


def _subplot_surface(surface_df: pd.DataFrame, ax: plt.Axes, region: str):
    """Function will plot a graph about accidents depending on surfaces
       for specified region.

    Args:
        surface_df (pd.DataFrame) - the given dataframe with the data about surfaces
        ax (pyplot.Axes) - the subplot where the graph will be plotted
        region (str) - the specified region
    """
    surface_df = surface_df.xs(region, level='region')
    surface_df.index = pd.to_datetime(surface_df.index)
    surface_df = surface_df.groupby(pd.Grouper(freq='M')).sum()

    with plt.style.context('seaborn-paper'):
        surface_df.plot.line(
            ax=ax, title=region, legend=False, rot=0,
            xlabel='Datum vzniku nehody', ylabel='Počet nehod',
        )


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
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
    data['date'] = deepcopy(data['p2a']).astype('datetime64[ns]')

    original_size_mb = getsizeof(data)/1048576

    for col in data:
        if col in ['region', 'p13a', 'p13b', 'p13c']:
            continue

        data[col] = data.pop(col).astype("category")

    new_size_mb = getsizeof(data)/1048576
    if verbose:
        print(f'orig_size={original_size_mb:.1f} MB')
        print(f'new_size={new_size_mb:.1f} MB')

    return data

def plot_conseq(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    """This function will create a plot with data
       about the consequences of different accidents (deaths, injuries etc.)

    Args:
        df (pd.DataFrame) - the given dataframe with all data about accidents
        fig_location (str) - a path, where the graph will be saved
        show_figure (boolean) - flag indicating that a plot shall be shown
    """
    causes = ['p13a', 'p13b', 'p13c']
    causes_names = ('Úmrtí (p13a)', 'Těžce ranění (p13b)',
                    'Lehce ranění (p13c)', 'Celkem nehod')
    colours = {'p13a': 'C3', 'p13b': 'darkorange', 'p13c': 'green', 'total_count': 'mediumblue'}

    accidents = df.groupby('region')[causes].sum()
    accidents['total_count'] = df['region'].value_counts()
    accidents = accidents.sort_values(by='total_count', ascending=False)

    with plt.style.context('seaborn-paper'):
        figure = accidents.plot.bar(
            subplots=True, figsize=(16, 9), color=colours,
            width=0.6, bottom=0, align='center', title=causes_names,
            ylabel='Počet nehod', legend=None, rot=30
        )
        figure = figure[0].get_figure()

    plt.suptitle('Následky nehod v jednotlivých regionech')
    plt.xlabel('Regiony')

    if fig_location:
        _save_fig_to_location(fig_location, figure)

    if show_figure:
        plt.show()
    plt.close(figure)


def plot_damage(df: pd.DataFrame, fig_location: str = None,
                show_figure: bool = False):
    """This function will create a plot with data
       about damage caused by the accident

    Args:
        df (pd.DataFrame) - the given dataframe with all data about accidents
        fig_location (str) - a path, where the graph will be saved
        show_figure (boolean) - flag indicating that a plot shall be shown
    """
    regions_df = _get_region_data(df)

    fine_bins = [0, 500, 2000, 5000, 10000, float("inf")]
    fines = pd.cut(regions_df['p53'].to_list(), bins=fine_bins, right=False)
    fines.categories = ['< 50', '50-200', '200-500', '500-1000', '> 1000']

    causes_bins = pd.IntervalIndex.from_tuples([
        (100, 100), (201, 209), (301, 311),
        (401, 414), (501, 516), (601, 615)
    ]).set_closed('both')
    causes = pd.cut(regions_df['p12'].to_list(), causes_bins)
    causes.categories = [
        'Nezaviněná řidičem', 'Nepřiměřená rychlost jízdy', 'Nesprávné předjíždění',
        'Nedání přednosti v jízdě', 'Nesprávný způsob jízdy', 'Technická závada vozidla'
    ]

    damage_df = pd.DataFrame({'region': regions_df['region'], 'fine': fines, 'cause': causes})

    figure, axs = plt.subplots(2, 2, figsize=(16, 9))
    figure.suptitle('Nehody v závislosti na škodě na vozidlech v jednotlivých regionech')
    _subplot_damage(damage_df, axs[0][0], 'HKK')
    _subplot_damage(damage_df, axs[0][1], 'JHM')
    _subplot_damage(damage_df, axs[1][0], 'PHA')
    _subplot_damage(damage_df, axs[1][1], 'PLK')

    # set the only one legend for all existing subplots
    patches, labels = axs[1][1].get_legend_handles_labels()
    figure.legend(
        patches, labels, title='Příčiny nehody', frameon=False,
        loc='center', bbox_to_anchor=(0.5, 0.03), shadow=False, ncol=6
    )

    if fig_location:
        _save_fig_to_location(fig_location, figure)

    if show_figure:
        plt.show()
    plt.close(figure)


def plot_surface(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """This function will create a plot with data
       about traffic surfaces when accidents occured

    Args:
        df (pd.DataFrame) - the given dataframe with all data about accidents
        fig_location (str) - a path, where the graph will be saved
        show_figure (boolean) - flag indicating that a plot shall be shown
    """
    regions_df = _get_region_data(df)[['region', 'date', 'p16']]
    surface_df = pd.crosstab(index=[regions_df['region'], regions_df['date']],
                             columns=regions_df['p16'], dropna=False)
    surface_df.columns.categories = [
        'Jiný stav', 'Suchý neznečištěný', 'Suchý znečištěný',
        'Mokrý', 'Bláto', 'Náledí, ujetý sníh - posypané',
        'Náledí, ujetý sníh - neposypané', 'Rozlitý olej, nafta apod.',
        'Souvislý sníh', 'Náhlá změna stavu'
    ]

    figure, axs = plt.subplots(2, 2, figsize=(16, 9), sharex=True, sharey=True)
    figure.suptitle('Nehody při různém stavu povrchu vozovky v jednotlivých regionech')
    _subplot_surface(surface_df, axs[0][0], 'HKK')
    _subplot_surface(surface_df, axs[0][1], 'JHM')
    _subplot_surface(surface_df, axs[1][0], 'PHA')
    _subplot_surface(surface_df, axs[1][1], 'PLK')

    # set the only one legend for all existing subplots
    patches, labels = axs[1][1].get_legend_handles_labels()
    figure.legend(
        patches, labels, title='Stav vozovky', frameon=False,
        loc='center', bbox_to_anchor=(0.5, 0.03), shadow=False, ncol=5
    )

    if fig_location:
        _save_fig_to_location(fig_location, figure)

    if show_figure:
        plt.show()
    plt.close(figure)


if __name__ == "__main__":
    dataframe = get_dataframe("accidents.pkl.gz")
    plot_conseq(dataframe, fig_location="01_nasledky.png")
    plot_damage(dataframe, "02_priciny.png")
    plot_surface(dataframe, "03_stav.png")
