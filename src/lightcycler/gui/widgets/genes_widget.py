import collections
import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.droppable_listview import DroppableListView
from lightcycler.kernel.models.available_genes_model import AvailableGenesModel
from lightcycler.kernel.models.droppable_model import DroppableModel


class GenesWidget(QtWidgets.QWidget):

    def __init__(self, main_window, *args, **kwargs):

        super(GenesWidget, self).__init__(main_window, *args, **kwargs)

        self._main_window = main_window

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._reset_genes_pushbutton.clicked.connect(self.on_clear)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._available_genes_listview)
        hlayout.addWidget(self._control_genes_listview)
        hlayout.addWidget(self._test_genes_listview)

        main_layout.addLayout(hlayout)

        main_layout.addWidget(self._reset_genes_pushbutton)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._available_genes_listview = QtWidgets.QListView()
        self._available_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._available_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._available_genes_listview.setDragEnabled(True)

        self._control_genes_listview = DroppableListView(None, self)
        self._control_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._control_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        control_genes_model = DroppableModel(self)
        self._control_genes_listview.setModel(control_genes_model)

        self._test_genes_listview = DroppableListView(None, self)
        self._test_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._test_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        test_genes_model = DroppableModel(self)
        self._test_genes_listview.setModel(test_genes_model)

        self._reset_genes_pushbutton = QtWidgets.QPushButton('Reset')

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def export(self, workbook):
        """Event handler which export the raw data to an excel spreadsheet.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        workbook.create_sheet('genes')
        worksheet = workbook.get_sheet_by_name('genes')

        worksheet.cell(row=1, column=1).value = 'control'
        worksheet.cell(row=1, column=2).value = 'test'

        control_genes_model = self._control_genes_listview.model()
        for i, item in enumerate(control_genes_model.items):
            worksheet.cell(row=i+2, column=1).value = item

        test_genes_model = self._test_genes_listview.model()
        for i, item in enumerate(test_genes_model.items):
            worksheet.cell(row=i+2, column=2).value = item

    def on_clear(self):
        """Event handler which resets all the groups defined so far.
        """

        available_genes_model = self._available_genes_listview.model()
        if available_genes_model is not None:
            available_genes_model.reset()

        control_genes_model = self._control_genes_listview.model()
        if control_genes_model is not None:
            control_genes_model.clear()

        test_genes_model = self._test_genes_listview.model()
        if test_genes_model is not None:
            test_genes_model.clear()

    def on_load_genes(self, genes, genes_per_group):
        """Event handler which loads sent rawdata model to the widget tableview.

        Args:
            genes (list of str): the list of genes
            genes_per_group (pandas.DataFrame): the gene set for each group (control and test)
        """

        filtered_genes = [gene for gene in genes if genes_per_group.isin([gene]).any().any()]

        if 'control' in genes_per_group.columns and 'test' in genes_per_group.columns:
            control_gene_model = self._control_genes_listview.model()
            control_genes = genes_per_group['control'].dropna()
            for gene in control_genes:
                control_gene_model.add_item(gene)

            test_gene_model = self._test_genes_listview.model()
            test_genes = genes_per_group['test'].dropna()
            for gene in test_genes:
                test_gene_model.add_item(gene)

        available_genes_model = AvailableGenesModel(self)
        available_genes_model.genes = genes

        self._available_genes_listview.setModel(available_genes_model)

        available_genes_model.remove_items(filtered_genes)

        self._control_genes_listview.set_source_model(available_genes_model)
        self._test_genes_listview.set_source_model(available_genes_model)

    def on_set_available_genes(self, genes):

        available_genes_model = AvailableGenesModel(self)
        available_genes_model.genes = genes

        self._available_genes_listview.setModel(available_genes_model)

        self._control_genes_listview.set_source_model(available_genes_model)
        self._test_genes_listview.set_source_model(available_genes_model)
