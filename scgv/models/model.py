'''
Created on Dec 21, 2016

@author: lubo
'''
from scipy.cluster.hierarchy import dendrogram
from scipy.cluster.hierarchy import linkage

import numpy as np
import pandas as pd

from models.loader import DataLoader


class BaseModel(object):
    CLONE_COLUMN = 'clone'
    SUBCLONE_COLUMN = 'subclone'
    GATE_COLUMN = 'gate'
    CHROM_COLUMN = 'chrom'
    SECTOR_COLUMN = 'sector'
    PATHOLOGY_COLUMN = 'Pathology'

    def __init__(self, data):
        self.data = data
        self.seg_data = self.data.seg_df.ix[:, 3:].values
        self.bins, self.samples = self.seg_data.shape
        self.lmat = None
        self.Z = None

        self._chrom_x_index = None
        self._bar_extent = None
        self._heat_extent = None

        self.interval_length = None

    @property
    def pathology(self):
        if self.data is not None:
            return self.data.pathology
        return None

    @property
    def bar_extent(self):
        if self._bar_extent is None:
            self._bar_extent = (
                0, self.samples * self.interval_length,
                0, 1)
        return self._bar_extent

    @property
    def heat_extent(self):
        if self._heat_extent is None:
            self._heat_extent = (0, self.samples * self.interval_length,
                                 self.bins, 0)
        return self._heat_extent

    @property
    def chrom_x_index(self):
        if self._chrom_x_index is None:
            self._chrom_x_index = \
                np.where(self.data.seg_df[self.CHROM_COLUMN] == 23)[0][0]
        return self._chrom_x_index

    def calc_chrom_lines(self):
        chrom_lines = self.calc_chrom_lines_index()
        return np.array(self.data.seg_df['abspos'][chrom_lines][:])

    def calc_chrom_lines_index(self):
        df = self.data.seg_df
        chrom_pos = df.chrom.values
        chrom_shift = np.roll(chrom_pos, -1)
        chrom_boundaries = chrom_pos != chrom_shift
        chrom_boundaries[0] = True
        chrom_lines = np.where(chrom_boundaries)
        return chrom_lines[0]

    def make(self):
        self.lmat = self.make_linkage()
        self.Z = self.make_dendrogram(self.lmat)
        self.ordering = self.make_ordering()
        self.column_labels = self.make_column_labels(
            ordering=self.ordering)
        self.interval_length = self.make_interval_length(self.Z)

        self.label_midpoints = self.make_label_midpoints()

        self.heatmap = self.make_heatmap(
            ordering=self.ordering)

        self.clone, self.subclone = self.make_clone(
            ordering=self.ordering)
        self.gate = self.make_gate(
            ordering=self.ordering)
        self.sector, self.sector_mapping = self.make_sector(
            ordering=self.ordering)
        self.multiplier = self.make_multiplier(
            ordering=self.ordering)
        self.error = self.make_error(
            ordering=self.ordering)

    def make_linkage(self):
        if self.data.tree_df is None:
            return linkage(self.seg_data.transpose(), method="ward")
        else:
            assert len(self.data.tree_df) + 1 == self.samples
            df = self.data.tree_df.copy()

            df.height = -1 * df.height
            max_height = df.height.max()
            df.height = 1.11 * max_height - df.height
            return df.values

    def make_dendrogram(self, lmat):
        Z = dendrogram(
            lmat, ax=None, no_plot=True, color_threshold=99999999)
        return Z

    def make_label_midpoints(self):
        return (np.arange(self.samples) + 0.5) * self.interval_length

    def make_ordering(self):
        return np.array(self.Z['leaves'])

    def make_column_labels(self, ordering):
        return np.array(self.data.seg_df.columns[3:])[ordering]

    def make_interval_length(self, Z):
        icoord = np.array(Z['icoord'])
        min_x = np.min(icoord)
        max_x = np.max(icoord)
        samples = len(Z['leaves'])
        interval_length = (max_x - min_x) / (samples - 1)
        return interval_length

    @classmethod
    def _reset_heatmap_color(cls):
        cls.heatmap_color_counter = 1

    @classmethod
    def _make_heatmap_array(cls, df):
        unique = df.unique()
        unique.sort()
        mapping = {}

        result = pd.Series(index=df.index)
        for val in unique:
            if val == 0:
                result[df == val] = 0
            else:
                mapping[val] = cls.heatmap_color_counter
                result[df == val] = cls.heatmap_color_counter
                cls.heatmap_color_counter += 1

        return result.values, mapping

    def make_heatmap(self, ordering):
        data = np.round(self.seg_data)
        return data[:, ordering]

    def make_featuremat(self, ordering):
        if self.data.features_df is None or self.data.featuremat_df is None:
            return None

        assert self.bins is not None
        assert self.samples is not None
        assert self.data.features_df is not None
        assert self.data.featuremat_df is not None

        self.data.featuremat_df = \
            self.data.featuremat_df.ix[:, ordering].copy()
        assert np.all(list(self.data.featuremat_df.columns) ==
                      self.column_labels)

        features = np.zeros((self.bins, self.samples))
        negative = self.data.features_df[self.data.features_df.sign == -1].bin
        positive = self.data.features_df[self.data.features_df.sign == 1].bin

        # assert len(negative) + len(positive) == self.bins
        features[negative, :] = \
            -1 * self.data.featuremat_df.ix[negative.index, :].values
        features[positive, :] = \
            +1 * self.data.featuremat_df.ix[positive.index, :].values

        psi = int(self.bins / 600)
        kernel = np.ones(2 * psi)
        return np.apply_along_axis(
            np.convolve,
            0,
            features,
            kernel,
            'same')

    def make_clone(self, ordering):
        assert ordering is not None
        if self.data.clone_df is None:
            return None, None

        clone_df = self.data.clone_df
        self._reset_heatmap_color()
        clone, clone_mapping = self._make_heatmap_array(
            clone_df[self.CLONE_COLUMN])
        subclone, subclone_mapping = self._make_heatmap_array(
            clone_df[self.SUBCLONE_COLUMN])

        mapping = clone_mapping
        mapping.update(subclone_mapping)
        # print("clone/subclone", mapping)

        return clone[ordering], subclone[ordering]

    EPCAM = {
        '2C EpCAM Neg': 2,
        '<2C EpCAM Pos': 1.5,
        '>2C-4C EpCAM Pos': 3,
        '4C EpCAM Pos': 4,
        '2C Rt EpCAM Pos': 2.25,
        '2C Lt EpCAM Pos': 1.75,
        '>4C EpCAM Pos': 5,
        '2C EpCAM Pos': 2,
        '>2C EpCAM Pos': 2.5,
    }
    GATE_MAPPING = {
        '4C': 4,
        '2C': 2,
        '2C Rt': 2.25,
        '2C EpCAM Neg': 1.95,
        '>2C': 2.5,
        '<2C EpCAM Pos': 1.5,
        '>2C-4C EpCAM Pos': 2.5,
        '4C EpCAM Pos': 4,
        '2C Rt EpCAM Pos': 2,
        '2C Lt EpCAM Pos': 2,
        '>4C EpCAM Pos': 4,
        '2C EpCAM Pos': 2,
        '>2C EpCAM Pos': 2.5,
        '2C Lt': 1.75,
        '<2C': 1.5,
        '>2C-4C': 3,
        '>2C-4C Lt': 2.75,
        '>2C-4C Rt': 3.25,
        '>4C': 5,

        '2C EpCAM Neg': 2,
        '<2C EpCAM Pos': 1.5,
        '>2C-4C EpCAM Pos': 3,
        '4C EpCAM Pos': 4,
        '2C Rt EpCAM Pos': 2.25,
        '2C Lt EpCAM Pos': 1.75,
        '>4C EpCAM Pos': 5,
        '2C EpCAM Pos': 2,
        '>2C EpCAM Pos': 2.5,
    }

    def make_gate(self, ordering):
        if self.data.guide_df is None:
            return None

        if self.GATE_COLUMN not in self.data.guide_df.columns:
            return None

        gate_column_df = self.data.guide_df.iloc[ordering, :]
        res = list(map(
            lambda g: self.GATE_MAPPING.get(g, 2),
            gate_column_df[self.GATE_COLUMN].values
        ))
        return np.array(res)

    def make_sector(self, ordering):
        if self.data.guide_df is None:
            return None, None
        if(self.SECTOR_COLUMN not in self.data.guide_df.columns):
            return None, None
        sector_df = self.data.guide_df[self.SECTOR_COLUMN]
        self._reset_heatmap_color()
        sector, sector_mapping = self._make_heatmap_array(sector_df)

        return sector[ordering], sector_mapping

    def make_multiplier(self, ordering):
        data = self.data.seg_df.iloc[:self.chrom_x_index, 3:]
        multiplier = data.mean().ix[ordering]
        return multiplier.values

    def make_error(self, ordering):
        if self.data.ratio_df is None:
            return None
        df_s = self.data.seg_df.iloc[:self.chrom_x_index, 3:].values
        df_r = self.data.ratio_df.iloc[:self.chrom_x_index, 3:].values
        return np.sqrt(np.sum(((df_r - df_s) / df_s)**2, axis=0))[ordering]

    def make_sectors_legend(self):
        if self.data.guide_df is None:
            return None
        sectors = self.data.guide_df[self.SECTOR_COLUMN].unique()
        sectors.sort()

        result = []
        for sector in sectors:
            sector_df = self.data.guide_df[
                self.data.guide_df[self.SECTOR_COLUMN] == sector]
            pathology = sector_df[self.PATHOLOGY_COLUMN].values[0]
            if not np.all(sector_df[self.PATHOLOGY_COLUMN] == pathology):
                print("single sector '{}'; different pathologies: {}".format(
                    sector,
                    sector_df[self.PATHOLOGY_COLUMN].unique()))
            result.append((sector, str(pathology).strip()))
        return result


class DataModel(BaseModel):

    def __init__(self, filename):
        self.data = DataLoader(filename)
        self.data.load()
        self.data.filter_cells()
        self.data.order_cells()

        super(DataModel, self).__init__(self.data)