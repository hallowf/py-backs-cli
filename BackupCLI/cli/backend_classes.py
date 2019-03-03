import keyring, logging, getpass, sys

class BackendManager(object):
    """docstring for BackendManager."""
    def __init__(self, backend, path):
        super(BackendManager, self).__init__()
        self.backend = backend
        self.path = path
        self.logger = logging.getLogger("BackendManager")


    def check_and_set_creds(self, overwrite="n"):
        self.logger.info("Checking and setting credentials\n")
        def db_creds():
            try:
                u_token = keyring.get_password("system", "dropbox")
                print(u_token)
                if not u_token or overwrite == "y":
                    sys.stdout.write("No token in credential manager for dropbox please provide one\n")
                    passwd = getpass.getpass("Token: ")
                    keyring.set_password("system", "dropbox", "%s" % (passwd))
            except Exception as e:
                print(e)

        def gd_creds():
            print("not implemented")

        def mod_creds():
            print("not implemented")

        funcs = {
        "db": db_creds,
        "gd": gd_creds,
        "mod": mod_creds,
        }

        funcs[self.backend]()

    def check_auth(self):



    def to_dropbox(self):
        print("dropbox")

    def to_google(self):
        print("google drive")

    def to_onedrive(self):
        print("microsoft onedrive")
