class NullTokenError(Exception):
    """ The token must be non-null """

class NoneDBScope(Exception):
    """ There is no db scope in the application """