#import declarative_base from sqlalchemy.ext.declarative to create a base class for our models

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# The declarative_base() function returns a new base class from which all mapped classes should inherit. 
