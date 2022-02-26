# core mod
import logging

def debug(msg, type = 'default'):
  logger = logging.getLogger(type)
  logger.debug(msg)

def error(msg, type = 'default'):
  logger = logging.getLogger(type)
  logger.error(msg)

def info(msg, type = 'default'):
  logger = logging.getLogger(type)
  logger.info(msg)

def onlyConsole(type = 'default', format = '%(levelname)s - %(message)s', loglevel = logging.INFO):
  print ('onlyConsole')
  ConsoleOut = logging.StreamHandler()
  ConsoleOut.setFormatter(logging.Formatter(format))

  logger = logging.getLogger(type)
  logger.setLevel(loglevel)
  logger.addHandler(ConsoleOut)
  return logger

