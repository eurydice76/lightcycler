from PyQt5 import QtCore


class GroupContentsModel(QtCore.QAbstractListModel):

    def __init__(self, *args, **kwargs):

        super(GroupContentsModel, self).__init__(*args, **kwargs)

        self._samples = []

    def add_sample(self, sample):
        """Add a sample to the model.

        Args:
            sample (str): the sample
        """

        if sample in self._samples:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._samples.append(sample)

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

        if not self._samples:
            return QtCore.QVariant()

        idx = index.row()

        if role == QtCore.Qt.DisplayRole:
            return self._samples[idx]

    def rowCount(self, parent=None):
        """Returns the number of samples.        
        """

        return len(self._samples)
