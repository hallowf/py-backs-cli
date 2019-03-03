import keyring, logging, getpass, sys, dropbox, os

from dropbox.files import WriteMode

class BackendManager(object):
    """docstring for BackendManager."""
    def __init__(self, backend, path):
        super(BackendManager, self).__init__()
        self.backend = backend
        self.u_path = path
        self.logger = logging.getLogger("Backend Manager")
        self.api_end = None
        self.mute_o_loggers()

    def mute_o_loggers(self):
        self.logger.debug("Muting other loggers")
        logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)


    def check_and_auth(self, overwrite="n"):
        self.logger.info("Checking and setting credentials\n")
        def db_creds():
            self.logger.info("Provider is: dropbox\n")
            try:
                u_token = keyring.get_password("system", "dropbox")
                if not u_token or overwrite == "y":
                    sys.stdout.write("Please provide a token\n")
                    passwd = getpass.getpass("Token: ")
                    keyring.set_password("system", "dropbox", "%s" % (passwd))
                u_token = keyring.get_password("system", "dropbox")
            except Exception:
                self.logger.critical("Something went wrong while trying to access token in keyring\n")
                sys.exit(1)
            try:
                self.do_auth(u_token)
            except Exception:
                self.logger.critical("Error while trying to authenticate, probably bad credentials\n")
                sys.exit(1)

        def gd_creds():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        def mod_creds():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        funcs = {
        "db": db_creds,
        "gd": gd_creds,
        "mod": mod_creds,
        }

        funcs[self.backend]()

    def do_auth(self, token, user=None):
        self.logger.info("Authenticating\n")
        def db_auth():
            self.api_end = dropbox.Dropbox(token)
            try:
                self.api_end.users_get_current_account()
            except AuthError:
                self.logger.critical("Authentication error for dropbox probably an invalid token\n")
                sys.exit(1)

        def gd_auth():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        def mod_auth():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        funcs = {
        "db": db_auth,
        "gd": gd_auth,
        "mod": mod_auth,
        }

        funcs[self.backend]()

    def upload_file_s(self, dest,  src=None):
        def to_dropbox():
            u_path = self.u_path if not src else src
            u_path = os.path.abspath(u_path)
            if os.path.isfile(u_path):
                self.logger.info("Src is file: %s" % (u_path))
                f_name = os.path.basename(u_path)
                with open(u_path, "rb") as f:
                    db_path = dest.lower()
                    db_path = "/%s" % (db_path)
                    f_path = "%s/%s" % (db_path, f_name)
                    list_d = [entry.name for entry in self.api_end.files_list_folder('').entries]
                    if dest.lower() not in list_d:
                        self.api_end.files_create_folder(db_path)
                    self.api_end.files_upload(f.read(), f_path, mode=WriteMode('overwrite'))
            else:
                for root, dirs, files in os.walk(u_path):
                    for f in files:
                        l_path = os.path.join(root, f)
                        db_path = "/%s/%s" % (dest.lower(), f)
                        with open(l_path, "rb") as f:
                            self.api_end.files_upload(f.read(), db_path, mode=WriteMode('overwrite'))


        def to_google():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        def to_onedrive():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        funcs = {
        "db": to_dropbox,
        "gd": to_google,
        "mod": to_onedrive,
        }

        funcs[self.backend]()
