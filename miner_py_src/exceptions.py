class MinerPyError(Exception):
    pass


class TryNotFoundException(MinerPyError):
    pass


class FunctionDefNotFoundException(MinerPyError):
    pass