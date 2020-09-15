import logging

from PyQt5 import QtWidgets

from lightcycler.gui.views.group_contents_listview import GroupContentsListView
from lightcycler.kernel.models.groups_model import GroupsModel
from lightcycler.kernel.models.samples_model import SamplesModel


class GroupsWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(GroupsWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_events(self):
        """Build the events related with the widget.
        """

        self._groups_listview.selectionModel().currentChanged.connect(self.on_select_group)
        self._new_group_pushbutton.clicked.connect(self.on_create_new_group)

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QHBoxLayout()

        main_layout.addWidget(self._samples_listview)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self._groups_listview)
        vlayout.addWidget(self._new_group_pushbutton)

        main_layout.addLayout(vlayout)

        main_layout.addWidget(self._group_contents_listview)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._samples_listview = QtWidgets.QListView()
        self._samples_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._samples_listview.setSelectionMode(QtWidgets.QListView.ExtendedSelection)
        self._samples_listview.setDragEnabled(True)

        self._groups_listview = QtWidgets.QListView()
        self._groups_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._groups_listview.setSelectionMode(QtWidgets.QListView.SingleSelection)
        self._groups_listview.setModel(GroupsModel(self))

        self._group_contents_listview = GroupContentsListView(None, self)
        self._group_contents_listview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self._new_group_pushbutton = QtWidgets.QPushButton('New group')

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()
        self._build_events()

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

    def on_select_group(self, idx):
        """Event handler which select a new group.

        Args:
            idx (PyQt5.QtCore.QModelIndex): the indexes selection
        """

        groups_model = self._groups_listview.model()

        group_contents_model = groups_model.data(idx, groups_model.model)

        self._group_contents_listview.setModel(group_contents_model)
