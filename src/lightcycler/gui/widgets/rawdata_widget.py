import logging

from PyQt5 import QtWidgets

class RawDataWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(RawDataWidget,self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._export_pushbutton.clicked.connect(self.on_export_rawdata)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._rawdata_tableview)

        main_layout.addWidget(self._export_pushbutton)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._rawdata_tableview = QtWidgets.QTableView()

        self._export_pushbutton = QtWidgets.QPushButton('Export')

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def on_export_rawdata(self):
        """Event handler which export the raw data to an excel spreadsheet.
        """

        model = self._rawdata_tableview.model()
        if model is None:
            logging.error('No data loaded yet')
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export raw data as ...', filter="Excel files (*.xls *.xlsx)")
        if not filename:
            return

        model.export(filename)

    def on_load_raw_data(self, rawdata_model):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        self._rawdata_tableview.setModel(rawdata_model)