from sqlalchemy import (
    Column, Integer, String, DateTime, Float, ForeignKey
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from .. import db


class Tarefa(db.Model):
    __tablename__ = 'tarefa'
    id                 = Column(Integer, primary_key=True)           # taskId da API
    data               = Column(DateTime, nullable=False)            # taskDate ou finishedDate
    cliente            = Column(String, nullable=True)               # customerDescription
    tipo_tarefa_id     = Column(Integer, ForeignKey('tipo_tarefa.id'), nullable=False)
    colaborador_id     = Column(Integer, ForeignKey('colaborador.id'), nullable=False)
    valor_total        = Column(Float, nullable=False)               # soma de produtos + serviços
    custo_total        = Column(Float, nullable=False)               # calculado a partir dos custos unitários
    lucro_bruto        = Column(Float, nullable=False)               # valor_total - custo_total
    detalhes_json      = Column(JSON, nullable=False)                # JSON com detalhes completos da tarefa

    tipo_tarefa        = relationship("TipoTarefa", backref="tarefas")
    colaborador        = relationship("Colaborador", backref="tarefas")

    def __repr__(self):
        return f"<Tarefa(id={self.id}, data={self.data.date()}, cliente={self.cliente})>"
