from compliance_checker.base import BaseCheck


class CallableCheckBase(object):

    # Define empty values for required arguments
    short_name = ""
    primary_arg_type = None
    defaults = {}
    message_templates = []
    level = "HIGH"

    def __init__(self, kwargs, messages=None, level="HIGH", vocabulary_ref=None):
        self.kwargs = self.defaults.copy()
        self.kwargs.update(kwargs)
        self._define_messages(messages)
        self.out_of = len(self.messages)
        self.level = getattr(BaseCheck, level)
        self.vocabulary_ref = vocabulary_ref

        self._setup()

    def _setup(self):
        "Child classes can override this to perform validation or modification of arguments."
        pass

    def _define_messages(self, messages=None):
        if messages:
            self.messages = messages
        else:
            self.messages = [tmpl.format(**self.kwargs) for tmpl in self.message_templates]

    def get_description(self):
        """
        Generates description of check based on doc string and kwargs.

        :return: description of check with kwargs inserted (if necessary) [string].
        """
        return self.__doc__.format(**self.kwargs)

    def get_short_name(self):
        return self.short_name.format(**self.kwargs)

    def get_message_templates(self):
        return self.message_templates

    def get_messages(self):
        # Note: messages are only provided for error/failure cases
        #       and SUCCESS is silent.
        return self.messages

    def __call__(self, primary_arg):
        """
        Calls the check with primary arg and keyword args provided during instantiation.

        :param primary_arg: main argument (object to check)
        :return: Result object (from compliance checker)
        """
        self._check_primary_arg(primary_arg)
        return self._get_result(primary_arg)

    def _get_result(self, primary_arg):
        raise NotImplementedError

    def _check_primary_arg(self, primary_arg):
        raise NotImplementedError
