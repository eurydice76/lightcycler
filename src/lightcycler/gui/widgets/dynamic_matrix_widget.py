import logging

from PyQt5 import QtWidgets

from lightcycler.kernel.models.dynamic_matrix_model import DynamicMatrixModel


class DynamicMatrixWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(DynamicMatrixWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._export_pushbutton.clicked.connect(self.on_export_matrices)
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

        main_layout.addWidget(self._export_pushbutton)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._view_label = QtWidgets.QLabel('View')

        self._view_combobox = QtWidgets.QComboBox()
        self._view_combobox.addItems(['means', 'stds', 'number of values'])

        self._dynamic_matrix_tableview = QtWidgets.QTableView()
        dynamic_matrix_model = DynamicMatrixModel()
        self._dynamic_matrix_tableview.setModel(dynamic_matrix_model)

        self._export_pushbutton = QtWidgets.QPushButton('Export')

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

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

    def on_export_matrices(self):
        """Event handler which export the dynamic matrix to an excel spreadsheet.
        """

        model = self._dynamic_matrix_tableview.model()
        if model is None:
            logging.error('No data loaded yet')
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption='Export dynamic matrix as ...', filter="Excel files (*.xls *.xlsx)")
        if not filename:
            return

        model.export(filename)
