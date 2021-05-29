import os

# this flag is false on systems that don't provide gcab library
compression_supported = True

if os.name == 'nt':
    # Use built-in makecab CLI utility on Windows OSes (included in PATH on all Windows versions)
    import subprocess
else:
    try:
        import gi
        gi.require_version('GCab', '1.0')
        from gi.repository import GCab
        from gi.repository import Gio
    except ValueError:
        compression_supported = False
    except ImportError:
        compression_supported = False


def compress(src_path, dest_path):
    assert compression_supported
    if os.name == 'nt':
        args = ['makecab', '/D', 'CompressionType=LZX', '/D', 'CompressionMemory=21', src_path, dest_path]
        subprocess.run(args, check=True, capture_output=True)
    else:
        cab_file = GCab.File.new_with_file(os.path.basename(src_path),
                                           Gio.File.new_for_path(src_path))

        cab_folder = GCab.Folder.new(GCab.Compression.MSZIP)
        cab_folder.add_file(cab_file, False)

        cab = GCab.Cabinet.new()
        cab.add_folder(cab_folder)

        out_file = Gio.File.new_for_path(dest_path)
        cab.write_simple(out_file.replace(None,
                                          False,
                                          Gio.FileCreateFlags.REPLACE_DESTINATION,
                                          None))
