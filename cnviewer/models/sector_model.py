'''
Created on Jan 10, 2017

@author: lubo
'''
import numpy as np
from models.model_delegate import ModelDelegate


class SectorsDataModel(ModelDelegate):

    def __init__(self, model):
        super(SectorsDataModel, self).__init__(model)
        assert self.model.sector is not None

        self.bins, self.samples = self.model.seg_data.shape

    def build_ordering(self):
        index = np.array(self.model.Z['leaves'])
        order = np.arange(len(index))

        sector = self.model.sector
        self.sector_mapping = self.model.sector_mapping

        res = np.lexsort(
            (
                order,
                sector,
            ))

        return index[res]

    def make(self):
        ordering = self.build_ordering()

        self.column_labels = np.array(self.data.seg_df.columns[3:])[ordering]
        self.label_midpoints = (
            np.arange(self.samples) + 0.5) * self.interval_length

        self.clone, self.subclone = self.make_clone(ordering=ordering)

        self.heatmap = self.model.make_heatmap(ordering=ordering)
        self.gate = self.model.make_gate(ordering=ordering)
        self.sector, self.sector_mapping = \
            self.model.make_sector(ordering=ordering)
        self.multiplier = self.model.make_multiplier(ordering=ordering)
        self.error = self.model.make_error(ordering=ordering)


class SingleSectorDataModel(ModelDelegate):

    def __init__(self, model, sector_id):
        super(SingleSectorDataModel, self).__init__(model)
        assert self.model.sector is not None
        assert self.model.sector_mapping is not None

        self.sector_id = sector_id
        assert self.sector_id in self.model.sector_mapping
        self.bins, self.samples = self.model.seg_data.shape

    def build_ordering(self):
        index = np.array(self.model.Z['leaves'])
        order = np.arange(len(index))

        sector = self.model.sector
        self.sector_mapping = self.model.sector_mapping

        res = np.lexsort(
            (
                order,
                sector,
            ))

        return index[res]

    def make(self):
        ordering = self.build_ordering()
        self.sector, self.sector_mapping = \
            self.model.make_sector(ordering=ordering)

        sector_val = self.sector_mapping[self.sector_id]
        sector_index = self.sector == sector_val

        self.column_labels = np.array(self.data.seg_df.columns[3:])[ordering]
        self.column_labels = self.column_labels[sector_index]

        self.samples = len(self.column_labels)
        self.interval_length = (self.model.max_x - self.model.min_x) / \
            (self.samples - 1)
        self.label_midpoints = (
            np.arange(self.samples) + 0.5) * self.interval_length
        self.bins = self.model.bins

        self.clone, self.subclone = self.make_clone(ordering=ordering)
        if self.clone is not None:
            self.clone = self.clone[sector_index]
            self.subclone = self.subclone[sector_index]

        self.heatmap = self.model.make_heatmap(ordering=ordering)
        self.heatmap = self.heatmap[:, sector_index]

        self.gate = self.model.make_gate(ordering=ordering)
        if self.gate is not None:
            self.gate = self.gate[sector_index]

        if self.sector is not None:
            self.sector = self.sector[sector_index]

        self.multiplier = self.model.make_multiplier(ordering=ordering)
        if self.multiplier is not None:
            self.multiplier = self.multiplier[sector_index]

        self.error = self.model.make_error(ordering=ordering)
        if self.error is not None:
            self.error = self.error[sector_index]
