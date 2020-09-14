"""This modules implements the following classes:
    _ MainWindow
"""

import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets

import lightcycler
from lightcycler.__pkginfo__ import __version__
from lightcycler.gui.widgets.logger_widget import QTextEditLogger
from lightcycler.gui.widgets.rawdata_widget import RawDataWidget
from lightcycler.kernel.models.rawdata_model import RawDataError, RawDataModel
from lightcycler.kernel.utils.progress_bar import progress_bar

class MainWindow(QtWidgets.QMainWindow):
    """This class implements the main window of the application.
    """

    raw_data_loaded = QtCore.pyqtSignal(QtCore.QAbstractTableModel)

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


    def _build_widgets(self):
        """Build the widgets.
        """

        self._main_frame = QtWidgets.QFrame(self)

        self._tabs = QtWidgets.QTabWidget()
        
        self._rawdata_widget = RawDataWidget(self)

        self._tabs.addTab(self._rawdata_widget, 'Raw data')

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
                rawdata_model.add_data(pdf_file)

            except Exception as error:
                logging.error(str(error))
            else:
                n_loaded_files += 1

            progress_bar.update(progress+1)

        logging.info('Loaded successfully {} files out of {}'.format(n_loaded_files, n_pdf_files))

        # Sort the model.
        try:
            rawdata_model.sort()
        except RawDataError:
            pass

        self.raw_data_loaded.emit(rawdata_model)

