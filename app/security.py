import abc
import typing
import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)


class AbstractAuthHandler(abc.ABC):

    @abc.abstractmethod
    def hash_password(self, password: str) -> str:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def create_access_token(self, header: typing.Dict, payload: typing.Dict) -> str:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def decode_access_token(self, token: str) -> typing.Dict:
        raise NotImplementedError()

class AuthHandler(AbstractAuthHandler):

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._password_hash = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self._password_hash.verify(password, hashed_password)

    def create_access_token(
        self,
        header: typing.Dict,
        payload: typing.Dict,
    ) -> str:
        return jwt.encode(
            payload=payload,
            key=self._secret_key,
            algorithm=self._algorithm,
            headers=header,
        )

    def decode_access_token(self, token: str) -> typing.Dict:
        return jwt.decode(
            jwt=token,
            key=self._secret_key,
            algorithms=[self._algorithm],
        )