class TransitionNotAllowed(Exception):
    """Raised when a transition is not allowed from the current state"""


class InvalidResultState(Exception):
    """Raised when we got invalid result state"""
