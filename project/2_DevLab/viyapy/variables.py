

class BaseVariable:

    default_length = None

    def __init__(self, name, length=None, level=None, description=None):
        """
        Create variable object

        :param name: Name of the variable
        :param length: Length of the variable
        :param description: Description of the variable
        :param level: One of Binary, Nominal, Ordinal, Interval
        """
        self.name = name
        self.length = length or self.default_length
        self.level = level
        self.description = description

    def to_viya(self, role):
        """
        Create variable data structure for Viya API

        :param role: input or output
        :return: dictionary representing variable
        """
        var = {
            "role": role,
            "name": self.name,
            "type": self.__class__.__name__
        }

        if self.length:
            var.update({"length": self.length})
        if self.level:
            var.update({"level": self.level})
        if self.description:
            var.update({"description": self.description})

        return var


class String(BaseVariable):

    pass


class Decimal(BaseVariable):

    pass


class Integer(BaseVariable):

    pass


class Boolean(BaseVariable):

    pass


class DateTime(BaseVariable):

    pass


class Date(BaseVariable):

    pass
