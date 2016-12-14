'''
Created on Dec 14, 2016

@author: lubo
'''
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import numpy as np
from utils.color_map import ColorMap
from views.dendrogram import DendrogramViewer


class HeatmapViewer(DendrogramViewer):

    def __init__(self, seg_df, tree_df=None):
        super(HeatmapViewer, self).__init__(seg_df, tree_df)
        self.cmap = ColorMap.make_cmap01()
        self.sample_list = []

    def make_legend(self):
        copynum_patches = []
        for color in self.cmap.colors.colors:
            copynum_patches.append(
                patches.Rectangle((0, 0), 0, 0, facecolor=color))
        plt.figlegend(copynum_patches, self.COPYNUM_LABELS, "upper right",
                      title="Copy #", prop={'size': 10})

    def draw_heatmap(self, ax):
        heat_extent = (0, self.samples * self.interval_length,
                       self.bins, 0)
        data = np.round(self.seg_data)

        ax.imshow(data[:, self.direct_lookup],
                  aspect='auto',
                  interpolation='nearest',
                  cmap=self.cmap.colors,
                  norm=self.cmap.norm,
                  extent=heat_extent)
        ax.set_xticks(self.label_midpoints)
        ax.set_xticklabels(self.column_labels,
                           rotation='vertical',
                           fontsize=10)
        chrom_lines = self.calc_chrom_lines_pos(self.seg_df)
        for chrom_line in chrom_lines:
            plt.axhline(y=chrom_line, color="#000000", linewidth=1)
        chrom_labelspos = self.calc_chrom_labels_pos(chrom_lines)
        ax.set_yticks(chrom_labelspos)
        ax.set_yticklabels(self.CHROM_LABELS, fontsize=9)
