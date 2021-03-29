import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.dialogs.ct_power_dialog import CTPowerDialog
from lightcycler.gui.views.droppable_listview import DroppableListView
from lightcycler.gui.widgets.gene_dataframe_widget import GeneDataFrameWidget
from lightcycler.kernel.models.available_genes_model import AvailableGenesModel
from lightcycler.kernel.models.droppable_model import DroppableModel
from lightcycler.kernel.models.genes_model import GenesModel
from lightcycler.kernel.models.pandas_data_model import PandasDataModel


class GenesWidget(QtWidgets.QWidget):

    def __init__(self, main_window, *args, **kwargs):

        super(GenesWidget, self).__init__(main_window, *args, **kwargs)

        self._main_window = main_window

        self._genes_model = None

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._reset_genes_pushbutton.clicked.connect(self.on_reset)
        self._compute_rq_matrix_pushbutton.clicked.connect(self.on_compute_rq_matrix)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Available genes'))
        vlayout.addWidget(self._available_genes_listview)
        hlayout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Reference genes'))
        vlayout.addWidget(self._reference_genes_listview)
        hlayout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Interest genes'))
        vlayout.addWidget(self._interest_genes_listview)
        hlayout.addLayout(vlayout)

        main_layout.addLayout(hlayout)

        main_layout.addWidget(self._reset_genes_pushbutton)

        rq_matrix_layout = QtWidgets.QHBoxLayout()

        rq_matrix_layout.addWidget(self._compute_rq_matrix_pushbutton, stretch=4)

        main_layout.addLayout(rq_matrix_layout)

        main_layout.addWidget(self._tabs, stretch=2)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._available_genes_listview = DroppableListView(self)
        self._available_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._available_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._available_genes_listview.setDragEnabled(True)

        self._reference_genes_listview = DroppableListView(self)
        self._reference_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._reference_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._reference_genes_listview.setDragEnabled(True)
        reference_genes_model = DroppableModel(self)
        self._reference_genes_listview.setModel(reference_genes_model)

        self._interest_genes_listview = DroppableListView(self)
        self._interest_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._interest_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._interest_genes_listview.setDragEnabled(True)
        interest_genes_model = DroppableModel(self)
        self._interest_genes_listview.setModel(interest_genes_model)

        self._reset_genes_pushbutton = QtWidgets.QPushButton('Reset')

        self._compute_rq_matrix_pushbutton = QtWidgets.QPushButton('Compute RQ matrix')

        self._tabs = QtWidgets.QTabWidget()

        self._delta_ct_matrices_widget = GeneDataFrameWidget(self)
        self._pow_delta_ct_matrices_widget = GeneDataFrameWidget(self)
        self._geom_means_widget = QtWidgets.QTableView()
        self._ratio_matrices_widget = GeneDataFrameWidget(self)
        self._ratio_matrices_per_group_widget = GeneDataFrameWidget(self)

        self._tabs.addTab(self._delta_ct_matrices_widget, 'Delta CT matrix')
        self._tabs.addTab(self._pow_delta_ct_matrices_widget, 'Pow Delta CT matrix')
        self._tabs.addTab(self._geom_means_widget, 'Geom. means')
        self._tabs.addTab(self._ratio_matrices_widget, 'Ratio matrix')
        self._tabs.addTab(self._ratio_matrices_per_group_widget, 'Ratio per group')

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

        rawdata_model = self._main_window.rawdata_widget.model()
        groups_model = self._main_window.groups_widget.model()
        reference_genes_model = self._reference_genes_listview.model()
        interest_genes_model = self._interest_genes_listview.model()

        self._genes_model = GenesModel(rawdata_model,
                                       groups_model,
                                       reference_genes_model,
                                       interest_genes_model)

    def model(self):
        """Returns the underlying composite model.

        Returns:
            lightcycler.kernel.models.genes_model.GenesModel
        """

        return self._genes_model

    def on_compute_rq_matrix(self):
        """Compute the RQ matrix.
        """

        rawdata_model = self._main_window.rawdata_widget.model()
        genes = rawdata_model.genes

        dialog = CTPowerDialog(genes)

        if dialog.exec_():
            self._genes_model.set_ct_power_per_gene(dialog.ct_powers)
            self._genes_model.compute_rq_matrix()
            self._delta_ct_matrices_widget.set_matrices(self._genes_model.delta_ct_matrices)
            self._pow_delta_ct_matrices_widget.set_matrices(self._genes_model.pow_delta_ct_matrices)
            self._geom_means_widget.setModel(PandasDataModel(self._genes_model.geom_means.round(3), self))
            self._ratio_matrices_widget.set_matrices(self._genes_model.ratio_matrices)
            self._ratio_matrices_per_group_widget.set_matrices(self._genes_model.ratio_matrices_per_group)

    def export(self, workbook):
        """Event handler which export the raw data to an excel spreadsheet.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        self._genes_model.export(workbook)

    def on_clear(self):
        """Event handler which resets all the groups defined so far.
        """

        available_genes_model = self._available_genes_listview.model()
        if available_genes_model is not None:
            available_genes_model.clear()

        reference_genes_model = self._reference_genes_listview.model()
        if reference_genes_model is not None:
            reference_genes_model.clear()

        interest_genes_model = self._interest_genes_listview.model()
        if interest_genes_model is not None:
            interest_genes_model.clear()

    def on_reset(self):
        """Event handler which resets all the groups defined so far.
        """

        available_genes_model = self._available_genes_listview.model()
        if available_genes_model is not None:
            available_genes_model.reset()

        reference_genes_model = self._reference_genes_listview.model()
        if reference_genes_model is not None:
            reference_genes_model.clear()

        interest_genes_model = self._interest_genes_listview.model()
        if interest_genes_model is not None:
            interest_genes_model.clear()

    def on_load_genes(self, genes, genes_per_group):
        """Event handler which loads sent rawdata model to the widget tableview.

        Args:
            genes (list of str): the list of genes
            genes_per_group (pandas.DataFrame): the gene set for each group (reference and interest)
        """

        filtered_genes = [gene for gene in genes if genes_per_group.isin([gene]).any().any()]

        if 'reference' in genes_per_group.columns and 'interest' in genes_per_group.columns:
            reference_genes_model = self._reference_genes_listview.model()
            reference_genes = genes_per_group['reference'].dropna()
            for gene in reference_genes:
                reference_genes_model.add_item(gene)

            interest_genes_model = self._interest_genes_listview.model()
            interest_genes = genes_per_group['interest'].dropna()
            for gene in interest_genes:
                interest_genes_model.add_item(gene)

        available_genes_model = AvailableGenesModel(self)
        available_genes_model.genes = genes

        self._available_genes_listview.setModel(available_genes_model)

        available_genes_model.remove_items(filtered_genes)

    def on_set_available_genes(self, genes):
        """
        """

        available_genes_model = AvailableGenesModel(self)
        available_genes_model.genes = genes

        self._available_genes_listview.setModel(available_genes_model)
