from sqlalchemy import (
    Column, Integer, DateTime, Float, ForeignKey
)
from sqlalchemy.orm import relationship
from .. import db


class FaturamentoTotal(db.Model):
    __tablename__ = 'faturamento_total'
    id               = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id       = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio   = Column(DateTime, nullable=False)
    periodo_fim      = Column(DateTime, nullable=False)
    valor_total      = Column(Float, nullable=False)
    atualizado_em    = Column(DateTime, nullable=False)

    usuario          = relationship("Usuario", backref="faturamentos_totais")

    def __repr__(self):
        return f"<FaturamentoTotal(user={self.usuario_id}, periodo={self.periodo_inicio.date()} a {self.periodo_fim.date()}, valor={self.valor_total})>"


class FaturamentoProduto(db.Model):
    __tablename__ = 'faturamento_produto'
    id                    = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id            = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio        = Column(DateTime, nullable=False)
    periodo_fim           = Column(DateTime, nullable=False)
    valor_produtos        = Column(Float, nullable=False)
    perc_relacao_total    = Column(Float, nullable=False)  # % do faturamento total

    usuario               = relationship("Usuario", backref="faturamentos_produto")

    def __repr__(self):
        return f"<FaturamentoProduto(user={self.usuario_id}, valor={self.valor_produtos}, %={self.perc_relacao_total})>"


class FaturamentoServico(db.Model):
    __tablename__ = 'faturamento_servico'
    id                    = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id            = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    periodo_inicio        = Column(DateTime, nullable=False)
    periodo_fim           = Column(DateTime, nullable=False)
    valor_servicos        = Column(Float, nullable=False)
    perc_relacao_total    = Column(Float, nullable=False)

    usuario               = relationship("Usuario", backref="faturamentos_servico")

    def __repr__(self):
        return f"<FaturamentoServico(user={self.usuario_id}, valor={self.valor_servicos}, %={self.perc_relacao_total})>"
