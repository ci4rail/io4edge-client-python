class FirmwareIdentification:
    """
    Class to hold firmware identification information.
    Contains the title and version of the firmware.
    """
    def __init__(self, title: str, version: str):
        self.title = title
        self.version = version

    def __str__(self):
        return f"{self.title} v{self.version}"

class HardwareIdentification:
    """
    Class to hold hardware identification information.
    Contains the title and version of the hardware.
    """
    def __init__(self, root_article: str, major_version: str, serial_number: str):
        self.root_article = root_article
        self.major_version = major_version
        self.serial_number = serial_number

    def __str__(self):
        return f"{self.root_article} v{self.major_version} SN: {self.serial_number}"
