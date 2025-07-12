from sqlalchemy import (
    Column, Integer, String, Float
)
from .. import db


class TipoTarefa(db.Model):
    __tablename__ = 'tipo_tarefa'
    id         = Column(Integer, primary_key=True)       # id vindo da API Auvo
    descricao  = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"<TipoTarefa(id={self.id}, descricao={self.descricao})>"


class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    id    = Column(Integer, primary_key=True)   # userId da API Auvo
    nome  = Column(String, nullable=False)

    def __repr__(self):
        return f"<Colaborador(id={self.id}, nome={self.nome})>"


class Produto(db.Model):
    __tablename__ = 'produto'
    id               = Column(String, primary_key=True)  # productId (UUID) da API
    nome             = Column(String, nullable=False)
    custo_unitario   = Column(Float, nullable=False)     # unitaryCost
    preco_unitario   = Column(Float, nullable=True)      # se disponível

    def __repr__(self):
        return f"<Produto(id={self.id}, nome={self.nome})>"


class Servico(db.Model):
    __tablename__ = 'servico'
    id               = Column(String, primary_key=True)  # serviceId (UUID) da API
    nome             = Column(String, nullable=False)
    custo_unitario   = Column(Float, nullable=True)      # se a API fornecer custo de serviço

    def __repr__(self):
        return f"<Servico(id={self.id}, nome={self.nome})>"
