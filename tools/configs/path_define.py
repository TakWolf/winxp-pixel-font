from pathlib import Path

PROJECT_ROOT_DIR = Path(__file__).parent.joinpath('..', '..').resolve()

ASSETS_DIR = PROJECT_ROOT_DIR.joinpath('assets')
FONTS_DIR = ASSETS_DIR.joinpath('fonts')

BUILD_DIR = PROJECT_ROOT_DIR.joinpath('build')
OUTPUTS_DIR = BUILD_DIR.joinpath('outputs')
RELEASES_DIR = BUILD_DIR.joinpath('releases')

WWW_DIR = PROJECT_ROOT_DIR.joinpath('www')
WWW_FONTS_DIR = WWW_DIR.joinpath('fonts')
