class PyActorException(Exception):
    pass


class InvalidMessage(PyActorException):
    pass


class ErrorException(PyActorException):
    pass

class SpawnException(PyActorException):
    pass
