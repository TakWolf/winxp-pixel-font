import datetime
import json

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.BitmapGlyphMetrics import SmallGlyphMetrics, BigGlyphMetrics
from fontTools.ttLib.tables.E_B_D_T_ import table_E_B_D_T_, ebdt_bitmap_classes, ebdt_bitmap_format_5, ebdt_bitmap_format_8, ebdt_bitmap_format_9
from fontTools.ttLib.tables.E_B_L_C_ import table_E_B_L_C_
# noinspection PyProtectedMember
from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e
from loguru import logger
from pixel_font_builder import FontBuilder, Glyph
from pixel_font_builder.opentype import Flavor

from tools import configs
from tools.configs import path_define, FontFormat


class DumpLog:
    font_name: str
    font_size: int
    family_name: str

    def __init__(
            self,
            font_name: str,
            font_size: int,
            family_name: str,
    ):
        self.font_name = font_name
        self.font_size = font_size
        self.family_name = family_name


def dump_fonts(font_formats: list[FontFormat]) -> list[DumpLog]:
    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)

    dump_logs = []
    for dump_config in configs.dump_configs:
        for sub_config in dump_config.sub_configs:
            tt_font = TTFont(dump_config.font_file_path, fontNumber=sub_config.font_number)
            tb_name: table__n_a_m_e = tt_font['name']
            tb_eblc: table_E_B_L_C_ = tt_font['EBLC']
            tb_ebdt: table_E_B_D_T_ = tt_font['EBDT']

            for strike, strike_data in zip(tb_eblc.strikes, tb_ebdt.strikeData):
                assert strike.bitmapSizeTable.ppemX == strike.bitmapSizeTable.ppemY
                assert strike.bitmapSizeTable.bitDepth == 1

                builder = FontBuilder()

                builder.font_metric.font_size = strike.bitmapSizeTable.ppemY
                builder.font_metric.horizontal_layout.ascent = strike.bitmapSizeTable.hori.ascender
                builder.font_metric.horizontal_layout.descent = strike.bitmapSizeTable.hori.descender
                builder.font_metric.vertical_layout.ascent = strike.bitmapSizeTable.vert.ascender
                builder.font_metric.vertical_layout.descent = strike.bitmapSizeTable.vert.descender

                # Fix incorrect descent
                if builder.font_metric.horizontal_layout.descent > 0:
                    builder.font_metric.horizontal_layout.descent *= -1
                if builder.font_metric.vertical_layout.descent > 0:
                    builder.font_metric.vertical_layout.descent *= -1

                builder.meta_info.version = f'{tb_name.getDebugName(5)} - Dump {configs.version}'
                builder.meta_info.created_time = datetime.datetime.fromisoformat(f'{configs.version.replace('.', '-')}T00:00:00Z')
                builder.meta_info.modified_time = builder.meta_info.created_time
                builder.meta_info.family_name = f'{tb_name.getDebugName(1)} {builder.font_metric.font_size}px'
                builder.meta_info.weight_name = sub_config.weight_name
                builder.meta_info.serif_style = sub_config.serif_style
                builder.meta_info.slant_style = sub_config.slant_style
                builder.meta_info.width_style = sub_config.width_style
                builder.meta_info.manufacturer = tb_name.getDebugName(8)
                builder.meta_info.designer = tb_name.getDebugName(9)
                builder.meta_info.description = tb_name.getDebugName(10)
                builder.meta_info.copyright_info = tb_name.getDebugName(0)
                builder.meta_info.license_info = tb_name.getDebugName(13)
                builder.meta_info.vendor_url = tb_name.getDebugName(11)
                builder.meta_info.designer_url = tb_name.getDebugName(12)
                builder.meta_info.license_url = tb_name.getDebugName(14)

                glyph_data_cache = {}
                for index_sub_table in strike.indexSubTables:
                    for glyph_name in index_sub_table.names:
                        assert glyph_name not in glyph_data_cache
                        glyph_data_cache[glyph_name] = {
                            'image_format': index_sub_table.imageFormat,
                            'metrics': index_sub_table.metrics if hasattr(index_sub_table, 'metrics') else None,
                        }

                glyph_names = set()
                for glyph_name, bitmap_data in strike_data.items():
                    glyph_data = glyph_data_cache[glyph_name]
                    assert isinstance(bitmap_data, ebdt_bitmap_classes[glyph_data['image_format']])
                    if isinstance(bitmap_data, ebdt_bitmap_format_5):
                        metrics = glyph_data['metrics']
                    elif isinstance(bitmap_data, (ebdt_bitmap_format_8, ebdt_bitmap_format_9)):
                        # TODO
                        # https://github.com/NightFurySL2001/fonttools/tree/fix_ebdt
                        continue
                    else:
                        metrics = bitmap_data.metrics

                    bitmap_height = metrics.height
                    if isinstance(metrics, SmallGlyphMetrics):
                        if strike.bitmapSizeTable.flags == 1:  # Horizontal
                            hori_bearing_x = metrics.BearingX
                            hori_bearing_y = metrics.BearingY
                            hori_advance = metrics.Advance
                            vert_bearing_x = 0
                            vert_bearing_y = 0
                            vert_advance = 0
                        else:  # Vertical
                            assert strike.bitmapSizeTable.flags == 2
                            hori_bearing_x = 0
                            hori_bearing_y = 0
                            hori_advance = 0
                            vert_bearing_x = metrics.BearingX
                            vert_bearing_y = metrics.BearingY
                            vert_advance = metrics.Advance
                    else:
                        assert isinstance(metrics, BigGlyphMetrics)
                        hori_bearing_x = metrics.horiBearingX
                        hori_bearing_y = metrics.horiBearingY
                        hori_advance = metrics.horiAdvance
                        vert_bearing_x = metrics.vertBearingX
                        vert_bearing_y = metrics.vertBearingY
                        vert_advance = metrics.vertAdvance

                    bitmap = []
                    for row_n in range(bitmap_height):
                        row_bytes = bitmap_data.getRow(row_n, bitDepth=strike.bitmapSizeTable.bitDepth, metrics=metrics)
                        row_string = ''
                        for b in row_bytes:
                            row_string += f'{b:08b}'
                        bitmap.append([int(c) for c in row_string])

                    builder.glyphs.append(Glyph(
                        name=glyph_name,
                        horizontal_origin=(hori_bearing_x, hori_bearing_y - bitmap_height),
                        advance_width=hori_advance,
                        vertical_origin=(vert_bearing_x, vert_bearing_y),
                        advance_height=vert_advance,
                        bitmap=bitmap,
                    ))
                    glyph_names.add(glyph_name)

                if '.notdef' not in glyph_names:
                    builder.glyphs.insert(0, Glyph(
                        name='.notdef',
                        advance_width=builder.font_metric.font_size,
                        advance_height=builder.font_metric.font_size,
                    ))

                for code_point, glyph_name in tt_font.getBestCmap().items():
                    if glyph_name in glyph_names:
                        builder.character_mapping[code_point] = glyph_name

                for font_format in font_formats:
                    file_path = path_define.outputs_dir.joinpath(f'{sub_config.font_name}-{builder.font_metric.font_size}px.{font_format}')
                    if font_format == 'woff2':
                        builder.save_otf(file_path, flavor=Flavor.WOFF2)
                    else:
                        getattr(builder, f'save_{font_format}')(file_path)
                    logger.info("Make font: '{}'", file_path)

                dump_logs.append(DumpLog(
                    font_name=sub_config.font_name,
                    font_size=builder.font_metric.font_size,
                    family_name=builder.meta_info.family_name,
                ))

    path_define.outputs_dir.joinpath('dump-logs.json').write_text(json.dumps([dump_log.__dict__ for dump_log in dump_logs], indent=2, ensure_ascii=False), 'utf-8')

    return dump_logs
