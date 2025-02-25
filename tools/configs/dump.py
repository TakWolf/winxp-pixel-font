from pathlib import Path

from pixel_font_builder import WeightName, SerifStyle, SlantStyle, WidthStyle

from tools.configs import path_define


class SubConfig:
    font_number: int
    font_name: str
    weight_name: WeightName
    serif_style: SerifStyle
    slant_style: SlantStyle
    width_style: WidthStyle

    def __init__(
            self,
            font_number: int,
            font_name: str,
            weight_name: WeightName = WeightName.REGULAR,
            serif_style: SerifStyle = SerifStyle.SERIF,
            slant_style: SlantStyle = SlantStyle.NORMAL,
            width_style: WidthStyle = WidthStyle.MONOSPACED,
    ):
        self.font_number = font_number
        self.font_name = font_name
        self.weight_name = weight_name
        self.serif_style = serif_style
        self.slant_style = slant_style
        self.width_style = width_style


class DumpConfig:
    font_file_path: Path
    sub_configs: list[SubConfig]

    def __init__(
            self,
            font_file_name: str,
            sub_configs: list[SubConfig],
    ):
        self.font_file_path = path_define.fonts_dir.joinpath(font_file_name)
        self.sub_configs = sub_configs
