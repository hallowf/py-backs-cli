import argparse, sys, logging, configparser, os

from backup_utils import add_args, Defaulter
from backup_classes import BackupManager
from backend_classes import BackendManager



def run_main():
    sys.stdout.write("\n")
    arg_parser = argparse.ArgumentParser(description='Simple backup CLI')
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
    logger = logging.getLogger("Backup Manager")
    logging.basicConfig(format="PYBackups CLI - %(name)s->%(levelname)s : %(message)s",level=d_level)
    # Initialize Defaulter and check for config
    defaulter = None
    config = None
    conf_file = args.cfg if args.cfg else "backups.ini"
    if not os.path.isfile(conf_file):
        logger.error("Can't find file: %s\n" % (conf_file))
        defaulter = Defaulter(args)
        config = defaulter.config
        logger.debug("Using default configuration:\n%s\n" % (config))
    else:
        config = configparser.ConfigParser()
        config.read(conf_file)
        defaulter = Defaulter(args, config)
    defaults = defaulter.return_defaults()
    # Initialize backup manager and copy files
    b_manager = BackupManager(args, logger, config, defaults)
    if not b_manager.check_paths():
        sys.exit(1)
    # b_manager.call_copy()
    # If specified make a zip file
    make_zip = defaulter.set_or_default("make_zip")
    if make_zip == "y":
        print("ZIPOFF")
        # b_manager.make_zip()
    if args.backend == "local":
        logger.info("Finished\n")
        sys.exit(0)
    else:
        backends = ["db","gd","mod",]
        if args.backend not in backends:
            logger.critical("Uknown backend %s" % (args.backend))
            sys.exit(1)
        tmp_dir = b_manager.tmp_dir
        over_creds = defaulter.set_or_default("over_creds")
        dest = defaulter.set_or_default("dest_folder")
        # If backend is onedrive get client_id
        c_id = None
        if args.backend == "mod":
            try:
                c_id = args.client_id or config["BACKUPS"]["client_id"]
                if c_id == "" or c_id == " ":
                    raise KeyError
            except KeyError:
                logger.critical("This backend requires a client id\n")
                sys.exit(1)
        # Release BackupManager Start BackendManager
        b_manager = BackendManager(args.backend, tmp_dir, dest, c_id)
        # b_manager.check_and_auth(over_creds)
        logger.info("Finished\n")



if __name__ == '__main__':
    run_main()
