from checklib.register.callable_check_base import CallableCheckBase
from checklib.register.file_checks_register import FileCheckBase
from checklib.register.nc_file_checks_register import NCFileCheckBase


def get_check_class(id):
    """
    Find check class matching `id` in the various registers.

    :param id: identifier for check (matches class name) [string]
    :return: class
    """
    for parent in (FileCheckBase, NCFileCheckBase):
        for cls in parent.__subclasses__():
            if cls.__name__ == id:
                return cls

    raise Exception("Cannot identify Check with identifier: {}".format(id))


