import os, zipfile, zlib, datetime, shutil, sys

class BackupManager(object):
    """docstring for BackupManager."""
    def __init__(self, args, logger, config):
        super(BackupManager, self).__init__()
        self.u_args = args
        self.logger = logger
        self.config = config
        self.z_name = "backups.zip" if not args.z_name else args.z_name.strip()
        if not self.z_name.endswith(".zip"):
            self.z_name = self.z_name + ".zip"
        path_s = None
        try:
            path_s = args.path_s if args.path_s else config["BACKUPS"]["path_s"]
            # Check if path_s is not an empty string
            if path_s == "" or path_s == " ":
                raise ValueError
        except Exception as e:
            logger.critical("Missing path values, exiting...")
            sys.exit(1)
        # Try to split path
        path_s = path_s.split(" ") if " " in path_s else path_s.split("\n")
        # Remove any possible whitespaces
        path_s = [v for v in path_s if v != ""]
        self.path_s = path_s
        self.add_date = self.set_or_default("add_date")
        d_format = self.set_or_default("date_format")
        d_format = d_format.replace("&", "%")
        self.date_format = d_format
        u_path = self.set_or_default("temp")
        self.tmp_dir = os.path.abspath(u_path)
        logger.info("BackupManager initialized\n")

    # For setting defaults when values are missing
    def set_or_default(self, name):
        vals = {
            "add_date": True,
            "temp": "temp",
            "date_format": "&d-&m-&Y",
            "make_zip": "y",
            "over_creds": "n",
            "dest_folder": "PYBCLI",
        }
        val = None
        try:
            if name == "temp":
                val = self.u_args.temp if self.u_args.temp else self.config["BACKUPS"]["temp"]
                if not val:
                    val = "temp"
            elif name == "add_date":
                val = self.u_args.add_date if self.u_args.add_date else self.config["BACKUPS"]["add_date"]
                val = True if val == "y" else False
            elif name == "date_format":
                d_formats = ["&d-&m-&Y", "&d-&Y-&m" "&m-&d-&Y", "&m-&Y-&d", "&Y-&m-&d", "&Y-&d-&m"]
                val = self.u_args.date_format if self.u_args.date_format else str(self.config["BACKUPS"]["date_format"])
                if val not in d_formats:
                    self.logger.debug("Invalid date format %s\n" % (val))
                    raise KeyError
            elif name == "make_zip":
                val = self.u_args.make_zip if self.u_args.make_zip else self.config["BACKUPS"]["make_zip"]
            elif name == "over_creds":
                val = self.u_args.over_creds if self.u_args.over_creds else self.config["BACKUPS"]["over_creds"]
            elif name == "dest_folder":
                val = self.u_args.dest_folder if self.u_args.dest_folder else self.config["BACKUPS"]["dest_folder"]
            if val == "" or val == " ":
                raise KeyError
        except KeyError:
            self.logger.debug("Missing parameter from config and arguments: %s\nSetting to default: %s" % (name, vals[name]))
            return vals[name]
        return val

    # Check if paths exist
    def check_paths(self):
        self.logger.info("Checking paths before proceeding\n")
        if not self.path_s:
            self.logger.critical("Couldn't find any paths, have you provided them in the config or by arguments?")
            return False
        path_s = self.path_s
        if isinstance(path_s, list):
            f_list = { v:True for v in path_s}
            for src in path_s:
                src = os.path.abspath(src)
                check = os.path.isdir if os.path.isdir(src) else os.path.isfile
                if not check(src):
                    f_list[src] = False
                    self.logger.info("Failed to find path: %s\n" % (src))
            c_list = [False for v in f_list if f_list[v] == False]
            # # TODO: If false in c_list ask to continue...
            if False in c_list:
                self.logger.critical("Missing path, cannot resume: Not implemented\n")
                return False
        else:
            check = os.path.isdir if os.path.isdir(path_s) else os.path.isfile
            if not check(path_s):
                self.logger.critical("Cant find path %s\n" % (path_s))
                return False
        return True
        self.logger.info("Found path(s) %s\n" % (self.path_s))

    # Copy to specified tmp dir
    def call_copy(self):
        self.logger.info("Copying files to temporary dir\n")
        path_s = self.path_s
        if os.path.isdir(self.tmp_dir):
            self.logger.debug("Removing temp dir")
            shutil.rmtree(self.tmp_dir)
        tmp_dir = os.path.abspath(self.tmp_dir)
        if not isinstance(path_s, list):
            abspath_s = os.path.abspath(path_s)
            d_copy = shutil.copytree if os.path.isdir(abspath_s) else shutil.copy
            if d_copy == shutil.copy:
                if not os.path.isdir(self.tmp_dir):
                    os.mkdir(self.tmp_dir)
                tmp_dir = "%s/%s" % (tmp_dir, path_s)
            self.logger.debug("Copying from %s to %s" % (abspath_s, tmp_dir))
            d_copy(path_s, tmp_dir)
        else:
            for src in path_s:
                abssrc = os.path.abspath(src)
                d_copy = shutil.copytree if os.path.isdir(abssrc) else shutil.copy
                if d_copy == shutil.copy:
                    if not os.path.isdir(self.tmp_dir):
                        os.mkdir(self.tmp_dir)
                    tmp_dir = "%s/%s" % (tmp_dir, src)
                self.logger.debug("Copying from %s to %s" % (abssrc, tmp_dir))
                d_copy(abssrc, tmp_dir)

    # Make a zip archive
    def make_zip(self):
        self.logger.info("Making zip file\n")
        src = self.tmp_dir
        if not os.path.isdir(src):
            self.logger.critical("Can't locate directory: %s" % (src))
            sys.exit(1)
        else:
            cdt = datetime.datetime.now()
            u_str = cdt.strftime(self.date_format)
            cdt_str = "%s_%sH_%sm" % (u_str, cdt.hour, cdt.minute)
            f_str = "%s__%s.zip" % ( self.z_name.replace(".zip", ""), cdt_str)
            zf = zipfile.ZipFile(f_str, "w", zipfile.ZIP_DEFLATED)
            try:
                for root, dirs, files in os.walk(src):
                    for file in files:
                        n_root = os.path.basename(os.path.normpath(root))
                        zf.write(os.path.join(root, file), "%s/%s" % (n_root, file))
                zf.close()
                try:
                    shutil.rmtree(src)
                    os.mkdir(src)
                    shutil.move(f_str, "%s\\%s" % (src, f_str))
                except Exception as e:
                    self.logger.critical("Failed to move zip to temp\n")
                    self.logger.debug(e)
                    sys.exit(1)
            except Exception as e:
                self.logger.critical("Failed to create zipfile\n")
                self.logger.debug(e)
                zf.close()
                sys.exit(1)
