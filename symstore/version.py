from os import path

ver_path = path.join(path.dirname(__file__), "VERSION")
VERSION = open(ver_path).read().strip()
