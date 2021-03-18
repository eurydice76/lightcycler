import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.kernel.models.rawdata_model import RawDataModel
from lightcycler.gui.views.rawdata_tableview import RawDataTableView


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

        self._rawdata_tableview = RawDataTableView()
        rawdata_model = RawDataModel(self)
        self._rawdata_tableview.setModel(rawdata_model)

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

    def model(self):
        """Returns the underlying model.

        Returns:
            lightcycle.kernel.models.dynamic_matrix_model.DynamicMatrixModel: the model
        """

        return self._rawdata_tableview.model()

    def on_select_value(self, sample, gene, index):

        rawdata_model = self._rawdata_tableview.model()
        if rawdata_model is None:
            return

        row = rawdata_model.get_row(sample, gene, index)
        if row is None:
            return

        self._rawdata_tableview.setCurrentIndex(rawdata_model.index(row, 0))
