from PyQt5 import QtWidgets

from lightcycler.gui.views.sample_contents_tableview import SampleContentsTableView
from lightcycler.kernel.models.sample_contents_model import SampleContentsModel


class GroupContentsDialog(QtWidgets.QDialog):

    def __init__(self, dynamic_matrix, samples, main_window, *args, **kwargs):

        super(GroupContentsDialog, self).__init__(main_window, *args, **kwargs)

        self._dynamic_matrix = dynamic_matrix

        self._samples = samples

        self._main_window = main_window

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._selected_gene_combobox.currentIndexChanged.connect(self.on_select_gene)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)
        hlayout.addStretch()

        main_layout.addWidget(self._values_per_sample_tableview)

        main_layout.addLayout(hlayout)

        self.setGeometry(0, 0, 600, 400)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._values_per_sample_tableview = SampleContentsTableView(self)

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()
        self._selected_gene_combobox.addItems(self._dynamic_matrix.index)

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

        self.on_select_gene(0)

    def on_select_gene(self, index):
        """Event handler which updates the means and errors plot for the selected gene.

        Args:
            index (int): the index of the select gene
        """

        gene = self._selected_gene_combobox.currentText()

        values_per_sample = []
        for sample in self._samples:
            values_per_sample.append((sample, gene, self._dynamic_matrix[sample].loc[gene]))

        sample_contents_model = SampleContentsModel(values_per_sample, self)

        self._values_per_sample_tableview.setModel(sample_contents_model)
        self._values_per_sample_tableview.selectionModel().selectionChanged.connect(self.on_select_value)

        dynamic_matrix_model = self._main_window.dynamic_matrix_widget.model()
        rawdata_model = self._main_window.rawdata_widget.model()

        sample_contents_model.remove_value.connect(rawdata_model.on_remove_value)
        sample_contents_model.change_value.connect(self._main_window.rawdata_widget.on_change_value)
        sample_contents_model.remove_value.connect(dynamic_matrix_model.on_remove_value)

    def on_select_value(self, event):
        """Event handler which will show the selected value in the raw data table view.
        """

        current_index = self._values_per_sample_tableview.currentIndex()

        sample_contents_model = self._values_per_sample_tableview.model()

        sample = sample_contents_model.data(current_index, SampleContentsModel.sample)

        gene = sample_contents_model.data(current_index, SampleContentsModel.gene)

        index = current_index.column()

        sample_contents_model.change_value.emit(sample, gene, index)
