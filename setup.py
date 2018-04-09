from cx_Freeze import setup, Executable

includefiles = ['session.json', 'default.json', 'settings.json']

setup(name="KTorrent",
      version="0.1",
      description="",
      options={'build_exe': {'include_files':includefiles}},
      executables=[Executable("KTorrent.py")],
)