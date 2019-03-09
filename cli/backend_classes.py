import keyring, logging, getpass, sys, dropbox, os, re, onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from dropbox.files import WriteMode
from dropbox.exceptions import AuthError
from keyring.errors import PasswordSetError

################ EXCEPTIONS -----------------

class AuthenticationError(Exception):
    """Exception to raise when try_auth fails"""
    pass

################ BackendManager -----------------------

class BackendManager(object):
    """docstring for BackendManager."""
    def __init__(self, backend, src, dest, c_id=None):
        super(BackendManager, self).__init__()
        self.backend = backend
        self.u_path = src
        self.dest = dest
        self.logger = logging.getLogger("Backend Manager")
        if "/" in dest:
            self.logger.critical("Path separator for destination is not supported\n")
            sys.exit(1)
        self.api_end = None
        self.client_id = c_id
        self.logger.debug("Reseting loggers from other dependencies")
        self.reset_o_loggers()
        if backend == "gd":
            self.logger.critical("This backend is not implemented yet\n")
            sys.exit(1)
        self.logger.info("Checking upload src\n")
        self.check_src()
        self.logger.info("Setting backend\n")
        self.current_backend = DBBackend(self.u_path, dest) if backend == "db" else (MODBackend(self.u_path, dest, c_id) if backend == "mod" else None)

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

    def check_src(self, n_src=None):
        src = n_src or self.u_path
        d_items = os.listdir(src)
        if len(d_items) == 1:
            n_path = os.path.join(src, d_items[0])
            if os.path.isdir(n_path):
                self.logger.debug("Shifting to: %s" % (os.path.abspath(n_path)))
                self.check_src(n_path)
            elif os.path.isfile(n_path):
                self.logger.debug("Found only one file setting src to it")
                n_path = os.path.abspath(n_path)
                self.u_path = n_path
        else:
            src = os.path.abspath(src)
            self.logger.debug("Found multiple items setting src to: %s" % (src))
            self.u_path = src

    # Check if authentication is successfull
    def run_backend(self):
        self.logger.info()
        try:
            self.current_backend.check_token()
        except (PasswordSetError, AuthenticationError, KeyboardInterrupt) as e:
            e_name = e.__class__.__name__
            if e_name == "PasswordSetError":
                self.logger.info("Error setting password with keyring\n")
            elif e_name == "AuthenticationError":
                self.logger.info("Error trying to authenticate\n")
            elif e_name == "KeyboardInterrupt"
                self.logger.info("User interrupted authentication\n")
            sys.exit(1)



################ Backends -----------------------

class DBBackend(object):
    """docstring for DBBackend."""
    def __init__(self, src, dest):
        super(DBBackend, self).__init__()
        self.u_path = src
        self.dest = dest
        self.api_end = None

    def check_token(self):
            if not keyring.get_password("dropbox", "api") or overwrite == "y":
                sys.stdout.write("Please provide a token\n")
                passwd = getpass.getpass("Token: ")
                try:
                    keyring.set_password("dropbox", "api", "%s" % (passwd))
                except PasswordSetError:
                    raise PasswordSetError
        # Authenticate and release token
        try:
            self.try_auth(keyring.get_password("dropbox", "api"))
        except AuthenticationError:
            raise AuthenticationError


    def try_auth(self, token):
        api_end = dropbox.Dropbox(token)
        try:
            api_end.users_get_current_account()
        except AuthError:
            raise AuthenticationError
        self.api_end = api_end

    def upload_file_s(self):
        u_path = self.u_path if not src else src
        u_path = os.path.abspath(u_path)
        if os.path.isfile(u_path):
            self.logger.info("Src is file: %s" % (u_path))
            f_name = os.path.basename(u_path)
            with open(u_path, "rb") as f:
                db_path = self.dest
                db_path = "/%s" % (db_path)
                f_path = "%s/%s" % (db_path, f_name)
                list_d = [entry.name for entry in self.api_end.files_list_folder('').entries]
                if self.dest not in list_d:
                    self.api_end.files_create_folder(db_path)
                self.api_end.files_upload(f.read(), f_path, mode=WriteMode('overwrite'))
        else:
            print("Not implemented")
            sys.exit(1)
            for root, dirs, files in os.walk(u_path):
                for f in files:
                    l_path = os.path.join(root, f)
                    db_path = "/%s/%s" % (dest.lower(), f)
                    with open(l_path, "rb") as f:
                        self.api_end.files_upload(f.read(), db_path, mode=WriteMode('overwrite'))


class MODBackend(object):
    """docstring for MODBackend."""
    def __init__(self, src, dest, client_id):
        super(MODBackend, self).__init__()
        self.u_path = src
        self.dest = dest
        self.client_id = client_id

    def check_auth(self):
        self.logger.info("Provider is: Microsoft onedrive\n")
        u_token = None
            u_token = keyring.get_password("onedrive", self.client_id)
            if not u_token or overwrite == "y":
                sys.stdout.write("Please provide a secret key\n")
                passwd = getpass.getpass("Secret: ")
                try:
                    keyring.set_password("onedrive", self.client_id, "%s" % (passwd))
                except PasswordSetError:
                    raise PasswordSetError
        try:
            self.try_auth(keyring.get_password("onedrive", self.client_id))
        except (KeyboardInterrupt, AuthenticationError) as e:
            raise e

    def try_auth(self):
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
                code = None
            except (KeyboardInterrupt) as e:
                raise e
            self.api_end = api_end
        except Exception:
            raise AuthenticationError

    def upload_file_s(self):
        def find_in_colls(prev_col=None):
            self.logger.debug("Paging trough collections\n")
            coll = None
            if prev_col:
                coll = onedrivesdk.ChildrenCollectionRequest.get_next_page_request(prev_col, client).get()
            else:
                coll = self.api_end.item(drive='me', id='root').children.request(top=1).get()
            names = [n.name for n in coll]
            end = True if len(coll) != 5 else False
            found = True if dest in names else False
            if end and not found:
                self.logger.debug("Couldn't find destination in collections")
                return False
            elif found:
                return True
            elif end:
                self.logger.debug("Collection has ended")
                return False
            else:
                self.logger.debug("Collection has ended, but there might be more pages retrying")
                return find_in_colls(coll)
        u_path = src or self.u_path
        u_path = os.path.abspath(u_path)
        if os.path.isfile(u_path):
            self.logger.info("Src is file: %s" % (u_path))
            f_name = os.path.basename(u_path)
            if not find_in_colls():
                self.logger.info("Your destination does not exist, creating it now...\n")
                f = onedrivesdk.Folder()
                i = onedrivesdk.Item()
                i.name = dest
                i.folder = f
                try:
                    returned_item = self.api_end.item(drive='me', id='root').children.add(i)
                except Exception as e:
                    self.logger.critical("Error creating folder\n")
                    sys.exit(1)
            with open(u_path, "rb") as f:
                db_path = dest.lower()
                db_path = "/%s" % (db_path)
                f_path = "%s/%s" % (db_path, f_name)
                list_d = [entry.name for entry in self.api_end.files_list_folder('').entries]
                if dest.lower() not in list_d:
                    self.api_end.files_create_folder(db_path)
                self.api_end.files_upload(f.read(), f_path, mode=WriteMode('overwrite'))
        else:
            print("Not implemented")
            sys.exit(1)
