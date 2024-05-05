class MinerTSError(Exception):
    pass


class TryNotFoundException(MinerTSError):
    pass


class CatchClauseExpectedException(MinerTSError):
    pass


class FunctionDefNotFoundException(MinerTSError):
    pass


class TreeSitterNodeException(MinerTSError):
    pass


class CallGraphError(MinerTSError):
    pass
