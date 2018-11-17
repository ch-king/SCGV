import sys
import traceback

import numpy as np

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, \
    QStatusBar, QFileDialog, QProgressBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, \
    QThreadPool

from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from scgv.models.model import DataModel
from scgv.utils.observer import DataObserver

import matplotlib.pyplot as plt
import matplotlib.colors as col

from scgv.views.clone import CloneViewer
from scgv.views.heatmap import HeatmapViewer
from scgv.views.sector import SectorViewer
from scgv.views.gate import GateViewer
from scgv.views.multiplier import MultiplierViewer
from scgv.views.error import ErrorViewer
import traceback
from scgv.views.dendrogram import DendrogramViewer


class WorkerSignals(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(int)

    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    status = pyqtSignal(object)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(
                *self.args, **self.kwargs,
                status=self.signals.status,
                progress=self.signals.progress,
            )
        except Exception:
            # Emit error
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            # Done
            self.signals.finished.emit()


class OpenButtons(object):

    def __init__(self, window, subject):
        # super(OpenButtons, self).__init__(subject)
        self.window = window

        self.window.toolbar.addSeparator()

        self.open_dir_action = QAction(
            QIcon("icons/folder.png"), "Open Directory", self.window)
        self.open_dir_action.setStatusTip("Open Directory button")
        self.open_dir_action.triggered.connect(self.on_open_directory_click)
        self.window.toolbar.addAction(self.open_dir_action)

        self.open_archive_action = QAction(
            QIcon("icons/archive.png"), "Open Archive", self.window)
        self.open_archive_action.setStatusTip("Open Archive button")
        self.open_archive_action.triggered.connect(self.on_open_archive_click)
        self.window.toolbar.addAction(self.open_archive_action)

        self.threadpool = QThreadPool()

    def on_open_directory_click(self, s):
        print("click open directory", s)
        dirname = QFileDialog.getExistingDirectory(
            self.window, "Open Directory")
        print(dirname)
        self._load_model(dirname)

    def on_open_archive_click(self, s):
        print("click open archive", s)
        filter = "Zip File (*.zip)"
        filename, _ = QFileDialog.getOpenFileName(
            self.window, "Open Zip File",
            ".", filter)
        print(filename)
        self._load_model(filename)

    def _load_model(self, filename):

        self.open_archive_action.setEnabled(False)
        self.open_dir_action.setEnabled(False)

        worker = Worker(self._build_model, filename)
        worker.signals.result.connect(self.window.set_model)
        worker.signals.error.connect(self._load_error)
        worker.signals.finished.connect(self._load_complete)
        self.threadpool.start(worker)

    def _load_complete(self):
        self.window.update()
        print("window updated called...")

    def _load_error(self, *args, **kwargs):
        print("_load_error: args=", args, "; kwargs=", kwargs)
        self.open_archive_action.setEnabled(True)
        self.open_dir_action.setEnabled(True)

    def _build_model(self, filename, *args, **kwargs):
            print("_build_model: args=", args, "; kwargs=", kwargs)
            model = DataModel(filename)
            model.make()
            return model


class CanvasSignals(QObject):

    profile_selected = pyqtSignal(object)


class Canvas(FigureCanvas):

    W = 0.8875
    X = 0.075

    def __init__(self):
        self.fig = Figure(figsize=(12, 8))
        self.model = None
        super(Canvas, self).__init__(self.fig)
        self.signals = CanvasSignals()

    def draw_canvas(self):
        assert self.model is not None

        ax_dendro = self.fig.add_axes(
            [self.X, 0.775, self.W, 0.175], frame_on=True)
        dendro_viewer = DendrogramViewer(self.model)
        dendro_viewer.draw_dendrogram(ax_dendro)

        ax_clone = self.fig.add_axes(
            [self.X, 0.7625, self.W, 0.0125], frame_on=True, sharex=ax_dendro)
        clone_viewer = CloneViewer(self.model)
        clone_viewer.draw_clone(ax_clone)
        ax_subclone = self.fig.add_axes(
            [self.X, 0.75, self.W, 0.0125], frame_on=True, sharex=ax_dendro)
        clone_viewer.draw_subclone(ax_subclone)

        ax_heat = self.fig.add_axes(
            [self.X, 0.20, self.W, 0.55], frame_on=True, sharex=ax_dendro)

        heatmap_viewer = HeatmapViewer(self.model)
        heatmap_viewer.draw_heatmap(ax_heat)

        ax_sector = self.fig.add_axes(
            [self.X, 0.175, self.W, 0.025], frame_on=True, sharex=ax_dendro)
        # draw sector bar
        sector_viewer = SectorViewer(self.model)
        sector_viewer.draw_sector(ax_sector)

        ax_gate = self.fig.add_axes(
            [self.X, 0.150, self.W, 0.025], frame_on=True, sharex=ax_dendro)
        gate_viewer = GateViewer(self.model)
        gate_viewer.draw_ploidy(ax_gate)

        ax_multiplier = self.fig.add_axes(
            [self.X, 0.125, self.W, 0.025], frame_on=True, sharex=ax_dendro)
        multiplier_viewer = MultiplierViewer(self.model)
        multiplier_viewer.draw_multiplier(ax_multiplier)

        ax_error = self.fig.add_axes(
            [self.X, 0.10, self.W, 0.025], frame_on=True, sharex=ax_dendro)
        error_viewer = ErrorViewer(self.model)
        error_viewer.draw_error(ax_error)
        error_viewer.draw_xlabels(ax_error)

        self.ax_label = ax_error

        plt.setp(ax_dendro.get_xticklabels(), visible=False)
        plt.setp(ax_clone.get_xticklabels(), visible=False)
        plt.setp(ax_clone.get_xticklines(), visible=False)
        plt.setp(ax_subclone.get_xticklabels(), visible=False)
        plt.setp(ax_subclone.get_xticklines(), visible=False)
        plt.setp(ax_heat.get_xticklabels(), visible=False)
        plt.setp(ax_sector.get_xticklabels(), visible=False)
        plt.setp(ax_gate.get_xticklabels(), visible=False)
        plt.setp(ax_multiplier.get_xticklabels(), visible=False)

    def redraw(self):
        if self.model is not None:
            self.draw_canvas()
            self.draw()
            self.fig.canvas.mpl_connect("button_press_event", self.onclick)

    def onclick(self, event):
        print(
            '%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
            ('double' if event.dblclick else 'single', event.button,
             event.x, event.y, event.xdata, event.ydata))
        if event.button == 3:
            sample_name = self.locate_sample_click(event)
            print("Located sample:", sample_name)
            self.signals.profile_selected.emit(sample_name)

    def set_model(self, model):
        print("Canvas: set model:", model)
        self.model = model

    def locate_sample_click(self, event):
        if event.xdata is None:
            return None
        xloc = int(event.xdata / self.model.interval_length)
        sample_name = self.model.column_labels[xloc]
        return sample_name


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("SCGV Main")

        self._main = QWidget()
        self.setCentralWidget(self._main)
        layout = QVBoxLayout(self._main)

        self.canvas = Canvas()
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(self.toolbar)

        self.setStatusBar(QStatusBar(self))
        self.open_buttons = OpenButtons(self, None)

    def set_model(self, model):
        print("set model:", model)
        self.model = model
        self.canvas.set_model(model)

    def update(self):
        if self.model is not None:
            self.canvas.redraw()
        super(MainWindow, self).update()

