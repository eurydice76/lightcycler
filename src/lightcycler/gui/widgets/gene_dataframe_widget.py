import collections

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.kernel.models.pandas_data_model import PandasDataModel


class GeneDataFrameWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(GeneDataFrameWidget, self).__init__(*args, **kwargs)

        self._matrices = collections.OrderedDict()

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._selected_gene_combobox.currentTextChanged.connect(self.on_select_gene)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._matrix_tableview)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._matrix_tableview = CopyPastableTableView(delimiter=',')

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def model(self):
        """Return the delta CT matrix underlying model.
        """

        return self._matrix_tableview.model()

    def set_matrices(self, matrices):
        """
        """

        self._matrices = matrices

        self._selected_gene_combobox.clear()
        self._selected_gene_combobox.addItems(matrices.keys())

    def on_select_gene(self, gene):
        """
        """

        if gene not in self._matrices:
            return

        pandas_model = PandasDataModel(self._matrices[gene].round(3), self)
        self._matrix_tableview.setModel(pandas_model)
