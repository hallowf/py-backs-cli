import argparse, sys, logging, configparser, os

from backup_utils import add_args
from backup_classes import BackupManager
from backend_classes import BackendManager

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
    logging.basicConfig(format="PYBackups CLI - %(name)s->%(levelname)s : %(message)s",level=d_level)
    logger = logging.getLogger("BackupManager")
    config = configparser.ConfigParser()
    conf_file = args.cfg if args.cfg else "backups.ini"
    if not os.path.isfile(conf_file):
        logger.critical("Can't find file: %s\n" % (conf_file))
        sys.exit(1)
    config.read(conf_file)
    # Initialize backup manager and copy files
    b_manager = BackupManager(args, logger, config)
    b_manager.check_paths()
    b_manager.call_copy()
    # If specified make a zip file
    make_zip = b_manager.set_or_default("make_zip")
    if make_zip:
        b_manager.make_zip()
    if args.backend == "local":
        logger.info("Finished\n")
    else:
        backends = ["db","gd","mod",]
        if args.backend not in backends:
            logger.critical("Uknown backend %s" % (args.backend))
            sys.exit(1)
        tmp_dir = b_manager.tmp_dir
        over_creds = b_manager.set_or_default("over_creds")
        # Release BackupManager Start BackendManager
        b_manager = BackendManager(args.backend, tmp_dir)
        b_manager.check_and_set_creds()



if __name__ == '__main__':
    run_main()
