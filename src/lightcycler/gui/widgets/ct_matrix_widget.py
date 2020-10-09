from PyQt5 import QtCore, QtWidgets

from lightcycler.gui.views.copy_pastable_tableview import CopyPastableTableView
from lightcycler.kernel.models.ct_matrix_model import CTMatrixModel


class CTMatrixWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):

        super(CTMatrixWidget, self).__init__(*args, **kwargs)

        self._init_ui()

    def _build_layout(self):
        """Build the layout of the widget.
        """

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addWidget(self._ct_matrix_tableview)

        self.setLayout(main_layout)

    def _build_widgets(self):
        """Build the widgets of the widget.
        """

        self._ct_matrix_tableview = CopyPastableTableView(delimiter=',')
        ct_matrix_model = CTMatrixModel(self)
        self._ct_matrix_tableview.setModel(ct_matrix_model)

    def _init_ui(self):
        """Initialize the ui.
        """

        self._build_widgets()
        self._build_layout()

    def model(self):
        """Return the CT matrix underlying model.
        """

        return self._ct_matrix_tableview.model()
