from sqlalchemy import (
    Column, Integer, DateTime, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from .. import db


class LucroTotal(db.Model):
    __tablename__ = 'lucro_total'
    id                 = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id         = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio     = Column(DateTime, nullable=False)
    periodo_fim        = Column(DateTime, nullable=False)
    lucro_total        = Column(Float, nullable=False)
    margem_lucro       = Column(Float, nullable=False)  # % de lucro sobre faturamento_total

    usuario            = relationship("Usuario", backref="lucros_totais")

    def __repr__(self):
        return f"<LucroTotal(user={self.usuario_id}, lucro={self.lucro_total}, margem={self.margem_lucro})>"


class LucroProduto(db.Model):
    __tablename__ = 'lucro_produto'
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id              = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio          = Column(DateTime, nullable=False)
    periodo_fim             = Column(DateTime, nullable=False)
    lucro_produtos          = Column(Float, nullable=False)
    perc_relacao_lucro      = Column(Float, nullable=False)  # % do lucro total

    usuario                 = relationship("Usuario", backref="lucros_produto")

    def __repr__(self):
        return f"<LucroProduto(user={self.usuario_id}, lucro={self.lucro_produtos}, %={self.perc_relacao_lucro})>"


class LucroServico(db.Model):
    __tablename__ = 'lucro_servico'
    id                      = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id              = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio          = Column(DateTime, nullable=False)
    periodo_fim             = Column(DateTime, nullable=False)
    lucro_servicos          = Column(Float, nullable=False)
    perc_relacao_lucro      = Column(Float, nullable=False)

    usuario                 = relationship("Usuario", backref="lucros_servico")

    def __repr__(self):
        return f"<LucroServico(user={self.usuario_id}, lucro={self.lucro_servicos}, %={self.perc_relacao_lucro})>"
