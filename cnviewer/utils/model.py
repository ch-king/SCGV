'''
Created on Dec 21, 2016

@author: lubo
'''
from scipy.cluster.hierarchy import dendrogram

import numpy as np
import pandas as pd

from utils.loader import DataLoader


class DataModel(DataLoader):
    CLONE_COLUMN = 'clone'
    SUBCLONE_COLUMN = 'subclone'
    PLOIDY_COLUMN = 'ploidy'
    GUIDE_SAMPLES_COLUMN = 'seq.unit.id'
    CHROM_COLUMN = 'chrom'

    def __init__(self, zip_filename):
        super(DataModel, self).__init__(zip_filename)
        self.seg_data = self.seg_df.ix[:, 3:].values
        self.bins, self.samples = self.seg_data.shape

        self.lmat = None
        self.Z = None

        self._chrom_x_index = None
        self._bar_extent = None

    @property
    def heat_extent(self):
        return (0, self.samples * self.interval_length,
                self.bins, 0)

    @property
    def chrom_x_index(self):
        if self._chrom_x_index is None:
            self._chrom_x_index = \
                np.where(self.seg_df[self.CHROM_COLUMN] == 23)[0][0]
        return self._chrom_x_index

    def make(self):
        self.make_linkage()
        self.make_dendrogram()
        self.make_heatmap()
        self.make_clone()
        self.make_ploidy()
        self.make_multiplier()
        self.make_error()

    def make_linkage(self):
        if self.lmat is not None:
            return
        assert len(self.tree_df) + 1 == self.samples
        df = self.tree_df.copy()

        df.height = -1 * df.height
        max_height = df.height.max()
        df.height = 1.11 * max_height - df.height
        self.lmat = df.values

    def make_dendrogram(self):
        if self.Z is not None:
            return
        self.Z = dendrogram(self.lmat, ax=None, no_plot=True)
        self.icoord = np.array(self.Z['icoord'])
        self.dcoord = np.array(self.Z['dcoord'])
        self.min_x = np.min(self.icoord)
        self.max_x = np.max(self.icoord)
        self.interval_length = (self.max_x - self.min_x) / (self.samples - 1)
        self.direct_lookup = self.Z['leaves']
        self.column_labels = \
            np.array(self.seg_df.columns[3:])[self.direct_lookup]
        self.label_midpoints = (
            np.arange(self.samples) + 0.5) * self.interval_length

    @staticmethod
    def _make_heatmap_array(df):
        color_counter = 1
        unique = df.unique()
        result = pd.Series(index=df.index)
        for val in unique:
            if val == 0:
                result[df == val] = 0
            else:
                result[df == val] = color_counter
                color_counter += 1

        return result.values

    def make_heatmap(self):
        data = np.round(self.seg_data)
        self.heatmap = data[:, self.direct_lookup]

    def make_clone(self):
        assert self.direct_lookup is not None
        labels = self.clone_df.ix[self.direct_lookup, 0].values
        assert np.all(labels == self.column_labels)

        clone_column_df = self.clone_df.iloc[self.direct_lookup, :]
        self.clone = self._make_heatmap_array(
            clone_column_df[self.CLONE_COLUMN])
        self.subclone = self._make_heatmap_array(
            clone_column_df[self.SUBCLONE_COLUMN])

    def make_ploidy(self):
        if self.PLOIDY_COLUMN not in self.guide_df.columns:
            self.ploidy = None
            return

        assert self.direct_lookup is not None
        labels = self.guide_df[self.GUIDE_SAMPLES_COLUMN].ix[
            self.direct_lookup].values
        assert np.all(labels == self.column_labels)

        ploidy_column_df = self.guide_df.iloc[self.direct_lookup, :]
        self.ploidy = self._make_heatmap_array(
            ploidy_column_df[self.PLOIDY_COLUMN])

    def make_multiplier(self):
        data = self.seg_df.iloc[:self.chrom_x_index, 3:]
        self.multiplier = data.mean(axis=1).ix[
            self.direct_lookup].values

    def make_error(self):
        df_s = self.seg_df.iloc[:self.chrom_x_index, 3:].values
        df_r = self.ratio_df.iloc[:self.chrom_x_index, 3:].values
        self.error = np.sqrt(np.sum(((df_r - df_s) / df_s)**2, axis=1))[
            self.direct_lookup]

    @property
    def bar_extent(self):
        if self._bar_extent is None:
            self._bar_extent = (
                0, self.samples * self.interval_length,
                0, 1)
        return self._bar_extent
