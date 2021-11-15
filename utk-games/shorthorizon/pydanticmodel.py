from typing import Any, Tuple

from pydantic import BaseModel


class PydanticModel(BaseModel):
    def tuple(self: BaseModel) -> Tuple[Any]:
        """Return a tuple of the pydantic model's attribute values."""
        return tuple(self.dict().values())

    @classmethod
    def from_args(cls, *args, **kwargs) -> "PydanticModel":
        arg_fields = [field_name for field_name in cls.__fields__ if field_name not in kwargs]
        kwargs.update(dict(zip(arg_fields, args)))
        return cls(**kwargs)
