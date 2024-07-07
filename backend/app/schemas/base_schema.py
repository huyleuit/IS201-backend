from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BaseSchema(BaseModel):
    create_date: datetime = Field(None, title="The date the record was created")
    last_modified_date: datetime = Field(None, title="The date the record was last modified",)

    def toDict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}
