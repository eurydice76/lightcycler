"""This modules implements the following classes:
    _ MainWindow
"""

import copy
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
from lightcycler.gui.widgets.genes_widget import GenesWidget
from lightcycler.gui.widgets.groups_widget import GroupsWidget
from lightcycler.gui.widgets.rawdata_widget import RawDataWidget
from lightcycler.kernel.models.rawdata_model import RawDataError, RawDataModel
from lightcycler.kernel.utils.progress_bar import progress_bar


class MainWindow(QtWidgets.QMainWindow):
    """This class implements the main window of the application.
    """

    clear_data = QtCore.pyqtSignal()

    # Signal emitted when Groups sheet of an imported workbook is read.
    groups_loaded = QtCore.pyqtSignal(list, pd.DataFrame)

    # Signal emitted when Genes sheet of an imported workbook is read.
    genes_loaded = QtCore.pyqtSignal(list, pd.DataFrame)

    # Signal emitted when Group control sheet of an imported workbook is read.
    group_control_loaded = QtCore.pyqtSignal(str)

    reset_data = QtCore.pyqtSignal()

    set_available_genes = QtCore.pyqtSignal(list)

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

        rawdata_model = self._rawdata_widget.model()
        rawdata_model.data_updated.connect(self._dynamic_matrix_widget.on_build_dynamic_matrices)

        # Fill up the available samples
        rawdata_model.data_updated.connect(self._groups_widget.on_update_samples_and_groups)

        groups_model = self._groups_widget.model()
        self._dynamic_matrix_widget.dynamic_matrices_computed.connect(groups_model.on_set_dynamic_matrices)

        self.clear_data.connect(rawdata_model.on_clear)
        self.clear_data.connect(self._groups_widget.on_clear)
        self.clear_data.connect(self._genes_widget.on_clear)

        self.reset_data.connect(rawdata_model.on_reset)

        self.groups_loaded.connect(self._groups_widget.on_load_groups)
        self.group_control_loaded.connect(self._groups_widget.on_set_group_control)

        genes_model = self._genes_widget.model()
        self._dynamic_matrix_widget.dynamic_matrices_computed.connect(genes_model.on_set_dynamic_matrices)
        self.genes_loaded.connect(self._genes_widget.on_load_genes)

        self.set_available_genes.connect(self._genes_widget.on_set_available_genes)

    def _build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._tabs, stretch=2)

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

        file_menu.addSeparator()

        import_action = QtWidgets.QAction('&Import workbook', self)
        import_action.setShortcut('Ctrl+I')
        import_action.setStatusTip('Import Excel spreadsheet')
        import_action.triggered.connect(self.on_import_excel_spreadsheet)
        file_menu.addAction(import_action)

        export_action = QtWidgets.QAction('&Export workbook', self)
        export_action.setShortcut('Ctrl+E')
        export_action.setStatusTip('Export data to an Excel spreadsheet')
        export_action.triggered.connect(self.on_export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit lightcycler')
        exit_action.triggered.connect(self.on_quit_application)
        file_menu.addAction(exit_action)

        data_menu = menubar.addMenu('&Data')

        clear_action = QtWidgets.QAction('&Clear', self)
        clear_action.setShortcut('Ctrl+D')
        clear_action.setStatusTip('Clear data')
        clear_action.triggered.connect(self.on_clear_data)
        data_menu.addAction(clear_action)

        data_menu.addSeparator()

        reset_action = QtWidgets.QAction('&Reset', self)
        reset_action.setShortcut('Ctrl+E')
        reset_action.setStatusTip('Reset data')
        reset_action.triggered.connect(self.on_reset_data)
        data_menu.addAction(reset_action)

    def _build_widgets(self):
        """Build the widgets.
        """

        self._main_frame = QtWidgets.QFrame(self)

        self._tabs = QtWidgets.QTabWidget()

        self._rawdata_widget = RawDataWidget(self)
        self._dynamic_matrix_widget = DynamicMatrixWidget(self)
        self._groups_widget = GroupsWidget(self)
        self._genes_widget = GenesWidget(self)

        self._tabs.addTab(self._rawdata_widget, 'Raw data')
        self._tabs.addTab(self._dynamic_matrix_widget, 'Dynamic_matrix')
        self._tabs.addTab(self._groups_widget, 'Groups')
        self._tabs.addTab(self._genes_widget, 'Genes')

        self._logger = QTextEditLogger(self)
        self._logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self._logger)
        logging.getLogger().setLevel(logging.INFO)

        self.setCentralWidget(self._main_frame)

        self.setGeometry(0, 0, 1200, 800)

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

    @ property
    def dynamic_matrix_widget(self):
        """Returns the dynamic matrix widget.

        Returns:
            lightcycler.gui.widgets.dynamic_matrix_widget.DynamicMatrixWidget: the widget
        """

        return self._dynamic_matrix_widget

    @ property
    def groups_widget(self):
        """Returns the groups widget.

        Returns:
            lightcycler.gui.widgets.groups_widget.GroupsWidget: the widget
        """

        return self._groups_widget

    def on_clear_data(self):
        """Clear the data.
        """

        self.clear_data.emit()

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
        self._genes_widget.export(workbook)

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
        if 'Raw data' not in sheet_names or 'Groups' not in sheet_names:
            logging.error('Invalid excel file: missing "Raw data" and/or "Groups" sheets')
            return

        logging.info('Importing {} file. Please wait ...'.format(excel_file))

        rawdata = pd.read_excel(excel_file, sheet_name='Raw data')

        rawdata_model = self._rawdata_widget.model()
        rawdata_model.rawdata = rawdata

        groups = pd.read_excel(excel_file, sheet_name='Groups')
        groups = groups.reindex(sorted(groups.columns), axis=1)
        groups = groups.astype(str)
        self.groups_loaded.emit(rawdata_model.samples, groups)

        group_control = pd.read_excel(excel_file, sheet_name='Group control', header=None)
        group_control = group_control.astype(str)
        if not group_control.empty:
            self.group_control_loaded.emit(group_control.loc[0, 0])

        genes_per_group = pd.read_excel(excel_file, sheet_name='Genes')
        self.genes_loaded.emit(rawdata_model.genes, genes_per_group)

        logging.info('... successfully imported {} file'.format(excel_file))

    def on_open_lightcycler_files(self):
        """Opens and loads lightcycler files.
        """

        # Pop up a file browser for selecting the workbooks
        data_files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open data files', '', 'Data Files (*.pdf *.PDF *.csv *.txt)')[0]
        if not data_files:
            return

        n_data_files = len(data_files)
        progress_bar.reset(n_data_files)

        n_loaded_files = 0

        rawdata_model = self._rawdata_widget.model()

        # Loop over the pig directories
        for progress, data_file in enumerate(data_files):

            # Read the pdf file and add the data to the model. Any kind of error must be caught here.
            try:
                self.statusBar().showMessage('Reading {} file ...'.format(data_file))
                rawdata_model.add_data(data_file, sort=False)

            except Exception as error:
                logging.error(str(error))
            else:
                n_loaded_files += 1

            progress_bar.update(progress+1)

        self.statusBar().showMessage('')
        logging.info('Loaded successfully {} file(s) out of {}'.format(n_loaded_files, n_data_files))

        # Sort the model.
        try:
            rawdata_model.sort()
        except RawDataError:
            pass

        if rawdata_model.rowCount() == 0:
            return

        self.set_available_genes.emit(rawdata_model.genes)

    def on_quit_application(self):
        """Quit the application.
        """

        choice = QtWidgets.QMessageBox.question(self, 'Quit', "Do you really want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()

    def on_reset_data(self):
        """Reset the rawdata, the dynamic matrix and the groups loaded intially.
        """

        self.reset_data.emit()

    @ property
    def rawdata_widget(self):
        """Returns the rawdata widget.

        Returns:
            lightcycler.gui.widgets.rawdata_widget.RawDataWidget: the widget
        """

        return self._rawdata_widget
