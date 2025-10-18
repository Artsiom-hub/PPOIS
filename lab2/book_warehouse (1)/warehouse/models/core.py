from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid, time
from ..exceptions import ValidationError

@dataclass
class IDGenerator:
    prefix: str = "ID"
    counter: int = 0

    def next(self) -> str:
        self.counter += 1
        return f"{self.prefix}-{self.counter}-{uuid.uuid4().hex[:6]}"

    def peek(self) -> str:
        return f"{self.prefix}-{self.counter+1}-XXXXXX"

@dataclass
class Clock:
    epoch_ms: int = field(default_factory=lambda: int(time.time()*1000))
    timezone: str = "UTC"
    drift_ms: int = 0

    def now_ms(self) -> int:
        return int(time.time()*1000) + self.drift_ms

    def with_drift(self, delta_ms:int) -> 'Clock':
        return Clock(epoch_ms=self.epoch_ms, timezone=self.timezone, drift_ms=self.drift_ms+delta_ms)

@dataclass
class Config:
    name: str
    version: str
    settings: Dict[str, str] = field(default_factory=dict)

    def get(self, key:str, default=None):
        return self.settings.get(key, default)

    def set(self, key:str, value:str) -> None:
        self.settings[key] = value

@dataclass
class Logger:
    name: str
    level: str = "INFO"
    records: List[str] = field(default_factory=list)

    def info(self, msg:str): self.records.append(f"INFO:{msg}")
    def warn(self, msg:str): self.records.append(f"WARN:{msg}")
    def error(self, msg:str): self.records.append(f"ERROR:{msg}")

@dataclass
class Address:
    line1: str
    city: str
    country: str
    postal_code: str
    line2: Optional[str] = None

    def short(self) -> str:
        return f"{self.line1}, {self.city} {self.postal_code}, {self.country}"

    def is_domestic(self, country:str) -> bool:
        return self.country.lower() == country.lower()

@dataclass
class Tag:
    name: str
    weight: float = 1.0

    def normalized(self) -> str:
        return self.name.strip().lower()

@dataclass
class KPI:
    name: str
    value: float = 0.0
    target: float = 1.0

    def achieved(self) -> bool:
        return self.value >= self.target

    def progress(self) -> float:
        return 0.0 if self.target == 0 else min(1.0, self.value / self.target)

@dataclass
class Credentials:
    username: str
    password_hash: str
    salt: str

    def check(self, hasher:'PasswordHasher', candidate:str) -> bool:
        return hasher.verify(candidate, self.salt, self.password_hash)

@dataclass
class PasswordHasher:
    rounds: int = 10
    algorithm: str = "fake-sha"

    def hash(self, password:str, salt:str) -> str:
        # toy hasher for demo
        data = (password + salt + self.algorithm) * self.rounds
        return hex(abs(hash(data)))[2:]

    def verify(self, candidate:str, salt:str, stored:str) -> bool:
        return self.hash(candidate, salt) == stored

@dataclass
class User:
    id: str
    name: str
    role: str
    creds: Credentials

    def can(self, action:str) -> bool:
        if self.role == "admin": return True
        return action in {"read", "buy"}

    def rename(self, new_name:str):
        if not new_name: raise ValidationError("empty name")
        self.name = new_name
