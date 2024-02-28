"""Define the base Reflex class."""
from __future__ import annotations

import os
from typing import Any, List, Type, Dict, Optional

import pydantic
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from reflex import constants


# TODO: migrate to pydantic v2
def validate_field_name(bases: List[Type["BaseModel"]], field_name: str) -> None:
    """Ensure that the field's name does not shadow an existing attribute of the model.

    Args:
        bases: List of base models to check for shadowed attrs.
        field_name: name of attribute

    Raises:
        NameError: If state var field shadows another in its parent state
    """
    reload = os.getenv(constants.RELOAD_CONFIG) == "True"
    for base in bases:
        try:
            if not reload and getattr(base, field_name, None):
                pass
        except TypeError as te:
            raise NameError(
                f'State var "{field_name}" in {base} has been shadowed by a substate var; '
                f'use a different field name instead".'
            ) from te


# monkeypatch pydantic validate_field_name method to skip validating
# shadowed state vars when reloading app via utils.prerequisites.get_app(reload=True)
# TODO
#  pydantic.main.validate_field_name = validate_field_name  # type: ignore


class Base(pydantic.BaseModel):
    """The base class subclassed by all Reflex classes.

    This class wraps Pydantic and provides common methods such as
    serialization and setting fields.

    Any data structure that needs to be transferred between the
    frontend and backend should subclass this class.
    """

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True
        use_enum_values = True
        extra = "allow"

    def json(self) -> str:
        """Convert the object to a json string.

        Returns:
            The object as a json string.
        """
        #  from reflex.utils.serializers import serialize

        return self.model_dump_json()
        #  return self.__config__.json_dumps(self.dict(), default=serialize)

    def set(self, **kwargs):
        """Set multiple fields and return the object.

        Args:
            **kwargs: The fields and values to set.

        Returns:
            The object with the fields set.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    @classmethod
    def get_fields(cls) -> dict[str, Any]:
        """Get the fields of the object.

        Returns:
            The fields of the object.
        """
        return cls.model_fields


    @classmethod
    def add_field(cls, var: Any, default_value: Any):
        """Add a pydantic field after class definition.

        Used by State.add_var() to correctly handle the new variable.

        Args:
            var: The variable to add a pydantic field for.
            default_value: The default value of the field
        """
        field_info = FieldInfo(default=default_value, annotation=var._var_type)
        cls.model_fields.update({var._var_name: field_info})
        cls.model_rebuild(force=True)


    def get_value(self, key: str) -> Any:
        """Get the value of a field.

        Args:
            key: The key of the field.

        Returns:
            The value of the field.
        """
        if isinstance(key, str) and key in self.get_fields():
            # Seems like this function signature was wrong all along?
            # If the user wants a field that we know of, get it and pass it off to _get_value
            key = getattr(self, key)
        return self._get_value(
            key,
            to_dict=True,
            by_alias=False,
            include=None,
            exclude=None,
            exclude_unset=False,
            exclude_defaults=False,
            exclude_none=False,
        )
