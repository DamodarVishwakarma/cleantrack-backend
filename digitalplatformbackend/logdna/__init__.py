from .logdna import MongoHandler
__all__ = ['MongoHandler']

# Publish this class to the "logging.handlers" module so that it can be use
# from a logging config file via logging.config.fileConfig().
import logging.handlers

logging.handlers.MongoHandler = MongoHandler
