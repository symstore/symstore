from os import path
from symstore import fileio

ver_path = path.join(path.dirname(__file__), "VERSION")
VERSION = fileio.read_all(ver_path).strip()
