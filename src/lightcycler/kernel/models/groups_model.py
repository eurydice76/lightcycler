import collections
import logging

from PyQt5 import QtCore

import numpy as np

import pandas as pd

import numpy as np

import scikit_posthocs as sk

from lightcycler.kernel.models.group_contents_model import GroupContentsModel


class GroupsModel(QtCore.QAbstractListModel):

    model = QtCore.Qt.UserRole + 1

    def __init__(self, *args, **kwargs):

        super(GroupsModel, self).__init__(*args, **kwargs)

        self._means = pd.DataFrame()

        self._groups = []

    def add_group(self, group_name):
        """Add a new group to the model.

        Args:
            group_name (str): the name of the group to add
        """

        group_names = [group[0] for group in self._groups]
        if group_name in group_names:
            return

        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())

        self._groups.append((group_name, GroupContentsModel(self), True))

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

        group, model, selected = self._groups[idx]

        if role == QtCore.Qt.DisplayRole:
            return group

        elif role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if selected else QtCore.Qt.Unchecked

        elif role == GroupsModel.model:
            return model

    def export(self, workbook):
        """Export the model to an excel spreadsheet

        Args:
            workbook (openpyxl.workbook.workbook.Workbook): the excel spreadsheet
        """

        workbook.create_sheet('groups')
        worksheet = workbook.get_sheet_by_name('groups')

        for i, (group, model, _) in enumerate(self._groups):
            worksheet.cell(row=1, column=i+1).value = group
            for j, sample in enumerate(model.samples):
                worksheet.cell(row=j+2, column=i+1).value = sample

    def flags(self, index):
        """Return the flag for the item with specified index.

        Returns:
            int: the flag
        """

        default_flags = super(GroupsModel, self).flags(index)

        return QtCore.Qt.ItemIsUserCheckable | default_flags

    def get_means_and_errors(self):
        """Returns the mean and error for each selected group.

        Returns:
            2-tuple of pandas.DataFrame: the means and errors
        """

        genes = self._means.index
        groups = [group for group, _, selected in self._groups if selected]

        means = pd.DataFrame(np.nan, index=genes, columns=groups)
        errors = pd.DataFrame(np.nan, index=genes, columns=groups)

        # Loop over all selected gene
        for gene in genes:

            for group, model, selected in self._groups:
                if not selected:
                    continue

                values = []
                for sample in model.samples:
                    values.append(self._means.loc[gene, sample])

                mean = np.nanmean(values)
                std = np.nanstd(values)

                means.loc[gene, group] = mean
                errors.loc[gene, group] = std

        return (means, errors)

    def on_load_groups(self, groups):
        """Reset the model and load groups.

        Args:
            groups (pd.DataFrame): the groups
        """

        self._groups = []

        for group in groups.columns:
            samples = groups[group].dropna()

            group_contents_model = GroupContentsModel()
            for sample in samples:
                group_contents_model.add_sample(sample)

            self._groups.append((group, group_contents_model, True))

        self.layoutChanged.emit()

    def on_set_dynamic_matrix(self, means):
        """Event handler which set the dynamic matrix.

        Args:
            means (pandas.DataFrame): the dynamic matrix
        """

        self._means = means

    def remove_groups(self, items):
        """
        """

        indexes = []

        group_names = [group[0] for group in self._groups]

        for item in items:
            try:
                indexes.append(group_names.index(item))
            except ValueError:
                continue

        indexes.reverse()

        for idx in indexes:
            self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
            del self._groups[idx]
            self.endRemoveRows()

    def reset(self):
        """Reset the model.
        """

        self._means = pd.DataFrame()
        self._groups = []
        self.layoutChanged.emit()

    def rowCount(self, parent=None):
        """Returns the number of groups.
        """

        return len(self._groups)

    def run_student_test(self):
        """Perform a pairwise student test over the groups.
        """

        student_test_per_gene = collections.OrderedDict()

        for gene in self._means.index:
            df = pd.DataFrame(columns=['groups', 'means'])
            for group, model, selected in self._groups:

                if not selected:
                    continue

                for sample in model.samples:
                    row = pd.DataFrame([[group, self._means.loc[gene, sample]]], columns=['groups', 'means'])
                    df = pd.concat([df, row])

            if not df.empty:

                if df.isnull().values.any():
                    logging.warning('NaN values detected for {} group in {} gene'.format(group, gene))

                # Any kind of error must be caught here
                try:
                    student_test_per_gene[gene] = sk.posthoc_ttest(df, val_col='means', group_col='groups', p_adjust='holm')
                except:
                    logging.error('Can not compute student test for gene {}. Skip it.'.format(gene))
                    continue

            else:
                logging.warning('No group selected for student test for gene {}'.format(gene))

        return student_test_per_gene
