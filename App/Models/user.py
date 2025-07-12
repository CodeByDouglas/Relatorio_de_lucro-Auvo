from sqlalchemy import (
    Column, Integer, String, DateTime
)
from sqlalchemy.orm import relationship
from .. import db


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id                = Column(Integer, primary_key=True, autoincrement=True)
    chave_app         = Column(String, unique=True, nullable=False)
    token_api         = Column(String, nullable=False)
    token_bearer      = Column(String, nullable=False)
    token_obtido_em   = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Usuario(id={self.id}, chave_app={self.chave_app})>"
