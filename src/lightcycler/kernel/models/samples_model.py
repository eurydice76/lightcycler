import copy

from PyQt5 import QtCore


class SamplesModel(QtCore.QAbstractListModel):

    def __init__(self, samples, *args, **kwargs):

        super(SamplesModel, self).__init__(*args, **kwargs)

        self._samples = samples

        self._samples_copy = copy.copy(samples)

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

        if not self._samples:
            return QtCore.QVariant()

        idx = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._samples[idx]

    def flags(self, index):
        """Return the flags of an itme with a given index.

        Args:
            index (PyQt5.QtCore.QModelIndex): the index

        Returns:
            int: the flag
        """

        if index.isValid():
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

    def remove_items(self, items):
        """
        """

        indexes = []

        for item in items:
            try:
                indexes.append(self._samples.index(item))
            except ValueError:
                continue

        indexes.reverse()

        for idx in indexes:
            self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self._samples[idx]
            self.endRemoveRows()

    def rowCount(self, parent=None):
        """Returns the number of samples.        
        """

        return len(self._samples)
