from PyQt5 import QtCore

from lightcycler.kernel.models.group_contents_model import GroupContentsModel


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    def __init__(self, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._groups = []

        self._models = []

    def add_group(self, group_name):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        if group_name in self._groups:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups.append(group_name)

        self._models.append(GroupContentsModel(self))

        self.endInsertRows()

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        if not self._groups:
            return QtCore.QVariant()

        idx = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._groups[idx]

        elif role == GroupsModel.model:
            return self._models[idx]

    def rowCount(self, parent=None):
        """Returns the number of groups.        
        """

        return len(self._groups)
