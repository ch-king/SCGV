'''
Created on Jan 17, 2017

@author: lubo
'''
import threading
import sys  # @UnusedImport
from views.controller import MainController
from utils.model import DataModel

if sys.version_info[0] < 3:
    import Tkinter as tk  # @UnusedImport @UnresolvedImport
    import ttk  # @UnusedImport @UnresolvedImport
    from tkFileDialog import askopenfilename  # @UnusedImport @UnresolvedImport
    import tkMessageBox as messagebox  # @UnusedImport @UnresolvedImport
else:
    import tkinter as tk  # @Reimport @UnresolvedImport
    from tkinter import ttk  # @UnresolvedImport @UnusedImport @Reimport
    from tkinter.filedialog \
        import askopenfilename  # @UnresolvedImport @Reimport@UnusedImport
    from tkinter.filedialog \
        import askdirectory  # @UnresolvedImport @Reimport@UnusedImport
    from tkinter import messagebox  # @UnresolvedImport @Reimport @UnusedImport


class OpenUi(object):
    DELAY = 500

    def __init__(self, main_window, master, fig):
        self.main_window = main_window
        self.master = master
        self.fig = fig
        self.model_lock = threading.RLock()

    def build_ui(self):
        frame = ttk.Frame(
            self.master,
            borderwidth=5, width=100
        )
        frame.grid(row=0, column=0)

        self.open_archive_button = ttk.Button(
            master=frame,
            width=2,
            text="OA",
            command=self._open_archive)
        self.open_archive_button.grid(column=0, row=0)
        self.open_dir_button = ttk.Button(
            master=frame,
            width=2,
            text="OD",
            command=self._open_dir)
        self.open_dir_button.grid(column=1, row=0)

        progress_frame = ttk.Frame(
            master=frame,
            borderwidth=5
        )
        progress_frame.grid(row=0, column=101)
        self.progress = ttk.Progressbar(
            progress_frame, mode='indeterminate')

    def _open_dir(self):
        print("opening directory...")
        filename = askdirectory()
        if not filename:
            print("open directory canceled...")
            return
        print(filename)
        self.filename = filename
        self._start_loading()

    def _start_loading(self):
        self.open_archive_button.config(state=tk.DISABLED)
        self.open_dir_button.config(state=tk.DISABLED)
        self.loader_task = threading.Thread(target=self._loading, args=[self])
        self.loader_task.start()
        self.master.after(4 * self.DELAY, self._on_loading_progress, self)
        self.progress.grid(row=0, column=101, sticky=tk.W + tk.E + tk.N)
        self.progress.start()

    def _open_archive(self):
        print("opening archive...")
        filename = askopenfilename(filetypes=(
            ("Zip archive", "*.zip"),
            ("Zip archive", "*.ZIP"),
            ("Zip archive", "*.Zip")))
        if not filename:
            print("openfilename canceled...")
            return
        self.filename = filename
        self._start_loading()

    def _on_loading_progress(self, *args):
        if self.loader_task.is_alive():
            self.master.after(self.DELAY, self._on_loading_progress, self)
            return

        if not self.model_lock.acquire(False):
            return

        with self.model_lock:
            if self.model:
                self.controller = MainController(self.model)
                self.controller.build_main(self.fig)
                self.progress.stop()
                self.progress.grid_remove()
                self.main_window.connect_controller(self.controller)
            else:
                self.progress.stop()
                self.progress.grid_remove()
                messagebox.showerror(
                    "Wrong file/directory type",
                    "Single Cell Genomics data set expected")

    def _loading(self, *args):
        with self.model_lock:
            try:
                print("loading '{}'".format(self.filename))
                model = DataModel(self.filename)
                print("preparing '{}'".format(self.filename))
                model.make()
                self.model = model

                return True
            except AssertionError:
                print("wrong file type: ZIP archive expected")
                return False