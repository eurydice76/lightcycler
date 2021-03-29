import collections
import logging

import numpy as np

import pandas as pd

import scipy.stats.mstats as stats

from PyQt5 import QtCore


def dataframe_to_excel(worksheet, row, dataframe):

    # Write the column
    for col, value in enumerate(dataframe.columns):
        worksheet.cell(row=row, column=col+2).value = value

    # write the dataframe and the indexes
    for ind in dataframe.index:
        row += 1
        worksheet.cell(row=row, column=1).value = ind
        for i, col in enumerate(dataframe.columns):
            worksheet.cell(row=row, column=i+2).value = dataframe.loc[ind, col]


class GenesModel:

    zones = ('ABCDE', 'ABCD', 'AB', 'CD', 'E')

    def __init__(self, rawdata_model, groups_model, reference_genes_model, interest_genes_model):
        """Constructor.
        """

        self._rawdata_model = rawdata_model

        self._groups_model = groups_model

        self._reference_genes_model = reference_genes_model

        self._interest_genes_model = interest_genes_model

        self._dynamic_matrices = None

        self._ct_power_per_gene = None

        self._delta_ct_matrices = collections.OrderedDict()

        self._pow_delta_ct_matrices = collections.OrderedDict()

        self._geom_means = pd.DataFrame()

        self._ratio_matrices = collections.OrderedDict()

        self._ratio_matrices_per_group = collections.OrderedDict()

    @property
    def delta_ct_matrices(self):
        return self._delta_ct_matrices

    @property
    def pow_delta_ct_matrices(self):
        return self._pow_delta_ct_matrices

    @property
    def geom_means(self):
        return self._geom_means

    @property
    def ratio_matrices(self):
        return self._ratio_matrices

    @property
    def ratio_matrices_per_group(self):
        return self._ratio_matrices_per_group

    def set_ct_power_per_gene(self, ct_power_per_gene):

        self._ct_power_per_gene = ct_power_per_gene

    def on_set_dynamic_matrices(self, dynamic_matrices):
        """Event handler which set the dynamic matrices.

        Args:
            _dynamic_matrices (collections.OrderedDict: the dynamic matrices
        """

        self._dynamic_matrices = dynamic_matrices

    def _compute_delta_ct_matrices(self):

        all_samples = sorted(self._rawdata_model.samples)

        control_samples = self._groups_model.get_group_control_contents()

        genes = self._rawdata_model.genes

        ct_control = pd.DataFrame(np.nan, index=GenesModel.zones, columns=genes)
        for gene in genes:
            for zone in GenesModel.zones:
                temp = []
                for sample in control_samples:
                    temp.extend(self._dynamic_matrices[gene].loc[zone, sample])
                ct_control.loc[zone, gene] = np.average(temp)

        delta_ct = collections.OrderedDict()
        for gene in genes:
            delta_ct[gene] = pd.DataFrame(np.nan, index=GenesModel.zones, columns=all_samples)
            for zone in GenesModel.zones:
                for sample in all_samples:
                    delta_ct[gene].loc[zone, sample] = ct_control.loc[zone, gene] - np.average(self._dynamic_matrices[gene].loc[zone, sample])

        return delta_ct

    def compute_rq_matrix(self):
        """Compute the RQ matrix.

        Args:
            ct_power_per_gene (float): the power used for computing the CT matrix per gene
        """

        if not self._ct_power_per_gene:
            return

        if not self._dynamic_matrices:
            return

        all_samples = sorted(self._rawdata_model.samples)

        zones = GenesModel.zones

        self._delta_ct_matrices = self._compute_delta_ct_matrices()

        # Compute the power of the delta ct matrix
        self._pow_delta_ct_matrices = collections.OrderedDict()
        for gene in self._delta_ct_matrices:
            power = self._ct_power_per_gene.get(gene, 2.00)
            self._pow_delta_ct_matrices[gene] = pow(power, self._delta_ct_matrices[gene])

        # Compute the geometric mean matrix over the reference genes
        self._geom_means = pd.DataFrame(np.nan, index=zones, columns=all_samples)
        reference_genes = self._reference_genes_model.items
        for zone in GenesModel.zones:
            for sample in all_samples:
                values = []
                for ref_gene in reference_genes:
                    values.append(self._pow_delta_ct_matrices[ref_gene].loc[zone, sample])
                self._geom_means.loc[zone, sample] = stats.gmean(values)

        # Compute the ratio matrices for each gene of interest
        self._ratio_matrices = collections.OrderedDict()
        interest_genes = self._interest_genes_model.items
        for gene in interest_genes:
            self._ratio_matrices[gene] = self._pow_delta_ct_matrices[gene]/self._geom_means

        # Compute the ratio matrices per group
        self._ratio_matrices_per_group = collections.OrderedDict()
        # Loop over the genes of interest
        for gene in interest_genes:
            self._ratio_matrices_per_group[gene] = pd.DataFrame(index=GenesModel.zones)
            for group, model, selected in self._groups_model.groups:
                if not selected:
                    continue
                samples_in_group = model.items
                self._ratio_matrices_per_group[gene][group] = self._ratio_matrices[gene].loc[GenesModel.zones, samples_in_group].mean(axis=1).tolist()

    def export(self, workbook):
        """
        """

        self.export_rq_statistics(workbook)
        self.export_genes(workbook)

    def export_rq_statistics(self, workbook):
        """
        """

        worksheet = workbook.create_sheet('Delta ct matrices')
        comp = 1
        for gene, df in self._delta_ct_matrices.items():
            worksheet.cell(row=comp, column=1).value = gene
            dataframe_to_excel(worksheet, comp+1, df)
            comp += df.shape[0] + 3

        worksheet = workbook.create_sheet('Pow delta ct matrices')
        comp = 1
        for gene, df in self._pow_delta_ct_matrices.items():
            worksheet.cell(row=comp, column=1).value = gene
            dataframe_to_excel(worksheet, comp+1, df)
            comp += df.shape[0] + 3

        worksheet = workbook.create_sheet('Geometric means')
        dataframe_to_excel(worksheet, 1, self._geom_means)

        worksheet = workbook.create_sheet('Ratio matrices')
        comp = 1
        for gene, df in self._ratio_matrices.items():
            worksheet.cell(row=comp, column=1).value = gene
            dataframe_to_excel(worksheet, comp+1, df)
            comp += df.shape[0] + 3

        worksheet = workbook.create_sheet('Ratio matrices per group')
        comp = 1
        for gene, df in self._ratio_matrices_per_group.items():
            worksheet.cell(row=comp, column=1).value = gene
            dataframe_to_excel(worksheet, comp+1, df)
            comp += df.shape[0] + 3

    def export_genes(self, workbook):
        """
        """

        worksheet = workbook.create_sheet('Genes')

        worksheet.cell(row=1, column=1).value = 'reference'
        worksheet.cell(row=1, column=2).value = 'interest'

        for i, item in enumerate(self._reference_genes_model.items):
            worksheet.cell(row=i+2, column=1).value = item

        for i, item in enumerate(self._interest_genes_model.items):
            worksheet.cell(row=i+2, column=2).value = item
