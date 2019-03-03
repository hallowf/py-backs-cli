import sys

def add_args(parser):
    # Optional
    parser.add_argument("--path_s", help="Path or paths when providing multiple values EX: 'path1 path2'", action="store")
    parser.add_argument("--backend", help="Where to store: can be local or any of the supported providers", action="store")
    parser.add_argument("--z_name", help="Name for the zip file created", action="store")
    parser.add_argument("--cfg", help="Configuration file default is backups.ini")
    parser.add_argument("--debug", help="Set debug level", action="store")
    parser.add_argument("--add_date", help="Add date to zipfile", action="store")
    parser.add_argument("--date_format", help="Date format to add to zipfile", action="store")
    args = parser.parse_args()
    return args
