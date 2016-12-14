'''
Created on Dec 2, 2016

@author: lubo
'''

import matplotlib.pyplot as plt

from utils.loader import load_df
from views.heatmap import HeatmapViewer
from views.samples import SampleViewer
from views.dendrogram import DendrogramViewer
from views.controller import HeatmapController


def main_heatmap():
    seg_filename = 'tests/data/sample.YL2671P11.5k.seg.quantal.primary.txt'
    seg_df = load_df(seg_filename)

    assert seg_df is not None

    viewer = HeatmapViewer(seg_df)

    fig = plt.figure(0, figsize=(12, 8))
    fig.suptitle(seg_filename, fontsize=10)

    ax_dendro = fig.add_axes([0.1, 0.75, 0.8, 0.2], frame_on=True)
    # draw_dendrogram(df, ax_dendro)
    viewer.draw_dendrogram(ax_dendro)
    viewer.clear_labels(ax_dendro)

    ax_heat = fig.add_axes(
        [0.1, 0.10, 0.8, 0.65], frame_on=True, sharex=ax_dendro)
    viewer.draw_heatmap(ax_heat)
    viewer.make_legend()

    plt.show()


def main_sample():
    seg_filename = \
        'tests/data/sample.YL2671P11.5k.seg.quantal.primary.txt'
    seg_df = load_df(seg_filename)

    assert seg_df is not None

    ratio_filename = \
        'tests/data/sample.YL2671P11.5k.lowratio.quantal.primary.txt'
    ratio_df = load_df(ratio_filename)

    assert ratio_df is not None

    viewer = SampleViewer(seg_df, ratio_df, ['CTB4517', 'CTB4543'])
    viewer.draw_samples()

    plt.show()


def main_dendrogram():
    seg_filename = \
        'tests/data/uber.YL2671P5_CORE_F.5k.seg.quantal.primary.csv'
    seg_df = load_df(seg_filename)
    assert seg_df is not None

    tree_filename = \
        'tests/data/YL2671P5smear1bpFisherTreePyP4Cols.csv'
    tree_df = load_df(tree_filename)
    assert tree_df is not None

    fig = plt.figure(0, figsize=(12, 8))
    fig.suptitle(seg_filename, fontsize=10)

    viewer = DendrogramViewer(seg_df, tree_df)
    ax_dendro = fig.add_axes([0.1, 0.75, 0.8, 0.2], frame_on=True)
    viewer.draw_dendrogram(ax_dendro)
    viewer.draw_labels(ax_dendro)

    plt.show()


def main_controller():
    seg_filename = \
        'tests/data/uber.YL2671P5_CORE_F.5k.seg.quantal.primary.csv'
    seg_df = load_df(seg_filename)
    assert seg_df is not None

    tree_filename = \
        'tests/data/YL2671P5smear1bpFisherTreePyP4Cols.csv'
    tree_df = load_df(tree_filename)
    assert tree_df is not None

    ratio_filename = \
        'tests/data/uber.YL2671P5_CORE_F.5k.lowratio.quantal.primary.csv'
    ratio_df = load_df(ratio_filename)

    assert ratio_df is not None

    sample_viewer = SampleViewer(seg_df, ratio_df)

    fig = plt.figure(0, figsize=(12, 8))
    fig.suptitle(seg_filename, fontsize=10)

    heatmap_viewer = HeatmapViewer(seg_df, tree_df)
    ax_dendro = fig.add_axes([0.1, 0.75, 0.8, 0.2], frame_on=True)
    heatmap_viewer.draw_dendrogram(ax_dendro)
    heatmap_viewer.clear_labels(ax_dendro)

    ax_heat = fig.add_axes(
        [0.1, 0.10, 0.8, 0.65], frame_on=True, sharex=ax_dendro)
    heatmap_viewer.draw_heatmap(ax_heat)
    heatmap_viewer.make_legend()

    controller = HeatmapController(heatmap_viewer, sample_viewer)
    controller.event_loop_connect(fig)

    plt.show()


if __name__ == '__main__':
    # main_heatmap()
    # main_sample()
    # main_dendrogram()
    main_controller()
