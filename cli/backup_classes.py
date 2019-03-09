import os, zipfile, zlib, datetime, shutil, sys, re

class BackupManager(object):
    """docstring for BackupManager."""
    def __init__(self, args, logger, config, defaults):
        super(BackupManager, self).__init__()
        self.u_args = args
        self.logger = logger
        self.config = config
        self.z_name = "backups.zip" if not args.z_name else args.z_name.strip()
        if not self.z_name.endswith(".zip"):
            self.z_name = self.z_name + ".zip"
        path_s = None
        from_conf = False
        try:
            if args.path_s:
                path_s = args.path_s
            else:
                # If this succeeds value comes from config
                path_s = config["BACKUPS"]["path_s"]
                from_conf = True
            # Check if path_s is not an empty string
            if path_s == "" or path_s == " " or not path_s:
                raise KeyError
        except KeyError:
            logger.critical("Missing path values, exiting...")
            sys.exit(1)
        # If value is from config split by new lines else comes from cli split by commas
        if from_conf:
            path_s = path_s.split("\n")
        else:
            path_s = path_s.split(",")
        # Remove any possible whitespaces
        path_s = [v.strip() for v in path_s if v != "" or v != " "]
        self.path_s = path_s
        self.add_date = defaults["add_date"]
        self.date_format = defaults["date_format"]
        self.tmp_dir = os.path.abspath(defaults["temp"])
        logger.info("BackupManager initialized\n")

    # TODO: Run this function only once when path_s are set and replace path_s
    def clean_path(self, p_loc):
        if '"' in p_loc:
            p_loc = p_loc.replace('"', '')
        elif "'" in p_loc:
            p_loc = p_loc.replace("'", "")
        return p_loc

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
                # Remove quotes
                src = self.clean_path(src)
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
            path_s = self.clean_path(path_s)
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
            path_s = self.clean_path(path_s)
            n_tmp_dir = tmp_dir
            abspath_s = os.path.abspath(path_s)
            d_copy = shutil.copytree if os.path.isdir(abspath_s) else shutil.copy
            if d_copy == shutil.copy:
                if not os.path.isdir(self.tmp_dir):
                    try:
                        os.mkdir(self.tmp_dir)
                    except PermissionError:
                        self.logger.critical("Failed to create temporary directory: Permission error\n")
                        sys.exit(1)
                n_tmp_dir = "%s/%s" % (tmp_dir, path_s)
            self.logger.debug("Copying from %s to %s" % (abspath_s, n_tmp_dir))
            try:
                d_copy(path_s, n_tmp_dir)
            except PermissionError:
                self.logger.critical("Failed to copy: Permission error")
                sys.exit(1)
        else:
            for src in path_s:
                src = self.clean_path(src)
                n_tmp_dir = tmp_dir
                abssrc = os.path.abspath(src)
                d_copy = shutil.copytree if os.path.isdir(abssrc) else shutil.copy
                if d_copy == shutil.copy:
                    if not os.path.isdir(self.tmp_dir):
                        try:
                            os.mkdir(self.tmp_dir)
                        except PermissionError:
                            self.logger.critical("Failed to create temporary directory: Permission error\n")
                            sys.exit(1)
                    n_tmp_dir = "%s/%s" % (tmp_dir, src)
                self.logger.debug("Copying from %s to %s" % (abssrc, n_tmp_dir))
                try:
                    d_copy(abssrc, n_tmp_dir)
                except PermissionError:
                    self.logger.critical("Failed to copy: Permission error")
                    sys.exit(1)

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
            relroot = os.path.abspath(os.path.join(src, os.pardir))
            zf = zipfile.ZipFile(f_str, "w", zipfile.ZIP_DEFLATED)
            try:
                for root, dirs, files in os.walk(src):
                    zf.write(root, os.path.relpath(root, relroot))
                    for file in files:
                        filename = os.path.join(root, file)
                        if os.path.isfile(filename): # regular files only
                            arcname = os.path.join(os.path.relpath(root, relroot), file)
                            zf.write(filename, arcname)
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
