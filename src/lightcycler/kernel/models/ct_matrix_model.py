from PyQt5 import QtCore, QtGui

import pandas as pd


class CTMatrixModel(QtCore.QAbstractTableModel):

    def __init__(self, *args, **kwargs):
        """Constructor.
        """

        super(CTMatrixModel, self).__init__(*args, **kwargs)

        self._ct_matrix = pd.DataFrame()

        self._reference_genes = []

        self._interest_genes = []

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        return len(self._ct_matrix.columns)

    def data(self, index, role):
        """Get the data at a given index for a given role.

        Args:
            index (QtCore.QModelIndex): the index
            role (int): the role

        Returns:
            QtCore.QVariant: the data
        """

        if self._ct_matrix.empty:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        col = index.column()

        if role == QtCore.Qt.DisplayRole:
            return str(self._ct_matrix.iloc[row, col])

        elif role == QtCore.Qt.BackgroundRole:

            gene = self._ct_matrix.index[row]

            if gene in self._reference_genes:
                return QtGui.QBrush(QtGui.QColor(51, 190, 255))
            elif gene in self._interest_genes:
                return QtGui.QBrush(QtGui.QColor(255, 119, 51))
            else:
                return QtGui.QBrush(QtCore.Qt.white)

    def headerData(self, idx, orientation, role):
        """Returns the header data for a given index, orientation and role.

        Args:
            idx (int): the index
            orientation (int): the orientation
            role (int): the role
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._ct_matrix.columns[idx]
            else:
                return self._ct_matrix.index[idx]

    def rowCount(self, parent=None):
        """Return the number of rows of the model for a given parent.

        Returns:
            int: the number of rows
        """

        return len(self._ct_matrix.index)

    @property
    def ct_matrix(self):

        return self._ct_matrix

    @ct_matrix.setter
    def ct_matrix(self, ct_matrix):

        self._ct_matrix = ct_matrix
        self.layoutChanged.emit()

    def set_interest_genes(self, interest_genes):
        """Set the list of genes used as the interest.
        """

        self._interest_genes = interest_genes
        self.layoutChanged.emit()

    def set_reference_genes(self, reference_genes):
        """Set the list of genes used as the reference.
        """

        self._reference_genes = reference_genes
        self.layoutChanged.emit()
