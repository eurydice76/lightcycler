import collections
import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.dialogs.means_and_errors_dialog import MeansAndErrorsDialog
from lightcycler.gui.dialogs.group_contents_dialog import GroupContentsDialog
from lightcycler.gui.dialogs.grubbs_data_dialog import GrubbsDataDialog
from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.gui.views.droppable_listview import DroppableListView
from lightcycler.gui.views.groups_listview import GroupsListView
from lightcycler.kernel.models.available_samples_model import AvailableSamplesModel
from lightcycler.kernel.models.groups_model import GroupsModel
from lightcycler.kernel.models.pvalues_data_model import PValuesDataModel


class GroupsWidget(QtWidgets.QWidget):

    def __init__(self, main_window, *args, **kwargs):

        super(GroupsWidget, self).__init__(main_window, *args, **kwargs)

        self._main_window = main_window

        self._init_ui()

        self._statistics = collections.OrderedDict()

        self._student_test_per_gene = collections.OrderedDict()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._groups_listview.selectionModel().currentChanged.connect(self.on_select_group)
        self._sort_groups_pushbutton.clicked.connect(self.on_sort_groups)
        self._new_group_pushbutton.clicked.connect(self.on_create_new_group)
        self._reset_groups_pushbutton.clicked.connect(self.on_clear)
        self._run_ttest_pushbutton.clicked.connect(self.on_run_student_test)
        self._selected_gene_combobox.currentTextChanged.connect(self.on_select_gene)
        self._selected_zone_combobox.currentTextChanged.connect(self.on_select_zone)
        self._plot_statistics_button.clicked.connect(self.on_plot_statistics)
        self._groups_listview.display_grubbs_data.connect(self.on_display_grubbs_data)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        groups_layout = QtWidgets.QHBoxLayout()

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Available samples'))
        vlayout.addWidget(self._available_samples_listview)
        groups_layout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Created groups'))
        vlayout.addWidget(self._groups_listview)
        vlayout.addWidget(self._sort_groups_pushbutton)
        vlayout.addWidget(self._new_group_pushbutton)
        vlayout.addWidget(self._reset_groups_pushbutton)
        groups_layout.addLayout(vlayout)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(QtWidgets.QLabel('Samples in group'))
        vlayout.addWidget(self._samples_per_group_listview)
        groups_layout.addLayout(vlayout)

        main_layout.addLayout(groups_layout)

        main_layout.addWidget(self._run_ttest_pushbutton)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)
        hlayout.addWidget(self._selected_zone_label)
        hlayout.addWidget(self._selected_zone_combobox)
        hlayout.addStretch()
        hlayout.addWidget(self._plot_statistics_button)

        main_layout.addWidget(self._tabs)

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._available_samples_listview = DroppableListView(self)
        self._available_samples_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._available_samples_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._available_samples_listview.setDragEnabled(True)
        self._available_samples_listview.setModel(AvailableSamplesModel(self))

        self._groups_listview = GroupsListView()
        self._groups_listview.setSelectionMode(QtWidgets.QListView.SingleSelection)
        self._groups_listview.setModel(GroupsModel(self))

        self._samples_per_group_listview = DroppableListView(self)
        self._samples_per_group_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._samples_per_group_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._samples_per_group_listview.setDragEnabled(True)

        self._sort_groups_pushbutton = QtWidgets.QPushButton('Sort groups')

        self._new_group_pushbutton = QtWidgets.QPushButton('New group')

        self._reset_groups_pushbutton = QtWidgets.QPushButton('Reset groups')

        self._run_ttest_pushbutton = QtWidgets.QPushButton('Run student test')

        self._selected_gene_label = QtWidgets.QLabel('Gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()

        self._selected_zone_label = QtWidgets.QLabel('Zone')
        self._selected_zone_combobox = QtWidgets.QComboBox()
        self._selected_zone_combobox.addItems(GroupsModel.student_test_zones)

        self._plot_statistics_button = QtWidgets.QPushButton('Plot statistics')

        self._tabs = QtWidgets.QTabWidget()

        self._statistics_tableview = CopyPastableTableView(delimiter=',')
        self._tabs.addTab(self._statistics_tableview, 'Statistics')

        self._student_test_tableview = CopyPastableTableView(delimiter=',')
        self._tabs.addTab(self._student_test_tableview, 'Student tests')

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

        model = self._groups_listview.model()
        if model is None:
            return

        model.export(workbook)

    @property
    def groups_listview(self):
        """Getter for _groups_listview attribute.
        """

        return self._groups_listview

    def model(self):
        """Returns the underlying model.

        Returns:
            lightcycle.kernel.models.groups_model.GroupsModel: the model
        """

        return self._groups_listview.model()

    def on_clear(self):
        """Event handler which resets all the groups defined so far.
        """

        samples_model = self._available_samples_listview.model()
        if samples_model is not None:
            samples_model.reset()

        groups_model = self._groups_listview.model()
        if groups_model is not None:
            groups_model.clear()

        samples_per_group_model = self._samples_per_group_listview.model()
        if samples_per_group_model is not None:
            samples_per_group_model.clear()

    def on_create_new_group(self):
        """Event handler which creates a new group.
        """

        group, ok = QtWidgets.QInputDialog.getText(self, 'Enter group name', 'Group name', QtWidgets.QLineEdit.Normal, 'group')

        if ok and group:
            self._groups_listview.model().add_group(group)

    def on_display_grubbs_data(self, index):
        """Pops up a dialog which shows the Grubbs data.
        """

        groups_model = self._groups_listview.model()
        if groups_model is None:
            return

        selected_group = groups_model.data(index, role=QtCore.Qt.DisplayRole)

        grubbs_data = groups_model.get_outliers(selected_group)

        dialog = GrubbsDataDialog(grubbs_data, self._main_window)
        dialog.show()

    def on_load_groups(self, samples, groups):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        groups_model = self._groups_listview.model()
        groups_model.load_groups(groups)

        # Coerce the dtype to str in case of empty dataframe to avoid FutureWarning
        filtered_samples = [sample for sample in samples if sample in groups.values.astype(str)]

        available_samples_model = AvailableSamplesModel(self)
        available_samples_model.samples = samples

        self._available_samples_listview.setModel(available_samples_model)

        available_samples_model.remove_items(filtered_samples)

    def on_set_group_control(self, group_control):
        """Sets the group control.

        Args:
            group_control (str): the group control
        """

        groups_model = self._groups_listview.model()

        groups_model.group_control = group_control

    def on_plot_statistics(self):
        """Pops up a dialog for plotting statistics.
        """

        if not self._statistics:
            return

        means_and_errors_dialog = MeansAndErrorsDialog(self._statistics, self)
        means_and_errors_dialog.show()

    def on_run_student_test(self):
        """Event handler which will performs pairwise student test on the groups defined so far.
        """

        groups_model = self._groups_listview.model()
        selected_groups = [group[0] for group in groups_model.groups if group[2]]

        # Compute the statistics
        self._statistics = groups_model.get_statistics(selected_groups=selected_groups)

        # Perform the student test for the selected groups
        self._student_test_per_gene = groups_model.run_student_test()

        # Update the selected gene and zone combo boxes
        self._selected_gene_combobox.clear()
        self._selected_gene_combobox.addItems(list(self._student_test_per_gene.keys()))

    def on_select_gene(self, gene):
        """Event handler which updates the student table view for the selected gene.

        Args:
            gene (str): the selected gene
        """

        if gene not in self._student_test_per_gene:
            return

        zone = self._selected_zone_combobox.currentText()
        if not zone:
            return

        statistics_df = self._statistics[gene][zone]
        self._statistics_tableview.setModel(PValuesDataModel(statistics_df, self))

        student_test_df = self._student_test_per_gene[gene][zone]
        self._student_test_tableview.setModel(PValuesDataModel(student_test_df, self))

    def on_select_group(self, idx):
        """Event handler which select a new group.

        Args:
            idx (PyQt5.QtCore.QModelIndex): the indexes selection
        """

        groups_model = self._groups_listview.model()

        samples_per_group_model = groups_model.data(idx, groups_model.model)
        if samples_per_group_model == QtCore.QVariant():
            return

        self._samples_per_group_listview.setModel(samples_per_group_model)

    def on_select_zone(self, zone):
        """Event handler which updates the student table view for the selected zone.

        Args:
            zone (str): the selected zone
        """

        gene = self._selected_gene_combobox.currentText()
        if not gene:
            return

        if not zone:
            return

        statistics_df = self._statistics[gene][zone]
        self._statistics_tableview.setModel(PValuesDataModel(statistics_df, self))

        student_test_df = self._student_test_per_gene[gene][zone]
        self._student_test_tableview.setModel(PValuesDataModel(student_test_df, self))

    def on_update_samples_and_groups(self, rawdata_model):
        """Update the available sample listview and the group contents listview with a change in rawdata.

        Args:
            rawdata_model (lightcycler.kernel.models.rawdata_model.RawDataModel): the raw data model
        """

        groups_model = self._groups_listview.model()

        groups_contents = [model.items for _, model, _ in groups_model.groups]

        # Update the available samples listview by removing from the samples the ones that are present in a group
        filtered_samples = []
        for s in rawdata_model.samples:
            for gc in groups_contents:
                if s in gc:
                    break
            else:
                filtered_samples.append(s)

        available_samples_model = AvailableSamplesModel(self)
        available_samples_model.samples = filtered_samples
        self._available_samples_listview.setModel(available_samples_model)

        # Update the group contents listview by removing from the group contents of
        # each group the samples which are not present in the input samples list
        for _, model, _ in groups_model.groups:
            to_be_deleted = []
            for s in model.items:
                if s not in rawdata_model.samples:
                    to_be_deleted.append(s)
            model.remove_items(to_be_deleted)

    def on_sort_groups(self):
        """Event handler which sort the groups in alphabetical order.
        """

        groups_model = self._groups_listview.model()
        if groups_model is None:
            return

        groups_model.sort()
