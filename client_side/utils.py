import logging

# logger
def getMyLogger(log_file='log.txt', mode='a'):
    logging.basicConfig(level=logging.INFO, 
        format="%(asctime)s %(name)s %(levelname)s %(message)s", 
        datefmt='%Y-%m-%d %H:%M:%S %a')
    logger = logging.getLogger()
    fh = logging.FileHandler(log_file, mode)
    logger.addHandler(fh)
    return logger
