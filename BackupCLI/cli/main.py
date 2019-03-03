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
    b_manager.call_copy()
    if args.make_zip:
        b_manager.make_zip()
    if args.backend == "local":
        logger.info("Finished\n")
    else:
        backends = ["db","gd","mod",]
        if args.backend not in backends:
            logger.critical("Uknown backend %s" % (args.backend))
        tmp_dir = b_manager.tmp_dir
        print(tmp_dir)
        b_manager = None
        print(tmp_dir)



if __name__ == '__main__':
    run_main()
