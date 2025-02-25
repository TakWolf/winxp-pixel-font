import zipfile

from loguru import logger

from tools import configs
from tools.configs import path_define, FontFormat
from tools.services.font_service import DumpLog


def make_release_zip(dump_logs: list[DumpLog], font_formats: list[FontFormat]):
    path_define.releases_dir.mkdir(parents=True, exist_ok=True)
    for font_format in font_formats:
        file_path = path_define.releases_dir.joinpath(f'winxp-pixel-font-{font_format}-v{configs.version}.zip')
        with zipfile.ZipFile(file_path, 'w') as file:
            for dump_log in dump_logs:
                file_path = path_define.outputs_dir.joinpath(f'{dump_log.font_name}-{dump_log.font_size}px.{font_format}')
                file.write(file_path, file_path.name)
        logger.info("Make release zip: '{}'", file_path)
