"""This modules implements the following classes:
    _ MainWindow
"""

import logging
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import openpyxl
import xlrd

import pandas as pd

import lightcycler
from lightcycler.__pkginfo__ import __version__
from lightcycler.gui.widgets.logger_widget import QTextEditLogger
from lightcycler.gui.widgets.dynamic_matrix_widget import DynamicMatrixWidget
from lightcycler.gui.widgets.groups_widget import GroupsWidget
from lightcycler.gui.widgets.rawdata_widget import RawDataWidget
from lightcycler.kernel.models.rawdata_model import RawDataError, RawDataModel
from lightcycler.kernel.utils.progress_bar import progress_bar


class MainWindow(QtWidgets.QMainWindow):
    """This class implements the main window of the application.
    """

    raw_data_loaded = QtCore.pyqtSignal(QtCore.QAbstractTableModel)

    build_dynamic_matrix = QtCore.pyqtSignal(QtCore.QAbstractTableModel)

    load_groups = QtCore.pyqtSignal(pd.DataFrame)

    def __init__(self, parent=None):
        """Constructor.

        Args:
            parent (QtCore.QObject): the parent window
        """

        super(MainWindow, self).__init__(parent)

        self._init_ui()

    def _build_events(self):
        """Build the signal/slots.
        """

        self.raw_data_loaded.connect(self._rawdata_widget.on_load_raw_data)
        self.raw_data_loaded.connect(self._groups_widget.on_load_raw_data)
        self.build_dynamic_matrix.connect(self._dynamic_matrix_widget.on_build_dynamic_matrix)
        self._export_pushbutton.clicked.connect(self.on_export_data)

        dynamic_matrix_model = self._dynamic_matrix_widget.model()
        groups_model = self._groups_widget.model()

        dynamic_matrix_model.propagate_means.connect(groups_model.on_set_dynamic_matrix)

        self.load_groups.connect(groups_model.on_load_groups)

    def _build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._tabs, stretch=2)

        main_layout.addWidget(self._export_pushbutton)

        main_layout.addWidget(self._logger.widget, stretch=1)

        self._main_frame.setLayout(main_layout)

    def _build_menu(self):
        """Build the menu.
        """

        menubar = self.menuBar()

        file_menu = menubar.addMenu('&File')

        file_action = QtWidgets.QAction('&Open lightcycler files', self)
        file_action.setShortcut('Ctrl+O')
        file_action.setStatusTip('Open lightcycler (pdf) files')
        file_action.triggered.connect(self.on_open_lightcycler_files)
        file_menu.addAction(file_action)

        import_action = QtWidgets.QAction('&Import Excel spreasheet', self)
        import_action.setShortcut('Ctrl+U')
        import_action.setStatusTip('Import Excel spreadsheet which contains the raw data and the dynmaic matrix')
        import_action.triggered.connect(self.on_import_excel_spreadsheet)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit pigcel')
        exit_action.triggered.connect(self.on_quit_application)
        file_menu.addAction(exit_action)

    def _build_widgets(self):
        """Build the widgets.
        """

        self._main_frame = QtWidgets.QFrame(self)

        self._tabs = QtWidgets.QTabWidget()

        self._rawdata_widget = RawDataWidget(self)
        self._dynamic_matrix_widget = DynamicMatrixWidget(self)
        self._groups_widget = GroupsWidget(self)

        self._tabs.addTab(self._rawdata_widget, 'Raw data')
        self._tabs.addTab(self._dynamic_matrix_widget, 'Dynamic_matrix')
        self._tabs.addTab(self._groups_widget, 'Groups')

        self._export_pushbutton = QtWidgets.QPushButton('Export')

        self._logger = QTextEditLogger(self)
        self._logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self._logger)
        logging.getLogger().setLevel(logging.INFO)

        self.setCentralWidget(self._main_frame)

        self.setGeometry(0, 0, 1200, 1100)

        self.setWindowTitle('lightcycler {}'.format(__version__))

        self._progress_label = QtWidgets.QLabel('Progress')
        self._progress_bar = QtWidgets.QProgressBar()
        progress_bar.set_progress_widget(self._progress_bar)
        self.statusBar().showMessage('lightcycler {}'.format(__version__))
        self.statusBar().addPermanentWidget(self._progress_label)
        self.statusBar().addPermanentWidget(self._progress_bar)

        icon_path = os.path.join(lightcycler.__path__[0], "icons", "lightcycler.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.show()

    def _init_ui(self):
        """Initializes the ui.
        """

        self._build_widgets()

        self._build_layout()

        self._build_menu()

        self._build_events()

    def on_export_data(self):
        """Event handler which export the raw data to an excel spreadsheet.
        """

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export data as ...', filter="Excel files (*.xls *.xlsx)")
        if not filename:
            return

        basename, ext = os.path.splitext(filename)
        if ext not in ['.xls', '.xlsx']:
            filename = basename + '.xlsx'

        workbook = openpyxl.Workbook()

        # Remove the first empty sheet created by default
        workbook.remove_sheet(workbook.get_sheet_by_name('Sheet'))

        self._rawdata_widget.export(workbook)
        self._dynamic_matrix_widget.export(workbook)
        self._groups_widget.export(workbook)

        try:
            workbook.save(filename)
        except PermissionError as error:
            logging.error(str(error))
        else:
            logging.info('Exported successfully raw data to {} file'.format(filename))

    def on_import_excel_spreadsheet(self):
        """Event handler which import excel spread sheets which contains the raw data and the dynamic matrix.
        """

        # Pop up a file browser for selecting the workbooks
        excel_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Open excel files', '', 'Excel Files (*.xls *.xlsx)')[0]
        if not excel_file:
            return

        workbook = xlrd.open_workbook(excel_file)
        sheet_names = workbook.sheet_names()
        if 'raw data' not in sheet_names or 'groups' not in sheet_names:
            logging.error('Invalid excel file: missing "raw data" and/or "groups" sheets')
            return

        rawdata = pd.read_excel(excel_file, sheet_name='raw data')

        rawdata_model = RawDataModel(self)

        rawdata_model.rawdata = rawdata

        groups = pd.read_excel(excel_file, sheet_name='groups')

        self.raw_data_loaded.emit(rawdata_model)

        self.build_dynamic_matrix.emit(rawdata_model)

        self.load_groups.emit(groups)

        logging.info('Successfully imported {} file'.format(excel_file))

    def on_open_lightcycler_files(self):
        """Event handler which loads several lightcycler files.
        """

        # Pop up a file browser for selecting the workbooks
        pdf_files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open data files', '', 'Data Files (*.pdf *.PDF)')[0]
        if not pdf_files:
            return

        rawdata_model = RawDataModel(self)

        n_pdf_files = len(pdf_files)
        progress_bar.reset(n_pdf_files)

        n_loaded_files = 0

        # Loop over the pig directories
        for progress, pdf_file in enumerate(pdf_files):

            # Read the pdf file and add the data to the model. Any kind of error must be caught here.
            try:
                self.statusBar().showMessage('Reading {} file ...'.format(pdf_file))
                rawdata_model.add_data(pdf_file)

            except Exception as error:
                logging.error(str(error))
            else:
                n_loaded_files += 1

            progress_bar.update(progress+1)

        self.statusBar().showMessage('')
        logging.info('Loaded successfully {} files out of {}'.format(n_loaded_files, n_pdf_files))

        # Sort the model.
        try:
            rawdata_model.sort()
        except RawDataError:
            pass

        self.raw_data_loaded.emit(rawdata_model)

        self.build_dynamic_matrix.emit(rawdata_model)

    def on_quit_application(self):
        """Event handler which quits the application.
        """

        choice = QtWidgets.QMessageBox.question(self, 'Quit', "Do you really want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
