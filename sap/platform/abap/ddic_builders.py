"""Helper builders for DDIC ABAP types"""

import abc
from typing import Union
from sap.platform.abap.ddic import RSIMP, RSEXC, RSEXP, RSTBL, RSCHA


class ParameterBuilder(abc.ABC):
    """Base Parameter Builder"""

    def __init__(self, parameter_line):
        self.parts = [part for part in parameter_line.split(' ') if part]
        self.name = None
        self.associated_type = self.parts[2]
        self.default_value = None
        self.optional = False
        self.pass_by_value = False

        self.set_name()

    @abc.abstractmethod
    def set_name(self):
        """Set name of parameter"""

        raise NotImplementedError

    @abc.abstractmethod
    def build(self):
        """Return DDIC parameter"""

        raise NotImplementedError


class ImportChangingBuilder(ParameterBuilder):
    """Import/Changing Parameter Builder Base"""

    param: Union[RSIMP, RSCHA]

    def __init__(self, parameter_line):
        super().__init__(parameter_line)
        self.set_default_value()
        self.set_optional()
        self.set_pass_by_value()

    def set_name(self):
        """Set name of parameter"""

        self.name = self.parts[0][self.parts[0].find('(') + 1:self.parts[0].find(')')]

    def set_default_value(self):
        """Set default value of parameter"""

        if 'DEFAULT' in self.parts:
            self.default_value = self.parts[4].replace("'", "&apos;")

    def set_optional(self):
        """Set if parameter is optional"""

        self.optional = 'OPTIONAL' in self.parts or 'DEFAULT' in self.parts

    def set_pass_by_value(self):
        """Set if parameter is passed by value"""

        self.pass_by_value = self.parts[0].startswith('VALUE')

    def build(self):
        """Return RSIMP or RSCHA parameter"""

        self.param.PARAMETER = self.name
        self.param.DEFAULT = self.default_value
        self.param.OPTIONAL = 'X' if self.optional else None
        self.param.REFERENCE = 'X' if not self.pass_by_value else None
        self.param.TYP = self.associated_type

        return self.param


class ImportBuilder(ImportChangingBuilder):
    """Import Parameter Builder"""

    def __init__(self, line):
        super().__init__(line)
        self.param = RSIMP()


class ChangingBuilder(ImportChangingBuilder):
    """Changing Parameter Builder"""

    def __init__(self, line):
        super().__init__(line)
        self.param = RSCHA()


class ExportBuilder(ParameterBuilder):
    """Export Parameter Builder"""

    def __init__(self, parameter_line):
        super().__init__(parameter_line)
        self.set_pass_by_value()

    def set_name(self):
        """Set name of parameter"""

        self.name = self.parts[0][self.parts[0].find('(') + 1:self.parts[0].find(')')]

    def set_pass_by_value(self):
        """Set if parameter is passed by value"""

        self.pass_by_value = self.parts[0].startswith('VALUE')

    def build(self):
        """Return RSEXP parameter"""

        rsexp = RSEXP()
        rsexp.PARAMETER = self.name
        rsexp.REFERENCE = 'X' if not self.pass_by_value else None
        rsexp.TYP = self.associated_type

        return rsexp


class TableBuilder(ParameterBuilder):
    """Table Parameter Builder"""

    def __init__(self, parameter_line):
        super().__init__(parameter_line)
        self.set_optional()

    def set_name(self):
        """Set name of parameter"""

        self.name = self.parts[0]

    def set_optional(self):
        """Set if parameter is optional"""

        self.optional = 'OPTIONAL' in self.parts or 'DEFAULT' in self.parts

    def build(self):
        """Return RSTBL parameter"""

        rstbl = RSTBL()
        rstbl.PARAMETER = self.name
        rstbl.OPTIONAL = 'X' if self.optional else None
        rstbl.DBSTRUCT = self.associated_type

        return rstbl


class ExceptionBuilder:
    """ABAP Exception Builder"""

    def __init__(self, parameter_line):
        self.name = parameter_line.strip()

    def build(self):
        """Return RSEXC parameter"""

        rsexc = RSEXC()
        rsexc.EXCEPTION = self.name

        return rsexc
