import logging

from PyQt5 import QtWidgets


class RawDataWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(RawDataWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._rawdata_tableview)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._rawdata_tableview = QtWidgets.QTableView()

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()

    def export(self, workbook):
        """Event handler which export the raw data to an excel spreadsheet.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        model = self._rawdata_tableview.model()
        if model is None:
            logging.error('No data loaded yet')
            return

        model.export(workbook)

    def on_load_raw_data(self, rawdata_model):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        self._rawdata_tableview.setModel(rawdata_model)
