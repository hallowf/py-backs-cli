import argparse, sys, logging, configparser, os

from backup_utils import add_args
from backup_classes import BackupManager

def run_main():
    sys.stdout.write("\n")
    arg_parser = argparse.ArgumentParser(description='Manage PCSX2 configs')
    args = add_args(arg_parser)
    di_level = "info" if not args.debug else args.debug
    d_level = None
    try:
        d_level = getattr(logging, di_level.upper())
    except Exception as e:
        sys.stdout.write("Invalid log level " + args.debug + "\n")
        sys.exit(1)
    if not isinstance(d_level, int):
        sys.stdout.write("Invalid log level " + di_level + "\n")
        sys.exit(1)
    logging.basicConfig(format="%(name)s - %(levelname)s : %(message)s",level=d_level)
    logger = logging.getLogger("PYBackups CLI")
    config = configparser.ConfigParser()
    conf_file = args.cfg if args.cfg else "backups.ini"
    if not os.path.isfile(conf_file):
        logger.critical("Can't find file: %s\n" % (conf_file))
        sys.exit(1)
    config.read(conf_file)
    b_manager = BackupManager(args, logger, config)
    b_manager.check_paths()
    n_list = [
        "backups__03-03-2019_17H_5m.zip",
        "backups__03-03-2019_17H_14m.zip",
        "backups__03-03-2019_18H_24m.zip",
        "backups__03-03-2019_23H_14m.zip",
        ]
    # b_manager.call_copy()
    # b_manager.make_zip()
    # b_manager.return_low_date("backups__03-03-2019_17H_5m.zip", "backups__03-03-2019_17H_14m.zip")
    b_manager.find_lowest(n_list)



if __name__ == '__main__':
    run_main()
