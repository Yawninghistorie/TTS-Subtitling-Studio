"""
Color constants for Flet compatibility
"""

# Material Design Colors (Hex)
class Colors:
    # Primary
    DEEP_PURPLE = "#673AB7"
    DEEP_PURPLE_200 = "#B39DDB"
    DEEP_PURPLE_300 = "#9575CD"
    
    # Surface
    SURFACE_CONTAINER_HIGH = "#1C1B1F"
    SURFACE_CONTAINER_HIGHEST = "#312B36"
    SURFACE_CONTAINER_LOW = "#1D1B20"
    SURFACE_CONTAINER_LOWEST = "#121212"
    
    # Common
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    GREY_400 = "#BDBDBD"
    GREY_500 = "#9E9E9E"
    
    # Semantic
    ERROR = "#F44336"
    WARNING = "#FF9800"
    SUCCESS = "#4CAF50"
    INFO = "#2196F3"
    
    # Cyan/Yellow for UI
    CYAN_200 = "#80DEEA"
    YELLOW_200 = "#FFE082"
    YELLOW_300 = "#FFD54F"
    
    # Borders
    OUTLINE = "#79747E"
    OUTLINE_VARIANT = "#49454F"
    
    # Misc
    TRANSPARENT = "#00000000"


# Icons shortcuts
ICONS = {
    "play_arrow": "PLAY_ARROW",
    "pause": "PAUSE",
    "stop": "STOP",
    "translate": "TRANSLATE",
    "settings": "SETTINGS",
    "info_outline": "INFO_OUTLINE",
    "dark_mode": "DARK_MODE",
    "upload_file": "UPLOAD_FILE",
    "folder_open": "FOLDER_OPEN",
    "subscript": "SUBSCRIPT",
    "close": "CLOSE",
    "mic": "MIC",
    "add": "ADD",
    "delete": "DELETE",
    "undo": "UNDO",
    "redo": "REDO",
    "search": "SEARCH",
    "play_circle_fill": "PLAY_CIRCLE_FILLED",
    "edit": "EDIT",
    "save": "SAVE",
    "graphic_eq": "GRAPHIC_EQ",
}

def get_icon(name):
    """Get icon name."""
    return ICONS.get(name, name.upper().replace("-", "_"))