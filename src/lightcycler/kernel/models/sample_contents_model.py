import collections
import logging
import os
import re

from PyQt5 import QtCore, QtGui

import openpyxl

import tabula

import numpy as np

import pandas as pd


class SampleContentsModel(QtCore.QAbstractTableModel):

    sample = QtCore.Qt.UserRole + 1

    gene = QtCore.Qt.UserRole + 2

    change_value = QtCore.pyqtSignal(str, str, int)

    remove_value = QtCore.pyqtSignal(str, str, int)

    def __init__(self, values_per_sample, *args, **kwargs):
        """Constructor.
        """

        super(SampleContentsModel, self).__init__(*args, **kwargs)

        self._values_per_sample = values_per_sample

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        return max([len(v[2]) for v in self._values_per_sample])

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

        row = index.row()
        col = index.column()

        sample, gene, values = self._values_per_sample[row]

        if role == QtCore.Qt.DisplayRole:

            return str(values[col]) if col < len(values) else QtCore.QVariant()

        elif role == SampleContentsModel.sample:

            return sample

        elif role == SampleContentsModel.gene:

            return gene

    def headerData(self, idx, orientation, role):
        """Returns the header data for a given index, orientation and role.

        Args:
            idx (int): the index
            orientation (int): the orientation
            role (int): the role
        """

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return idx
            else:
                return self._values_per_sample[idx][0]

    def remove_contents(self, row, col):

        if row < 0 or row >= len(self._values_per_sample):
            return

        sample, gene, values = self._values_per_sample[row]

        if col < 0 or col >= len(values):
            return

        del values[col]

        self.remove_value.emit(sample, gene, col)

        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Return the number of rows of the model for a given parent.

        Returns:
            int: the number of rows
        """

        return len(self._values_per_sample)
