import PyInstaller.__main__
import os, shutil, platform

UPX_PATH = os.environ["UPX_PATH"]
CWD = os.path.dirname(os.path.abspath(__file__))

c_plat= platform.system().lower()

b_dir = "win" if c_plat == "windows" else ("lin" if c_plat == "linux" else "mac")

PyInstaller.__main__.run([
        '--noconfirm',
        '--upx-dir=%s' % (UPX_PATH),
        '--log-level=WARN',
        '--onefile',
        '--name=PYBCLI',
        "cli/main.py",
    ])


# Only run this on last stage which is windows build stage
# Add other to dist
to_add = {
    "backups.ini.template": "cli/backups.ini.template",
}
t_dest = "%s/dist/" % (CWD)
if c_plat == "windows":
    for f in to_add:
        f_src = "%s/%s" % (CWD, to_add[f])
        f_dest = t_dest + f
        if not os.path.isfile(f_dest):
            shutil.copyfile(f_src, f_dest)
