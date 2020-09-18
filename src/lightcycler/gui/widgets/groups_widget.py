import collections
import logging

from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.dialogs.means_and_errors_dialog import MeansAndErrorsDialog
from lightcycler.gui.views.group_contents_listview import GroupContentsListView
from lightcycler.gui.views.groups_listview import GroupsListView
from lightcycler.kernel.models.groups_model import GroupsModel
from lightcycler.kernel.models.pvalues_data_model import PValuesDataModel
from lightcycler.kernel.models.samples_model import SamplesModel


class GroupsWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(GroupsWidget, self).__init__(*args, **kwargs)

        self._init_ui()

        self._student_test_per_gene = collections.OrderedDict()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._groups_listview.selectionModel().currentChanged.connect(self.on_select_group)
        self._new_group_pushbutton.clicked.connect(self.on_create_new_group)
        self._reset_groups_pushbutton.clicked.connect(self.on_reset_groups)
        self._run_ttest_pushbutton.clicked.connect(self.on_run_student_test)
        self._selected_gene_combobox.currentTextChanged.connect(self.on_select_gene)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        groups_layout = QtWidgets.QHBoxLayout()

        groups_layout.addWidget(self._samples_listview)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._groups_listview)
        vlayout.addWidget(self._new_group_pushbutton)
        vlayout.addWidget(self._reset_groups_pushbutton)

        groups_layout.addLayout(vlayout)

        groups_layout.addWidget(self._group_contents_listview)

        main_layout.addLayout(groups_layout)

        main_layout.addWidget(self._run_ttest_pushbutton)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self._selected_gene_label)
        hlayout.addWidget(self._selected_gene_combobox)
        hlayout.addStretch()

        main_layout.addWidget(self._student_test_tableview)

        main_layout.addLayout(hlayout)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._samples_listview = QtWidgets.QListView()
        self._samples_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._samples_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._samples_listview.setDragEnabled(True)

        self._groups_listview = GroupsListView()
        self._groups_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._groups_listview.setSelectionMode(QtWidgets.QListView.SingleSelection)
        self._groups_listview.setModel(GroupsModel(self))

        self._group_contents_listview = GroupContentsListView(None, self)
        self._group_contents_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._group_contents_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)

        self._new_group_pushbutton = QtWidgets.QPushButton('New group')

        self._reset_groups_pushbutton = QtWidgets.QPushButton('Reset groups')

        self._run_ttest_pushbutton = QtWidgets.QPushButton('Run student test')

        self._selected_gene_label = QtWidgets.QLabel('Selected gene')
        self._selected_gene_combobox = QtWidgets.QComboBox()

        self._student_test_tableview = QtWidgets.QTableView()

    def _init_ui(self):

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

    def model(self):
        """Returns the underlying model.

        Returns:
            lightcycle.kernel.models.groups_model.GroupsModel: the model
        """

        return self._groups_listview.model()

    def on_create_new_group(self):
        """Event handler which creates a new group.
        """

        group, ok = QtWidgets.QInputDialog.getText(self, 'Enter group name', 'Group name', QtWidgets.QLineEdit.Normal, 'group')

        if ok and group:
            self._groups_listview.model().add_group(group)

    def on_load_raw_data(self, rawdata_model):
        """Event handler which loads sent rawdata model to the widget tableview.
        """

        samples_model = SamplesModel(rawdata_model.samples)

        self._samples_listview.setModel(samples_model)

        self._group_contents_listview.set_samples_model(samples_model)

    def on_reset_groups(self):
        """Event handler which resets all the groups defined so far
        """

        samples_model = self._samples_listview.model()
        if samples_model is not None:
            samples_model.reset()

        groups_model = self._groups_listview.model()
        if groups_model is not None:
            groups_model.reset()

        group_contents_model = self._group_contents_listview.model()
        if group_contents_model is not None:
            group_contents_model.reset()

    def on_run_student_test(self):
        """Event handler which will performs pairwise student test on the groups defined so far.
        """

        groups_model = self._groups_listview.model()

        self._student_test_per_gene = groups_model.run_student_test()

        self._selected_gene_combobox.clear()
        self._selected_gene_combobox.addItems(self._student_test_per_gene.keys())

        means, errors = groups_model.get_means_and_errors()

        if means.empty:
            return

        means_and_errors_dialog = MeansAndErrorsDialog(means, errors, self)
        means_and_errors_dialog.show()

    def on_select_gene(self, gene):
        """Event handler which updates the student table view for the selected gene.

        Args:
            gene (str): the selected gene
        """

        if gene not in self._student_test_per_gene:
            return

        df = self._student_test_per_gene[gene]

        self._student_test_tableview.setModel(PValuesDataModel(df, self))

    def on_select_group(self, idx):
        """Event handler which select a new group.

        Args:
            idx (PyQt5.QtCore.QModelIndex): the indexes selection
        """

        groups_model = self._groups_listview.model()

        group_contents_model = groups_model.data(idx, groups_model.model)

        if group_contents_model == QtCore.QVariant():
            return

        self._group_contents_listview.setModel(group_contents_model)
