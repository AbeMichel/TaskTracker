from PyQt6.QtGui import QColor

class ColorHex:
    def __init__(self, hex_code: str):
        self.hex = hex_code

    def toQColor(self) -> QColor:
        return QColor(self.hex)

    def __str__(self):
        return self.hex

    def __repr__(self):
        return f"Color({self.hex})"


class COLORS:
    Red        = ColorHex("#FF6B6B")
    Pink       = ColorHex("#FF9AA2")
    Purple     = ColorHex("#C49BBB")
    DeepPurple = ColorHex("#A093C7")
    Indigo     = ColorHex("#8CA6DB")
    Blue       = ColorHex("#6BAED6")
    LightBlue  = ColorHex("#63C5DA")
    Cyan       = ColorHex("#56D4DD")
    Teal       = ColorHex("#4DB6AC")
    Green      = ColorHex("#6FCF97")
    LightGreen = ColorHex("#A0E6A3")
    Lime       = ColorHex("#D2F898")
    Amber      = ColorHex("#FFE066")
    Orange     = ColorHex("#FFA94D")
    Brown      = ColorHex("#B28D6B")

