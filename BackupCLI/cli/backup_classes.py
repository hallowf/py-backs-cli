import os, zipfile, zlib, datetime, shutil, sys, re, itertools

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
        path_s = args.path_s if args.path_s else config["BACKUPS"]["path_s"]
        path_s = path_s.split(" ") if " " in path_s else path_s.split("\n")
        path_s = [v for v in path_s if v != ""]
        self.path_s = path_s
        add_date = True if args.add_date else config["BACKUPS"]["add_date"]
        self.add_date = True if add_date or add_date == "y" else False
        d_formats = ["&d-&m-&Y", "&d-&Y-&m" "&m-&d-&Y", "&m-&Y-&d", "&Y-&m-&d", "&Y-&d-&m"]
        d_format = args.date_format if args.date_format else str(config["BACKUPS"]["date_format"])
        if d_format not in d_formats:
            logger.critical("Invalid date format %s\n" % (d_format))
            sys.exit(1)
        d_format = d_format.replace("&", "%")
        self.d_format = d_format
        self.logger.info("BackupManager initialized\n")

    def check_paths(self):
        self.logger.info("Checking paths before proceeding\n")
        if not self.path_s:
            self.logger.critical("Couldn't find any paths, have you provided them in the config or by arguments?")
            sys.exit(1)
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
                self.logger.critical("Missing path, cannot resume: Not implemented")
                sys.exit(1)
        else:
            check = os.path.isdir if os.path.isdir(path_s) else os.path.isfile(path_s)
            if not check(path_s):
                self.logger.critical("Cant find path %s\n" % (path_s))
                sys.exit(1)
        self.logger.info("Found path(s) %s\n" % (self.path_s))

    def call_copy(self):
        self.logger.info("Copying files to temporary dir\n")
        path_s = self.path_s
        if os.path.isdir("temp"):
            self.logger.debug("Removing temp dir")
            shutil.rmtree("temp")
        self.logger.debug("Creating temp dir")
        os.mkdir("temp")
        tmp_dir = os.path.abspath("temp")
        self.tmp_dir = tmp_dir
        if not isinstance(path_s, list):
            d_copy = shutil.copytree if os.path.isdir(path_s) else shutil.copy
            self.logger.debug("Copying from %s to %s" % (path_s, tmp_dir))
            d_copy(path_s, tmp_dir)
        else:
            for src in path_s:
                d_copy = shutil.copytree if os.path.isdir(src) else shutil.copy
                self.logger.debug("Copying from %s to %s" % (src, tmp_dir))
                d_copy(src, tmp_dir)

    def return_low_date(self, name1, name2):
        try:
            time1 = re.search("__(.*)\.zip", name1).group(1)
            time1 = datetime.datetime.strptime(time1, self.d_format + str("_%HH_%Mm"))
            time2 = re.search("__(.*)\.zip", name2).group(1)
            time2 = datetime.datetime.strptime(time2, self.d_format + str("_%HH_%Mm"))
            if time1 < time2:
                return name1
            else:
                return name2
        except AttributeError:
            self.logger.critical("Failed to find dates in the provided names\n")
            sys.exit(1)

    def return_lowest(self, list):
        lowest = None
        last = None
        for name in list:
            if not lowest:
                lowest = name
                pass
            elif name != last:
                lowest = self.return_low_date(lowest, name)
                name = last
        return lowest

    def make_zip(self, src="temp"):
        self.logger.info("Making zip file\n")
        if not os.path.isdir(src):
            self.logger.critical("Can't locate directory: %s" % (src))
            sys.exit(1)
        else:
            cdt = datetime.datetime.now()
            u_str = cdt.strftime(self.d_format)
            cdt_str = "%s_%sH_%sm" % (u_str, cdt.hour, cdt.minute)
            f_str = "%s__%s.zip" % (self.z_name.replace(".zip", ""), cdt_str)
            zf = zipfile.ZipFile(f_str, "w", zipfile.ZIP_DEFLATED)
            try:
                for root, dirs, files in os.walk(src):
                    for file in files:
                        zf.write(os.path.join(root, file))
            except Exception as e:
                self.logger.critical("Failed to create zipfile\n")
                self.logger.debug(e)
                zf.close()
                sys.exit(1)
