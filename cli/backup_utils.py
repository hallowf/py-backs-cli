import sys

def add_args(parser):
    # required
    parser.add_argument("backend", help="Where to store: can be local or any of the supported providers", action="store")
    # Optional
    parser.add_argument("--path_s", help="Path or paths when providing multiple values EX: 'path1 path2'", action="store")
    parser.add_argument("--z_name", help="Name for the zip file created", action="store")
    parser.add_argument("--cfg", help="Configuration file default is backups.ini")
    parser.add_argument("--make_zip", help="Creates a zip file with the items specified", action="store")
    parser.add_argument("--temp", help="location to store temporary files", action="store")
    parser.add_argument("--debug", help="Set debug level", action="store")
    parser.add_argument("--add_date", help="Add date to zipfile", action="store")
    parser.add_argument("--date_format", help="Date format to add to zipfile", action="store")
    parser.add_argument("--over_creds", help="Overwrite credentials for cloud providers", action="store")
    parser.add_argument("--client_id", help="Client id for providers, only some require it", action="store")
    parser.add_argument("--dest_folder", help="Destination folder for cloud provider", action="store")
    args = parser.parse_args()
    return args

class Defaulter(object):
    """------------------------------------
        Requires user args and config,
        uses default config if config is none
    ----------------------------------------"""
    def __init__(self, args, config = None):
        super(Defaulter, self).__init__()
        self.d_config = {
            "BACKUPS": {
                "backend": "local",
                "make_zip": "y",
                "add_date": "y",
                "over_creds": "n",
                "date_format": "&d-&m-&Y",
                "temp": "temp",
                "client_id": "",
                "dest_folder": "PYBCLI",
                "path_s": ""
            }
        }
        self.u_args = args
        self.config = config or self.d_config

    # Use the defaulter to check and set some values
    # This is to avoid importing and instantiating a defaulter at backup_classes
    def return_defaults(self):
        defaults = {}
        defaults["add_date"] = self.set_or_default("add_date")
        d_format = self.set_or_default("date_format")
        d_format = d_format.replace("&", "%")
        defaults["date_format"] = d_format
        defaults["temp"] = self.set_or_default("temp")
        return defaults

    def set_or_default(self, name):
        # Raise KeyError on empty value
        def raise_on_empty_val(val):
            if val == "" or val == " " or not val:
                raise KeyError
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
            if name == "add_date":
                val = self.u_args.add_date or self.config["BACKUPS"]["add_date"]
                val = True if val == "y" else False
            elif name == "date_format":
                d_formats = ["&d-&m-&Y", "&d-&Y-&m" "&m-&d-&Y", "&m-&Y-&d", "&Y-&m-&d", "&Y-&d-&m"]
                val = self.u_args.date_format or self.config["BACKUPS"]["date_format"]
                if val not in d_formats:
                    self.logger.debug("Invalid date format %s\n" % (val))
                    raise KeyError
            else:
                val = getattr(self.u_args, name) or self.config["BACKUPS"][name]
            # Raise if value  is empty
            raise_on_empty_val(val)
        except KeyError:
            self.logger.debug("Missing parameter from config and arguments: %s\nSetting to default: %s" % (name, vals[name]))
            return vals[name]
        return val
