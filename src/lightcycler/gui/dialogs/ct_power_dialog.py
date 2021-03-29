from PyQt5 import QtWidgets


class CTPowerDialog(QtWidgets.QDialog):

    def __init__(self, genes, *args, **kwargs):

        super(CTPowerDialog, self).__init__(*args, **kwargs)

        self._genes = genes

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        self._main_layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()

        for gw in self._gene_widgets:
            form_layout.addRow(*gw)

        self._main_layout.addLayout(form_layout)

        self._main_layout.addWidget(self._button_box)

        self.setLayout(self._main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._gene_widgets = []

        for gene in self._genes:
            gene_label = QtWidgets.QLabel(gene)
            gene_spinbox = QtWidgets.QDoubleSpinBox()
            gene_spinbox.setValue(2.000)
            gene_spinbox.setMinimum(0.001)
            gene_spinbox.setMaximum(4.000)
            gene_spinbox.setSingleStep(0.001)
            gene_spinbox.setDecimals(3)
            self._gene_widgets.append([gene_label, gene_spinbox])

        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)

        self.setWindowTitle('CT power per gene')

    def _init_ui(self):

        self._build_widgets()
        self._build_layout()

    @property
    def ct_powers(self):

        return dict([(l.text(), w.value()) for l, w in self._gene_widgets])
