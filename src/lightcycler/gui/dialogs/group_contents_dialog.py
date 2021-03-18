from PyQt5 import QtWidgets

from lightcycler.gui.views.group_contents_tableview import GroupContentsTableView
from lightcycler.kernel.models.group_contents_model import GroupContentsModel


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

        main_layout.addWidget(self._group_contents_tableview)

        main_layout.addLayout(hlayout)

        self.setGeometry(0, 0, 600, 400)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._group_contents_tableview = GroupContentsTableView(self)

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()
        self._selected_gene_combobox.addItems(self._dynamic_matrix.index)

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

        self.on_select_gene(0)

    def on_select_gene(self, index):
        """

        Args:
            index (int): the index of the select gene
        """

        gene = self._selected_gene_combobox.currentText()

        values_per_sample = []
        for sample in self._samples:
            values_per_sample.append((sample, gene, self._dynamic_matrix[sample].loc[gene]))

        group_contents_model = GroupContentsModel(values_per_sample, self)

        self._group_contents_tableview.setModel(group_contents_model)
        self._group_contents_tableview.selectionModel().selectionChanged.connect(self.on_select_value)

        dynamic_matrix_model = self._main_window.dynamic_matrix_widget.model()
        rawdata_model = self._main_window.rawdata_widget.model()

        group_contents_model.change_value.connect(rawdata_model.on_change_value)
        group_contents_model.remove_value.connect(rawdata_model.on_remove_value)

        group_contents_model.change_value.connect(dynamic_matrix_model.on_change_value)
        group_contents_model.remove_value.connect(dynamic_matrix_model.on_remove_value)
        group_contents_model.select_value.connect(self._main_window.rawdata_widget.on_select_value)

    def on_select_value(self, event):
        """Event handler which will show the selected value in the raw data table view.
        """

        current_index = self._group_contents_tableview.currentIndex()

        group_contents_model = self._group_contents_tableview.model()

        sample = group_contents_model.data(current_index, GroupContentsModel.sample)

        gene = group_contents_model.data(current_index, GroupContentsModel.gene)

        index = current_index.column()

        group_contents_model.select_value.emit(sample, gene, index)
