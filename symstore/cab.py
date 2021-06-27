from __future__ import absolute_import

import os
from symstore import errs

# 'points' to suitable cab compression function,
# as initilized on module import
# None if compression is not supported
compress = None


def _compress_gcab(src_path, dest_path):
    """
    compress using GCab library
    """
    cab_file = GCab.File.new_with_file(os.path.basename(src_path),
                                       Gio.File.new_for_path(src_path))

    cab_folder = GCab.Folder.new(GCab.Compression.MSZIP)
    cab_folder.add_file(cab_file, False)

    cab = GCab.Cabinet.new()
    cab.add_folder(cab_folder)

    out_file = Gio.File.new_for_path(dest_path)
    cab.write_simple(
        out_file.replace(None,
                         False,
                         Gio.FileCreateFlags.REPLACE_DESTINATION,
                         None))


def _compress_makecab(src_path, dest_path):
    """
    compress by running 'makecab.exe' utility
    """
    args = ["makecab.exe", "/D", "CompressionType=LZX",
            "/D", "CompressionMemory=21", src_path, dest_path]

    # use Popen() API to launch makecab.exe,
    # as this is the only suitable API available in python 2.7 and 3.4
    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, _ = proc.communicate()

    if proc.returncode != 0:
        raise errs.CabCompressionError("%s" % out.decode())


if os.name != "nt":
    #
    # For non-windows systems, check if GCab library is available,
    # and use gcab based compression if it's available
    #
    try:
        import gi
        gi.require_version("GCab", "1.0")
        from gi.repository import GCab
        from gi.repository import Gio

        compress = _compress_gcab
    except ValueError:
        pass
    except ImportError:
        pass
else:
    #
    # On windows systems, use built-in 'makecab' based compression
    #
    import subprocess
    compress = _compress_makecab
