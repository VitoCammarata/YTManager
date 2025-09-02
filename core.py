import re

def sanitize_folder_name(name: str) -> str:
    """
    Cleans a string to make it a valid folder name for any operating system.

    Args:
        name: The original string, typically a playlist title.

    Returns:
        A filesystem-safe string to be used as a directory name.
    """
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r'[\x00-\x1f\x7f]', "", name)
    name = re.sub(r'\s+', " ", name).strip()
    name = name.strip('. ')
    return name

def sanitize_title(title: str) -> str:
    """
    Cleans a string to make it a valid file name.

    Args:
        title: The original string, typically a video title.

    Returns:
        A filesystem-safe string to be used as a file name.
    """
    title = re.sub(r"[\'\*\?\"<>]", "", title)
    title = title.replace("[", "(").replace("]", ")")
    title = title.replace("{", "(").replace("}", ")")
    title = re.sub(r"[|\\\/]", "-", title)
    title = re.sub(r"^[\'\*\?\"<>]+", "", title)
    title = re.sub(r"[\'\*\?\"<>]+$", "", title)
    return title