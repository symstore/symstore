from os import path
from gi.repository import GCab
from gi.repository import Gio


def compress(src_path, dest_path):
    cab_file = GCab.File.new_with_file(path.basename(src_path),
                                       Gio.File.new_for_path(src_path))

    cab_folder = GCab.Folder.new(GCab.Compression.MSZIP)
    cab_folder.add_file(cab_file, False)

    cab = GCab.Cabinet.new()
    cab.add_folder(cab_folder)

    out_file = Gio.File.new_for_path(dest_path)
    cab.write_simple(out_file.create(Gio.FileCreateFlags.NONE))
