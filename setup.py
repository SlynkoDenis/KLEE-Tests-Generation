import clang.cindex

from config import Config


def setup(conf: Config):
    clang.cindex.Config.set_library_file(conf.LIBCLANG_PATH)
