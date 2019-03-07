import argparse, sys, logging, configparser, os

from backup_utils import add_args, return_def_conf
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
    logging.basicConfig(format="PYBackups CLI - %(name)s->%(levelname)s : %(message)s",level=d_level)
    logger = logging.getLogger("Backup Manager")
    config = None
    conf_file = args.cfg if args.cfg else "backups.ini"
    if not os.path.isfile(conf_file):
        logger.error("Can't find file: %s\n" % (conf_file))
        config = return_def_conf()
        logger.debug("Using default configuration:\n%s\n" % (config))
    else:
        config = configparser.ConfigParser()
        config.read(conf_file)
    # Initialize backup manager and copy files
    b_manager = BackupManager(args, logger, config)
    if not b_manager.check_paths():
        sys.exit(1)
    b_manager.call_copy()
    # If specified make a zip file
    make_zip = b_manager.set_or_default("make_zip")
    if make_zip == "y":
        b_manager.make_zip()
    if args.backend == "local":
        logger.info("Finished\n")
        sys.exit(0)
    else:
        backends = ["db","gd","mod",]
        if args.backend not in backends:
            logger.critical("Uknown backend %s" % (args.backend))
            sys.exit(1)
        tmp_dir = b_manager.tmp_dir
        over_creds = b_manager.set_or_default("over_creds")
        dest = b_manager.set_or_default("dest_folder")
        # If backend is onedrive get client_id
        c_id = None
        if args.backend == "mod":
            try:
                c_id = args.client_id if args.client_id else config["BACKUPS"]["client_id"]
                if c_id == "" or c_id == " ":
                    raise KeyError
            except KeyError:
                logger.critical("This backend requires a client id\n")
                sys.exit(1)
        # Release BackupManager Start BackendManager
        b_manager = BackendManager(args.backend, tmp_dir, c_id)
        b_manager.check_and_auth(over_creds)
        # # TODO: Maybe put this inside BackendManager
        src = tmp_dir
        d_items = os.listdir(tmp_dir)
        if len(d_items) == 1:
            n_path = os.path.join(tmp_dir, d_items[0])
            if os.path.isdir(n_path):
                logger.info("Shifting src down since only one folder is present\n")
                src = n_path
            elif os.path.isfile(n_path):
                logger.info("Found only one file setting src to it\n")
                src = n_path
        # b_manager.upload_file_s(dest, src)
        logger.info("Finished\n")



if __name__ == '__main__':
    run_main()
