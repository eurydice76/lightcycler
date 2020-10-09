import logging

from PyQt5 import QtWidgets

from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.kernel.models.dynamic_matrix_model import DynamicMatrixModel


class DynamicMatrixWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(DynamicMatrixWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._view_combobox.currentIndexChanged.connect(self.on_change_dynamic_matrix_view)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._view_label)
        hlayout.addWidget(self._view_combobox)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        main_layout.addWidget(self._dynamic_matrix_tableview)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._view_label = QtWidgets.QLabel('View')

        self._view_combobox = QtWidgets.QComboBox()
        self._view_combobox.addItems(['means', 'stdevs', 'number of values'])

        self._dynamic_matrix_tableview = CopyPastableTableView(delimiter='\n')
        dynamic_matrix_model = DynamicMatrixModel()
        self._dynamic_matrix_tableview.setModel(dynamic_matrix_model)

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def export(self, workbook):
        """Event handler which export the raw data to an excel spreadsheet.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        model = self._dynamic_matrix_tableview.model()
        if model is None:
            logging.error('No data loaded yet')
            return

        model.export(workbook)

    def model(self):
        """Returns the underlying model.

        Returns:
            lightcycle.kernel.models.dynamic_matrix_model.DynamicMatrixModel: the model
        """

        return self._dynamic_matrix_tableview.model()

    def on_build_dynamic_matrix(self, rawdata_model):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        self._dynamic_matrix_tableview.model().set_dynamic_matrix(rawdata_model)

    def on_change_dynamic_matrix_view(self, idx):
        """Event handler which changes the view of the dynamic matrix. Can be the mean, the std or the number of values.
        """

        if idx not in range(3):
            return

        self._dynamic_matrix_tableview.model().set_view(idx)
