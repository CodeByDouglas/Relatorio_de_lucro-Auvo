from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from .. import db


class TipoTarefa(db.Model):
    __tablename__ = 'tipo_tarefa'
    id         = Column(Integer, primary_key=True)       # id vindo da API Auvo
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    descricao  = Column(String, nullable=False)
    
    usuario    = relationship("Usuario", backref="tipos_tarefa")

    def __repr__(self):
        return f"<TipoTarefa(id={self.id}, usuario_id={self.usuario_id}, descricao={self.descricao})>"


class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    id         = Column(Integer, primary_key=True)   # userId da API Auvo
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    nome       = Column(String, nullable=False)
    
    usuario    = relationship("Usuario", backref="colaboradores")

    def __repr__(self):
        return f"<Colaborador(id={self.id}, usuario_id={self.usuario_id}, nome={self.nome})>"


class Produto(db.Model):
    __tablename__ = 'produto'
    id               = Column(String, primary_key=True)  # productId (UUID) da API
    usuario_id       = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    nome             = Column(String, nullable=False)
    custo_unitario   = Column(Float, nullable=False)     # unitaryCost
    preco_unitario   = Column(Float, nullable=True)      # se disponível
    
    usuario          = relationship("Usuario", backref="produtos")

    def __repr__(self):
        return f"<Produto(id={self.id}, usuario_id={self.usuario_id}, nome={self.nome})>"


class Servico(db.Model):
    __tablename__ = 'servico'
    id               = Column(String, primary_key=True)  # serviceId (UUID) da API
    usuario_id       = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    nome             = Column(String, nullable=False)
    custo_unitario   = Column(Float, nullable=True)      # se a API fornecer custo de serviço
    
    usuario          = relationship("Usuario", backref="servicos")

    def __repr__(self):
        return f"<Servico(id={self.id}, usuario_id={self.usuario_id}, nome={self.nome})>"
