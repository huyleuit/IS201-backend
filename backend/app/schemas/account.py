from pydantic import BaseModel, Field
from typing import Optional
from schemas.base_schema import BaseSchema
import bcrypt
import base64
from datetime import datetime


class AccountSchema(BaseSchema):
    username: str = Field(..., description="The username of the account", examples=['alira'])
    role_id: int = Field(..., description="The role_id of the account", examples=['1'])
    password: str = Field(..., description="The password of the account", examples=['123456789'], min_length=8)

    def hashPassword(self, salt: bytes) -> str:
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt)
        base64_password = base64.b64encode(hashed_password)
        return base64_password.decode('utf-8')

    def toDict(self):
        account_dict = {"username": self.username, "role_id": self.role_id}
        salt = bcrypt.gensalt()
        account_dict["password"] = self.hashPassword(salt)
        salt_base64 = base64.b64encode(salt).decode()
        account_dict["salt"] = salt_base64
        return account_dict


class AccountRPSchema(BaseSchema):
    username: str = Field(..., description="The username of the account", examples=['alira'])
    role_id: int = Field(..., description="The role of the account", examples=['admin'])


class AccountTokenRPSchema(BaseSchema):
    username: str = Field(..., description="The username of the account", examples=['alira'])
    token: str = Field(..., description="The token of the account", examples=['MWQ+S348U1B6SHVYeTgzYQ=='])
    expire: datetime = Field(..., description="The date the token will expire", examples=['2021-09-01 00:00:00'])
