from PyQt5 import QtWidgets

from lightcycler.kernel.models.groups_model import GroupsModel
from lightcycler.kernel.models.grubbs_data_model import GrubbsDataModel


class GrubbsDataDialog(QtWidgets.QDialog):

    def __init__(self, grubbs_data, main_window, *args, **kwargs):

        super(GrubbsDataDialog, self).__init__(main_window, *args, **kwargs)

        self._grubbs_data = grubbs_data

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._selected_gene_combobox.currentIndexChanged.connect(self.on_select_gene)
        self._selected_zone_combobox.currentIndexChanged.connect(self.on_select_zone)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._grubbs_data_tableview)

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)
        hlayout.addWidget(self._selected_zone_label)
        hlayout.addWidget(self._selected_zone_combobox)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        self.setGeometry(0, 0, 600, 400)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._grubbs_data_tableview = QtWidgets.QTableView()
        self._grubbs_data_tableview.setModel(None)

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()
        self._selected_gene_combobox.addItems(self._grubbs_data.keys())

        self._selected_zone_label = QtWidgets.QLabel('Zone')
        self._selected_zone_combobox = QtWidgets.QComboBox()
        self._selected_zone_combobox.addItems(GroupsModel.student_test_zones)

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

        self.on_select_gene(0)

    def on_select_gene(self, index):
        """Select a gene and update the Grubbs data table view.

        Args:
            index (int): the index of the select gene
        """

        gene = self._selected_gene_combobox.currentText()

        zone = self._selected_zone_combobox.currentText()

        cp_values, outliers_indices = self._grubbs_data[gene][zone]

        grubbs_data_model = GrubbsDataModel(cp_values, outliers_indices)

        self._grubbs_data_tableview.setModel(grubbs_data_model)

    def on_select_zone(self, index):
        """Select a zone and update the Grubbs data table view.

        Args:
            index (int): the index of the select gene
        """

        gene = self._selected_gene_combobox.currentText()

        zone = self._selected_zone_combobox.currentText()

        cp_values, outliers_indices = self._grubbs_data[gene][zone]

        grubbs_data_model = GrubbsDataModel(cp_values, outliers_indices)

        self._grubbs_data_tableview.setModel(grubbs_data_model)
