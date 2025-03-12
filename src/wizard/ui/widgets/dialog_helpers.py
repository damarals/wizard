"""
Helper functions for styling dialogs consistently.
"""

from PySide6.QtWidgets import QDialogButtonBox

from wizard.ui.icons import get_icon
from wizard.ui.theme import ThemeColors


def style_dialog_buttons(dialog, button_box):
    """
    Apply consistent styling to dialog buttons.

    Args:
        dialog: The QDialog instance
        button_box: The QDialogButtonBox instance
    """
    # Get buttons - need to use StandardButton enum in PySide6
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok) or button_box.button(
        QDialogButtonBox.StandardButton.Save
    )
    cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

    # Style the OK/Accept button with primary color
    if ok_button:
        # Use white icon for primary button
        ok_button.setIcon(get_icon("CHECK", color="#FFFFFF"))
        ok_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ThemeColors.PRIMARY};
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #5448ca;
            }}
            QPushButton:pressed {{
                background-color: #3d31a3;
            }}
        """
        )

    # Style the Cancel button with lighter styling
    if cancel_button:
        cancel_button.setIcon(get_icon("X"))
        cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e9ecef;
                color: #212529;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
            QPushButton:pressed {
                background-color: #ced4da;
            }
        """
        )


def setup_dialog_header(dialog, title, icon_name=None):
    """
    Set up the dialog's title and icon.

    Args:
        dialog: The QDialog instance
        title: Dialog title
        icon_name: TablerIcon name to use
    """
    dialog.setWindowTitle(title)

    # Set minimum width for all dialogs
    dialog.setMinimumWidth(600)

    if icon_name:
        dialog.setWindowIcon(get_icon(icon_name))
