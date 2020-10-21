import logging

import numpy as np

from PyQt5 import QtCore


class GenesModel:

    def __init__(self, groups_model, ct_matrix_model, rq_matrix_model, reference_genes_model, interest_genes_model):

        self._groups_model = groups_model
        self._ct_matrix_model = ct_matrix_model
        self._rq_matrix_model = rq_matrix_model
        self._reference_genes_model = reference_genes_model
        self._interest_genes_model = interest_genes_model

    def compute_rq_matrix(self):
        """Compute the RQ matrix.
        """

        reference_genes = [self._reference_genes_model.data(self._reference_genes_model.index(i, 0), QtCore.Qt.DisplayRole)
                           for i in range(self._reference_genes_model.rowCount())]
        if not reference_genes:
            logging.info('No genes of reference defined')
            return

        interest_genes = [self._interest_genes_model.data(self._interest_genes_model.index(i, 0), QtCore.Qt.DisplayRole)
                          for i in range(self._interest_genes_model.rowCount())]
        if not interest_genes:
            logging.info('No genes of interest defined')
            return

        logging.info('Computing RQ matrix. Please wait ...')
        ct_matrix = self._groups_model.compute_ct_matrix()
        if ct_matrix is None:
            return

        self._ct_matrix_model.set_reference_genes(reference_genes)
        self._ct_matrix_model.set_interest_genes(interest_genes)

        self._ct_matrix_model.ct_matrix = ct_matrix

        geom_means = self._groups_model.compute_geometric_means(ct_matrix, reference_genes)

        rq_matrix = ct_matrix.loc[interest_genes]/geom_means.values

        rq_matrix = rq_matrix.round(3)

        self._rq_matrix_model.rq_matrix = rq_matrix

        logging.info('.. done')

    def export(self, workbook):
        """
        """

        self.export_rq_statistics(workbook)
        self.export_genes(workbook)

    def export_rq_statistics(self, workbook):
        """
        """

        interest_genes = self._interest_genes_model.items

        selected_groups = [r for r in range(self._groups_model.rowCount()) if self._groups_model.is_selected(r)]

        n_selected_groups = len(selected_groups)

        rq_matrix = self._rq_matrix_model.rq_matrix
        if rq_matrix.empty:
            return

        worksheet = workbook.create_sheet('statistics-rq')

        # Loop over the genes of interest
        for i, gene in enumerate(interest_genes):

            worksheet.cell(row=(n_selected_groups+2)*i + 1, column=1).value = gene
            worksheet.cell(row=(n_selected_groups+2)*i + 1, column=2).value = "n"
            worksheet.cell(row=(n_selected_groups+2)*i + 1, column=3).value = "mean"

            for j, r in enumerate(selected_groups):
                index = self._groups_model.index(r, 0)
                group_name = self._groups_model.data(index, QtCore.Qt.DisplayRole)
                worksheet.cell(row=(n_selected_groups+2)*i + j + 2, column=1).value = group_name
                group_contents_model = self._groups_model.data(index, self._groups_model.model)
                samples = [group_contents_model.data(group_contents_model.index(s, 0), QtCore.Qt.DisplayRole)
                           for s in range(group_contents_model.rowCount())]
                worksheet.cell(row=(n_selected_groups+2)*i + j + 2, column=2).value = len(samples)
                worksheet.cell(row=(n_selected_groups+2)*i + j + 2, column=3).value = np.mean(rq_matrix.loc[gene, samples].values)

    def export_genes(self, workbook):
        """
        """

        worksheet = workbook.create_sheet('genes')

        worksheet.cell(row=1, column=1).value = 'reference'
        worksheet.cell(row=1, column=2).value = 'interest'

        for i, item in enumerate(self._reference_genes_model.items):
            worksheet.cell(row=i+2, column=1).value = item

        for i, item in enumerate(self._interest_genes_model.items):
            worksheet.cell(row=i+2, column=2).value = item
