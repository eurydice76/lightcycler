import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.droppable_listview import DroppableListView
from lightcycler.gui.widgets.ct_matrix_widget import CTMatrixWidget
from lightcycler.gui.widgets.rq_matrix_widget import RQMatrixWidget
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
        self._compute_rq_matrix_pushbutton.clicked.connect(self.on_compute_rq_matrix)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._available_genes_listview)
        hlayout.addWidget(self._reference_genes_listview)
        hlayout.addWidget(self._interest_genes_listview)

        main_layout.addLayout(hlayout)

        main_layout.addWidget(self._reset_genes_pushbutton)
        main_layout.addWidget(self._compute_rq_matrix_pushbutton)

        main_layout.addWidget(self._tabs, stretch=2)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._available_genes_listview = QtWidgets.QListView()
        self._available_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._available_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._available_genes_listview.setDragEnabled(True)

        self._reference_genes_listview = DroppableListView(None, self)
        self._reference_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._reference_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        reference_genes_model = DroppableModel(self)
        self._reference_genes_listview.setModel(reference_genes_model)

        self._interest_genes_listview = DroppableListView(None, self)
        self._interest_genes_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._interest_genes_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        interest_genes_model = DroppableModel(self)
        self._interest_genes_listview.setModel(interest_genes_model)

        self._reset_genes_pushbutton = QtWidgets.QPushButton('Reset')

        self._compute_rq_matrix_pushbutton = QtWidgets.QPushButton('Compute RQ matrix')

        self._tabs = QtWidgets.QTabWidget()

        self._ct_matrix_widget = CTMatrixWidget(self)
        self._rq_matrix_widget = RQMatrixWidget(self)

        self._tabs.addTab(self._ct_matrix_widget, 'CT matrix')
        self._tabs.addTab(self._rq_matrix_widget, 'RQ matrix')

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def on_compute_rq_matrix(self):
        """Compute the RQ matrix.
        """

        groups_model = self._main_window.groups_widget.groups_listview.model()
        if groups_model is None:
            return

        reference_genes_model = self._reference_genes_listview.model()
        reference_genes = [reference_genes_model.data(reference_genes_model.index(i, 0), QtCore.Qt.DisplayRole)
                           for i in range(reference_genes_model.rowCount())]
        if not reference_genes:
            logging.info('No genes of reference defined')
            return

        interest_genes_model = self._interest_genes_listview.model()
        interest_genes = [interest_genes_model.data(interest_genes_model.index(i, 0), QtCore.Qt.DisplayRole)
                          for i in range(interest_genes_model.rowCount())]
        if not interest_genes:
            logging.info('No genes of interest defined')
            return

        logging.info('Computing RQ matrix. Please wait ...')
        ct_matrix = groups_model.compute_ct_matrix()
        if ct_matrix is None:
            return

        ct_matrix_model = self._ct_matrix_widget.model()

        ct_matrix_model.set_reference_genes(reference_genes)
        ct_matrix_model.set_interest_genes(interest_genes)

        ct_matrix_model.set_ct_matrix(ct_matrix)

        geom_means = groups_model.compute_geometric_means(reference_genes)

        rq_matrix = ct_matrix.loc[interest_genes]/geom_means.values

        rq_matrix = rq_matrix.round(3)

        rq_matrix_model = self._rq_matrix_widget.model()
        rq_matrix_model.set_rq_matrix(rq_matrix)

        logging.info('.. done')

    def export(self, workbook):
        """Event handler which export the raw data to an excel spreadsheet.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        workbook.create_sheet('genes')
        worksheet = workbook.get_sheet_by_name('genes')

        worksheet.cell(row=1, column=1).value = 'reference'
        worksheet.cell(row=1, column=2).value = 'interest'

        reference_genes_model = self._reference_genes_listview.model()
        for i, item in enumerate(reference_genes_model.items):
            worksheet.cell(row=i+2, column=1).value = item

        interest_genes_model = self._interest_genes_listview.model()
        for i, item in enumerate(interest_genes_model.items):
            worksheet.cell(row=i+2, column=2).value = item

    def on_clear(self):
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

        self._reference_genes_listview.set_source_model(available_genes_model)
        self._interest_genes_listview.set_source_model(available_genes_model)

    def on_set_available_genes(self, genes):
        """
        """

        available_genes_model = AvailableGenesModel(self)
        available_genes_model.genes = genes

        self._available_genes_listview.setModel(available_genes_model)

        self._reference_genes_listview.set_source_model(available_genes_model)
        self._interest_genes_listview.set_source_model(available_genes_model)
