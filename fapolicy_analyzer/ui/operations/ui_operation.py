from abc import ABC, abstractmethod


class UIOperation(ABC):
    """
    An abstract base class implemented by any class providing an operation that can be
    initiated by the user on the system. (i.e. Deploying Changsets)
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.dispose()

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def get_icon(self) -> str:
        pass

    @abstractmethod
    def run(self):
        pass

    def dispose(self):
        pass
