'''
Created on Dec 21, 2016

@author: lubo
'''
from matplotlib import cm

from views.base import ViewerBase


class ErrorViewer(ViewerBase):

    def __init__(self, model):
        super(ErrorViewer, self).__init__(model)

    def draw_error(self, ax):
        assert self.model.error is not None

        ax.imshow(
            [self.model.error],
            aspect='auto',
            interpolation='nearest',
            cmap=cm.coolwarm,  # @UndefinedVariable
            extent=self.model.bar_extent)
        ax.set_xticks([])
        ax.set_xticklabels([])
        ax.set_yticks([0.5])
        ax.set_yticklabels(["Error"])