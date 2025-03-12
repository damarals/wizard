"""
src/wizard/ui/icons.py - Icons module for the Wizard application.
"""

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QStyle
from pytablericons import FilledIcon, OutlineIcon, TablerIcons

from ..utils.logger import get_logger
from .theme import ThemeColors

logger = get_logger(__name__)

# Default primary color for icons
DEFAULT_ICON_COLOR = ThemeColors.PRIMARY


def get_icon(icon_name, size=24, color=None):
    """
    Get a TablerIcon by name.

    Args:
        icon_name: Name of the icon (e.g., 'SEARCH', 'PLUS')
        size: Icon size in pixels
        color: Icon color (hex string)

    Returns:
        QIcon object
    """
    if color is None:
        color = DEFAULT_ICON_COLOR

    try:
        # Try to get from OutlineIcon first
        try:
            icon_const = getattr(OutlineIcon, icon_name)
            pillow_image = TablerIcons.load(icon_const, size=size, color=color)
        except (AttributeError, ValueError):
            # If not in OutlineIcon, try FilledIcon
            icon_const = getattr(FilledIcon, icon_name)
            pillow_image = TablerIcons.load(icon_const, size=size, color=color)

        # Convert to QIcon
        qpixmap = pillow_image.toqpixmap()
        return QIcon(qpixmap)
    except Exception as e:
        logger.warning(f"Error loading icon {icon_name}: {e}")
        return QIcon()


# Mapping from Qt standard icons to TablerIcons
ICON_MAPPING = {
    QStyle.SP_FileDialogNewFolder: "FOLDER_PLUS",
    QStyle.SP_FileDialogDetailedView: "SETTINGS",
    QStyle.SP_DialogSaveButton: "DEVICE_FLOPPY",
    QStyle.SP_DialogOkButton: "CHECK",
    QStyle.SP_DialogCancelButton: "X",
    QStyle.SP_MediaPlay: "PLAYER_PLAY",
    QStyle.SP_MediaPause: "PLAYER_PAUSE",
    QStyle.SP_TrashIcon: "TRASH",
    QStyle.SP_ArrowBack: "ARROW_LEFT",
    QStyle.SP_ArrowForward: "ARROW_RIGHT",
    QStyle.SP_ArrowUp: "ARROW_UP",
    QStyle.SP_ArrowDown: "ARROW_DOWN",
    QStyle.SP_DialogHelpButton: "HELP",
    QStyle.SP_DialogCloseButton: "X",
    QStyle.SP_FileIcon: "FILE",
    QStyle.SP_DirIcon: "FOLDER",
    QStyle.SP_DirOpenIcon: "FOLDER_OPEN",
}


def get_standard_icon(standard_icon, size=24, color=None):
    """
    Get a TablerIcon equivalent of a Qt standard icon.

    Args:
        standard_icon: Qt standard icon constant (e.g., QStyle.SP_TrashIcon)
        size: Icon size in pixels
        color: Icon color (hex string)

    Returns:
        QIcon object
    """
    if color is None:
        color = DEFAULT_ICON_COLOR

    # Get the TablerIcon name from the mapping
    tabler_name = ICON_MAPPING.get(standard_icon)

    if tabler_name:
        # Use the TablerIcon
        return get_icon(tabler_name, size, color)
    else:
        # Fallback to Qt standard icon
        return QApplication.style().standardIcon(standard_icon)
