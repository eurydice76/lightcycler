import collections
import logging

import pandas as pd

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.kernel.models.diff_data_model import DiffDataModel
from lightcycler.kernel.models.dynamic_matrix_model import DynamicMatrixModel
from lightcycler.kernel.models.n_values_data_model import NValuesDataModel
from lightcycler.kernel.models.pandas_data_model import PandasDataModel
from lightcycler.kernel.models.stds_data_model import StdsDataModel
from lightcycler.gui.widgets.checkable_combobox import CheckableComboBox


class DynamicMatrixWidget(QtWidgets.QWidget):

    # Signal emitted when the dynamics matrices just have been computed.
    dynamic_matrices_computed = QtCore.pyqtSignal(collections.OrderedDict)

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(DynamicMatrixWidget, self).__init__(*args, **kwargs)

        # The dynamic matrices.
        # This is a dict whose keys are the genes and values are pandas dataframe whose indexes are the zones and columns are the sample names.
        # The values stored by the pandas dataframe are lists of CP values computed from the raw data.
        self._dynamic_matrices = collections.OrderedDict()

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._selected_gene_combobox.currentTextChanged.connect(self.on_select_gene)
        self._selected_zones_combobox.view().clicked.connect(self.on_select_zones)

    def _build_layout(self):
        """Build the layout.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._tabs)

        hlayout = QtWidgets.QHBoxLayout()

        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)

        hlayout.addWidget(self._selected_zones_label)
        hlayout.addWidget(self._selected_zones_combobox)

        hlayout.addStretch()

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets.
        """

        self._view_label = QtWidgets.QLabel('View')

        self._tabs = QtWidgets.QTabWidget()

        self._dynamic_matrix_tableview = QtWidgets.QTableView()
        dynamic_matrix_model = DynamicMatrixModel()
        self._dynamic_matrix_tableview.setModel(dynamic_matrix_model)
        self._tabs.addTab(self._dynamic_matrix_tableview, 'Dynamic matrix')

        self._averages_tableview = CopyPastableTableView(',')
        self._tabs.addTab(self._averages_tableview, 'Averages')

        self._stds_tableview = CopyPastableTableView(',')
        self._tabs.addTab(self._stds_tableview, 'Std Devs')

        self._n_values_tableview = CopyPastableTableView(',')
        self._tabs.addTab(self._n_values_tableview, 'N')

        self._diff_tableview = CopyPastableTableView(',')
        self._tabs.addTab(self._diff_tableview, 'Difference')

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()

        self._selected_zones_label = QtWidgets.QLabel('Zones')
        self._selected_zones_combobox = CheckableComboBox()
        self._selected_zones_combobox.addItems([''.join(z) for z in DynamicMatrixModel.zones])

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()
        self._build_events()

    def export(self, workbook):
        """Export the dynamic matrix and the statistics tables to an excel workbook.

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the workbook
        """

        # Loop over the gene
        for gene, df in self._dynamic_matrices.items():

            # Create a dynamic matrix model with the current dynamic matrix
            model = DynamicMatrixModel()
            model.dynamic_matrix = df

            # Export the data
            model.export(workbook, gene)

    def on_select_gene(self, gene):
        """Update the averages, stds and n values tables with the newly selected gene.

        Args:
            gene (str): the selected gene 
        """

        dynamic_matrix_model = self._dynamic_matrix_tableview.model()

        selected_gene = self._selected_gene_combobox.currentText()
        # If the selected gene string is empty, clear the dynamic matrix model and related statistics tables.
        if not selected_gene:
            dynamic_matrix_model.clear()
            self._averages_tableview.setModel(None)
            self._stds_tableview.setModel(None)
            self._n_values_tableview.setModel(None)
            self._diff_tableview.setModel(None)

        else:
            # Update the dynamic matrix model with the dynamic matrix corresponding to the selected gene
            dynamic_matrix_model.dynamic_matrix = self._dynamic_matrices[selected_gene]

            # Fetch the checked zones from the corresponding combo box
            selected_zones = [item.text() for item in self._selected_zones_combobox.checked_items()]

            # Update the averages, stds and n values tables
            self._averages_tableview.setModel(PandasDataModel(dynamic_matrix_model.get_averages(selected_zones), self))
            self._stds_tableview.setModel(StdsDataModel(dynamic_matrix_model.get_stds(selected_zones), self))
            self._n_values_tableview.setModel(NValuesDataModel(dynamic_matrix_model.get_n_values(selected_zones), self))
            self._diff_tableview.setModel(DiffDataModel(dynamic_matrix_model.get_diff(selected_zones), self))

    def on_select_zones(self):
        """Updates the averages, stds and values tables with the selected zones.
        """

        selected_zones = [item.text() for item in self._selected_zones_combobox.checked_items()]

        dynamic_matrix_model = self._dynamic_matrix_tableview.model()

        self._averages_tableview.setModel(PandasDataModel(dynamic_matrix_model.get_averages(selected_zones), self))

        self._stds_tableview.setModel(StdsDataModel(dynamic_matrix_model.get_stds(selected_zones), self))

        self._n_values_tableview.setModel(NValuesDataModel(dynamic_matrix_model.get_n_values(selected_zones), self))

        self._diff_tableview.setModel(DiffDataModel(dynamic_matrix_model.get_diff(selected_zones), self))

    def on_build_dynamic_matrices(self, rawdata_model):
        """Build the dynamic matrices for each gene from the rawdata dataframe.

        Args:
            rawdata_model (lightcycler.kernel.models.rawdata_model.RawDataModel): the rawdata model
        """

        self._dynamic_matrices.clear()

        rawdata = rawdata_model.rawdata

        # Fetch the list of genes from the rawdata
        genes = sorted(list(collections.OrderedDict.fromkeys(rawdata['Gene']))) if 'Gene' in rawdata.columns else []
        if not genes:
            logging.error('No gene loaded')

        # Fetch the list of samples from the rawdata
        samples = sorted(list(collections.OrderedDict.fromkeys(rawdata['Name']))) if 'Name' in rawdata.columns else []

        # The zones for which the dynamic matrices will be computed
        zones = [''.join(z) for z in DynamicMatrixModel.zones]

        # Loop over the genes and compute a dataframe for each gene
        for gene in genes:
            self._dynamic_matrices[gene] = pd.DataFrame(None, index=zones, columns=samples)
            # Loop over the zones
            for zone in zones:
                # Loop over the samples
                for sample in samples:
                    # Create a filter for the rawdata parts which match the running gene, sample and zone
                    fylter = rawdata['Gene'].isin([gene]) & rawdata['Name'].isin([sample]) & rawdata['Zone'].isin(tuple(zone))
                    self._dynamic_matrices[gene].loc[zone, sample] = rawdata['CP'][fylter].tolist()

        # Update the selected gene combobox
        self._selected_gene_combobox.clear()
        self._selected_gene_combobox.addItems(genes)
        self.on_select_gene(self._selected_gene_combobox.currentText())

        # Emit a signal that the dynamic matrices have been computed.
        self.dynamic_matrices_computed.emit(self._dynamic_matrices)
