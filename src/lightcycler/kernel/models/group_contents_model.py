import collections
import logging
import os
import re

from PyQt5 import QtCore, QtGui

import openpyxl

import tabula

import numpy as np

import pandas as pd


class GroupContentsModel(QtCore.QAbstractTableModel):

    sample = QtCore.Qt.UserRole + 1

    gene = QtCore.Qt.UserRole + 2

    change_value = QtCore.pyqtSignal(str, str, int, float)

    remove_value = QtCore.pyqtSignal(str, str, int)

    select_value = QtCore.pyqtSignal(str, str, int)

    def __init__(self, group_contents, *args, **kwargs):
        """Constructor.
        """

        super(GroupContentsModel, self).__init__(*args, **kwargs)

        self._group_contents = group_contents

    def columnCount(self, parent=None):
        """Return the number of columns of the model for a given parent.

        Returns:
            int: the number of columns
        """

        return max([len(v[2]) for v in self._group_contents])

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

        sample, gene, values = self._group_contents[row]

        if role == QtCore.Qt.DisplayRole:

            return str(values[col]) if col < len(values) else QtCore.QVariant()

        elif role == GroupContentsModel.sample:

            return sample

        elif role == GroupContentsModel.gene:

            return gene

    def flags(self, index):
        """Return the flag for the item with specified index.

        Args:
            int: the flag
        """

        row = index.row()
        col = index.column()

        _, _, values = self._group_contents[row]

        default_flags = super(GroupContentsModel, self).flags(index)

        if col >= len(values):
            return default_flags
        else:
            return QtCore.Qt.ItemIsEditable | default_flags

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
                return self._group_contents[idx][0]

    def remove_contents(self, row, col):

        if row < 0 or row >= len(self._group_contents):
            return

        sample, gene, values = self._group_contents[row]

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

        return len(self._group_contents)

    def setData(self, index, value, role):
        """Set the data for a given index and given role.

        Args:
            value (QtCore.QVariant): the data
        """

        if not index.isValid():
            return QtCore.QVariant()

        row = index.row()
        col = index.column()

        sample, gene, values = self._group_contents[row]

        if col < 0 or col >= len(values):
            return super(GroupContentsModel, self).setData(index, value, role)

        if role == QtCore.Qt.EditRole:

            try:
                new_value = float(value)
            except ValueError:
                return super(GroupContentsModel, self).setData(index, value, role)
            else:
                values[col] = new_value
                self.dataChanged.emit(index, index)
                self.change_value.emit(sample, gene, col, new_value)
                return True

        return super(GroupContentsModel, self).setData(index, value, role)
