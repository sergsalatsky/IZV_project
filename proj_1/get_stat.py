import argparse

from download import DataDownloader, os, arange
import matplotlib.pyplot as plt


def parse_arguments():
    """Function for parsing arguments
    
    Returns:
        arguments values 
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--fig_location',
        default=None,
        type=str,
        help='Save drown plot into given file path'
    )
    parser.add_argument(
        '--show_figure',
        action='store_true',
        help='Show the plot in separate frame'
    )

    return parser.parse_args()

def get_accidents_count(data_source):
    """Function for counting accidents on trffic
       in each region by year
    
    Args:
        data_source (tuple) - main data for plotting

    Returns:
        dict, with count of accidents in regions
    """
    count = dict()
    
    for idx in arange(data_source[1].shape[1]):
        year = data_source[1][3][idx][:4]
        region = data_source[1][64][idx]

        if not year in count:
            count[year] = dict()
        if not region in count[year]:
            count[year][region] = 0

        count[year][region] += 1
    
    return count


def plot_stat(data_source, fig_location = None, show_figure = False):
    """Function for drawing a plot with data about accidents on traffic

    Args:
        data_source (tuple) - main data for plotting
        fig_location (str) - a path, where the graph will be saved
        show_figure (boolean) - flag indicating that a plot shall be shown
    """
    accidents_count = get_accidents_count(data_source)

    figure, axs = plt.subplots(len(accidents_count), figsize=(16,9), sharey='col')
    figure.suptitle('Statistika nehod na silnicich v Ceske republice')

    for idx, ax in enumerate(axs):
        year = sorted(accidents_count.keys())[idx]

        ax.set_xlabel("Regiony")
        ax.set_ylabel("Pocet nehod v {}".format(year))
        ax.bar(accidents_count[year].keys(),
               accidents_count[year].values(),
               width=0.35, bottom=0, align='center',
               color='C3')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_position('zero')
        ax.margins(0.05)

    if fig_location:
        *folder, _ = os.path.split(fig_location)
        folders = '/'.join(folder)
        if folders:
            os.makedirs('/'.join(folder), exist_ok=True)
        plt.savefig(fig_location)

    if show_figure:
        plt.show()


if __name__ == "__main__":
    args = parse_arguments()
    plot_stat(DataDownloader().get_list(['PHA', 'STC', 'HHK']), args.fig_location, args.show_figure)
