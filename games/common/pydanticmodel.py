from enum import Enum
from typing import (AbstractSet, Any, Callable, Dict, Iterable, List, Mapping,
                    Optional, Set, Tuple, Union)

import pandas as pd
from pydantic import BaseModel, Extra

IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
DictIntStrAny = Dict[IntStr, Any]
DictStrAny = Dict[str, Any]
MappingIntStrAny = Mapping[IntStr, Any]


class PydanticModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow
        json_encoders = {Enum: lambda v: v.value, pd.DataFrame: lambda df: df.to_dict("records")}

    def tuple(self: BaseModel) -> Tuple[Any]:
        """Return a tuple of the pydantic model's attribute values."""
        return tuple(self.dict().values())

    @classmethod
    def from_args(cls, *args, **kwargs) -> "PydanticModel":
        arg_fields = [field_name for field_name in cls.__fields__ if field_name not in kwargs]
        kwargs.update(dict(zip(arg_fields, args)))
        return cls(**kwargs)

    def __repr_args__(self) -> Any:
        return self.dict().items()

    def _format_include_or_exclude(self, arg: Any) -> Set:
        if arg is None:
            return arg
        elif isinstance(arg, Mapping):
            return arg
        elif isinstance(arg, Iterable):
            return set(arg)
        else:
            return {arg}

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":

        return super().dict(
            include=self._format_include_or_exclude(include) or set([c for c in self.__fields__]),
            exclude=self._format_include_or_exclude(exclude),
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Callable[[Any], Any] = None,
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(
            include=self._format_include_or_exclude(include) or set([c for c in self.__fields__]),
            exclude=self._format_include_or_exclude(exclude),
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )
