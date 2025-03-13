"""
Theme management for the Wizard application.
"""

import qdarktheme


# Application theme colors
class ThemeColors:
    PRIMARY = "#463ABE"
    SECONDARY = "#6C757D"
    SUCCESS = "#28A745"
    DANGER = "#DC3545"
    WARNING = "#FFC107"
    INFO = "#17A2B8"
    LIGHT = "#F8F9FA"
    DARK = "#343A40"
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#E9ECEF"
    MEDIUM_GRAY = "#CED4DA"
    DARK_GRAY = "#6C757D"
    BLACK = "#000000"

    # Status colors for query table
    STATUS_IDLE = "#F8F9FA"  # Light gray
    STATUS_RUNNING = "#FFF3CD"  # Light yellow
    STATUS_STOPPED = "#E2E3E5"  # Medium gray
    STATUS_COMPLETED = "#D4EDDA"  # Light green
    STATUS_ERROR = "#F8D7DA"  # Light red


def setup_theme(theme_mode="light"):
    """
    Set up the application theme.

    Args:
        theme_mode: Theme mode ('dark', 'light', or 'auto')

    Returns:
        Stylesheet string
    """
    # Configure qdarktheme with custom colors
    custom_colors = {
        "primary": ThemeColors.PRIMARY,
    }

    # Load stylesheet
    return qdarktheme.load_stylesheet(
        theme=theme_mode,
        corner_shape="rounded",
        custom_colors=custom_colors,
    )


def get_additional_stylesheet():
    """
    Get additional stylesheet rules to customize the application appearance.

    Returns:
        CSS stylesheet string
    """
    return f"""
    /* Button styling */
    QPushButton {{
        border-radius: 4px;
        padding: 5px 10px;
    }}
    
    QPushButton:hover {{
        background-color: rgba(70, 58, 190, 0.13);
    }}
    
    QPushButton:pressed {{
        background-color: rgba(70, 58, 190, 0.20);
    }}
    
    QPushButton:checked {{
        background-color: {ThemeColors.PRIMARY};
        color: {ThemeColors.WHITE};
    }}
    
    /* Primary action button styling */
    QPushButton.primary-action {{
        background-color: {ThemeColors.PRIMARY};
        color: white;
        font-weight: bold;
        border-radius: 4px;
        padding: 6px 12px;
    }}

    QPushButton.primary-action QIcon {{
        color: white;
    }}
    
    QPushButton.primary-action:hover {{
        background-color: #5448ca;
    }}
    
    QPushButton.primary-action:pressed {{
        background-color: #3d31a3;
    }}
    
    QPushButton.primary-action:disabled {{
        background-color: #9b96c9;
        color: #e0e0e0;
    }}
    
    /* Icon button styling */
    QPushButton.icon-button {{
        background-color: transparent;
        border-radius: 3px;
        padding: 3px;
    }}
    
    QPushButton.icon-button:hover {{
        background-color: #dfe3e8;
    }}
    
    QPushButton.icon-button:pressed {{
        background-color: #ced4da;
    }}
    
    /* Progress bar styling */
    QProgressBar {{
        border: 1px solid {ThemeColors.MEDIUM_GRAY};
        border-radius: 4px;
        background-color: {ThemeColors.LIGHT_GRAY};
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: rgba(70, 58, 190, 0.4);
        width: 10px;
        margin: 0px;
        border-radius: 0px;
    }}
    
    /* Table styling */
    QTableWidget {{
        gridline-color: {ThemeColors.LIGHT_GRAY};
        selection-background-color: rgba(70, 58, 190, 0.11);
    }}
    
    QTableWidget::item:hover {{
        background-color: rgba(70, 58, 190, 0.08);
    }}
    
    QTableWidget::item:selected {{
        background-color: rgba(70, 58, 190, 0.20);
        color: {ThemeColors.BLACK};
    }}
    
    QHeaderView::section {{
        background-color: {ThemeColors.LIGHT_GRAY};
        border: 1px solid {ThemeColors.MEDIUM_GRAY};
        padding: 4px;
    }}
    
    /* Empty state styling */
    .EmptyStateLabel {{
        color: {ThemeColors.DARK_GRAY};
        font-size: 14px;
    }}

    /* QSplitter styling */
    QSplitter::handle {{
        background-color: {ThemeColors.LIGHT_GRAY};
        height: 1px; 
        width: 1px;
    }}
    
    QSplitter::handle:horizontal {{
        margin-top: 1px;
        margin-bottom: 1px;
        height: 1px;
        background-color: {ThemeColors.LIGHT_GRAY};
    }}
    
    QSplitter::handle:pressed {{
        background-color: {ThemeColors.PRIMARY};
    }}
    """


def create_primary_button(text, icon_name=None, callback=None):
    """
    Create a primary action button with proper styling.

    Args:
        text: Button text
        icon_name: Name of TablerIcon to use (optional)
        callback: Function to call when clicked (optional)

    Returns:
        QPushButton instance
    """
    from PySide6.QtWidgets import QPushButton

    from wizard.ui.icons import get_icon

    button = QPushButton(text)
    button.setProperty("class", "primary-action")

    if icon_name:
        button.setIcon(get_icon(icon_name, color="#FFFFFF"))

    if callback:
        button.clicked.connect(callback)

    return button
