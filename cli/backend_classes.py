import keyring, logging, getpass, sys, dropbox, os, re, onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from dropbox.files import WriteMode

class BackendManager(object):
    """docstring for BackendManager."""
    def __init__(self, backend, path, c_id=None):
        super(BackendManager, self).__init__()
        self.backend = backend
        self.u_path = path
        self.logger = logging.getLogger("Backend Manager")
        self.api_end = None
        self.client_id = c_id
        self.reset_o_loggers()

    # Reset other loggers
    def reset_o_loggers(self):
        self.logger.debug("Muting other loggers")
        logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
        logging.getLogger("asyncio").setLevel(logging.INFO)

    # Return lowest date between 2 values from file names
    def return_low_date(self, name1, name2):
        try:
            time1 = re.search("__(.*)\.zip", name1).group(1)
            time1 = datetime.datetime.strptime(time1, self.date_format + str("_%HH_%Mm"))
            time2 = re.search("__(.*)\.zip", name2).group(1)
            time2 = datetime.datetime.strptime(time2, self.date_format + str("_%HH_%Mm"))
            if time1 < time2:
                return name1
            else:
                return name2
        except AttributeError:
            self.logger.critical("Failed to find dates in the provided names\n")
            sys.exit(1)

    # Return lowest date
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

    # Check if authentication is successfull
    def check_and_auth(self, overwrite="n"):
        self.logger.info("Checking and setting credentials\n")
        def db_creds():
            self.logger.info("Provider is: dropbox\n")
            try:
                u_token = keyring.get_password("dropbox", "api")
                if not u_token or overwrite == "y":
                    sys.stdout.write("Please provide a token\n")
                    passwd = getpass.getpass("Token: ")
                    keyring.set_password("dropbox", "api", "%s" % (passwd))
                u_token = keyring.get_password("dropbox", "api")
            except Exception:
                self.logger.critical("Something went wrong while trying to access token in keyring\n")
                sys.exit(1)
            # Authenticate and release token
            self.do_auth(u_token)
            u_token = None

        def gd_creds():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        def mod_creds():
            self.logger.info("Provider is: Microsoft onedrive\n")
            u_token = None
            try:
                u_token = keyring.get_password("onedrive", self.client_id)
                if not u_token or overwrite == "y":
                    sys.stdout.write("Please provide a secret key\n")
                    passwd = getpass.getpass("Secret: ")
                    keyring.set_password("onedrive", self.client_id, "%s" % (passwd))
                u_token = keyring.get_password("onedrive", self.client_id)
            except Exception:
                self.logger.critical("Something went wrong while trying to access token in keyring\n")
                sys.exit(1)
            self.do_auth(u_token)
            u_token = None

        funcs = {
        "db": db_creds,
        "gd": gd_creds,
        "mod": mod_creds,
        }

        funcs[self.backend]()

    # Token is secret
    def do_auth(self, token, user=None):
        self.logger.info("Authenticating\n")

        def db_auth():
            api_end = dropbox.Dropbox(token)
            try:
                api_end.users_get_current_account()
            except AuthError:
                self.logger.critical("Authentication error for dropbox probably an invalid token\n")
                sys.exit(1)
            self.api_end = api_end

        def gd_auth():
            self.logger.critical("not implemented\n")
            sys.exit(1)

        def mod_auth():
            redirect_uri = 'http://localhost:8080/'
            scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
            try:
                api_end = onedrivesdk.get_default_client(client_id=self.client_id, scopes=scopes)
                auth_url = api_end.auth_provider.get_auth_url(redirect_uri)
                #this will block until we have the code
                # TODO: Check if this code can be stored and reused
                # TODO: Will also need a timeout in case the user closes the webpage
                try:
                    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)
                    api_end.auth_provider.authenticate(code, redirect_uri, token)
                except KeyboardInterrupt:
                    self.logger.critical("User interrupted login\n")
                    sys.exit(1)

                self.api_end = api_end
                code = None
            except Exception:
                self.logger.critical("Authentication error for onedrive, please check id and secret\n")
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
            u_path = self.u_path if not src else src
            u_path = os.path.abspath(u_path)
            if os.path.isfile(u_path):
                self.logger.info("Src is file: %s" % (u_path))
                f_name = os.path.basename(u_path)
                collection = client.item(drive='me', id='root').children.request(top=3).get()
                exit(0)
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

        funcs = {
        "db": to_dropbox,
        "gd": to_google,
        "mod": to_onedrive,
        }

        funcs[self.backend]()
