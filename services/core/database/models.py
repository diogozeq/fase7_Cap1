"""
SQLAlchemy models based on Fase 2 MER
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Cultura(Base):
    """Cultura model - Fase 2"""
    __tablename__ = 'culturas'
    
    id_cultura = Column(Integer, primary_key=True, autoincrement=True)
    nome_cultura = Column(String(100), nullable=False, unique=True)
    
    # Relationships
    talhoes = relationship("Talhao", back_populates="cultura")
    
    def __repr__(self):
        return f"<Cultura(id={self.id_cultura}, nome='{self.nome_cultura}')>"


class Talhao(Base):
    """Talhao model - Fase 2"""
    __tablename__ = 'talhoes'
    
    id_talhao = Column(Integer, primary_key=True, autoincrement=True)
    nome_talhao = Column(String(150), nullable=False, unique=True)
    area_hectares = Column(Numeric(10, 2), nullable=False)
    id_cultura_atual = Column(Integer, ForeignKey('culturas.id_cultura'), nullable=True)
    
    # Relationships
    cultura = relationship("Cultura", back_populates="talhoes")
    sensores = relationship("Sensor", back_populates="talhao")
    aplicacoes = relationship("AjusteAplicacao", back_populates="talhao")
    
    def __repr__(self):
        return f"<Talhao(id={self.id_talhao}, nome='{self.nome_talhao}')>"


class TipoSensor(Base):
    """TipoSensor model - Fase 2"""
    __tablename__ = 'tipos_sensor'
    
    id_tipo_sensor = Column(Integer, primary_key=True, autoincrement=True)
    nome_tipo_sensor = Column(String(50), nullable=False, unique=True)
    unidade_medida_padrao = Column(String(20), nullable=False)
    
    # Relationships
    sensores = relationship("Sensor", back_populates="tipo_sensor")
    
    def __repr__(self):
        return f"<TipoSensor(id={self.id_tipo_sensor}, nome='{self.nome_tipo_sensor}')>"


class Sensor(Base):
    """Sensor model - Fase 2"""
    __tablename__ = 'sensores'
    
    id_sensor = Column(Integer, primary_key=True, autoincrement=True)
    identificacao_fabricante = Column(String(100), nullable=False)
    data_instalacao = Column(Date, nullable=False)
    id_tipo_sensor = Column(Integer, ForeignKey('tipos_sensor.id_tipo_sensor'), nullable=False)
    id_talhao = Column(Integer, ForeignKey('talhoes.id_talhao'), nullable=False)
    
    # Relationships
    tipo_sensor = relationship("TipoSensor", back_populates="sensores")
    talhao = relationship("Talhao", back_populates="sensores")
    leituras = relationship("LeituraSensor", back_populates="sensor")
    
    def __repr__(self):
        return f"<Sensor(id={self.id_sensor}, fabricante='{self.identificacao_fabricante}')>"


class LeituraSensor(Base):
    """LeituraSensor model - Fase 2 + Fase 3 enhancements"""
    __tablename__ = 'leituras_sensores'
    
    id_leitura = Column(Integer, primary_key=True, autoincrement=True)
    data_hora_leitura = Column(DateTime, nullable=False, unique=True, index=True, default=datetime.utcnow)
    id_sensor = Column(Integer, ForeignKey('sensores.id_sensor'), nullable=False)
    
    # Sensor values
    valor_umidade = Column(Numeric(5, 2), nullable=True)
    valor_ph = Column(Numeric(4, 2), nullable=True)
    valor_fosforo_p = Column(Numeric(10, 2), nullable=True)
    valor_potassio_k = Column(Numeric(10, 2), nullable=True)
    temperatura = Column(Numeric(5, 2), nullable=True)
    precipitacao_mm = Column(Numeric(6, 2), nullable=True)
    
    # Fase 3: Irrigation logic
    bomba_ligada = Column(Boolean, nullable=False, default=False)
    decisao_logica_esp32 = Column(String(500), nullable=True)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="leituras")
    
    def __repr__(self):
        return f"<LeituraSensor(id={self.id_leitura}, timestamp='{self.data_hora_leitura}')>"

class InsumoCultura(Base):
    """Coeficientes de insumo e custo por cultura"""
    __tablename__ = 'insumos_cultura'

    id_insumo = Column(Integer, primary_key=True, autoincrement=True)
    id_cultura = Column(Integer, ForeignKey('culturas.id_cultura'), nullable=False, unique=True)
    coef_insumo_por_m2 = Column(Numeric(8, 4), nullable=False)
    custo_por_m2 = Column(Numeric(12, 2), nullable=False)

    cultura = relationship("Cultura")

    def __repr__(self):
        return f"<InsumoCultura(cultura={self.id_cultura}, coef={self.coef_insumo_por_m2})>"


class AjusteAplicacao(Base):
    """AjusteAplicacao model - Fase 2"""
    __tablename__ = 'ajustes_aplicacao'
    
    id_aplicacao = Column(Integer, primary_key=True, autoincrement=True)
    data_hora_aplicacao = Column(DateTime, nullable=False, default=datetime.utcnow)
    id_talhao = Column(Integer, ForeignKey('talhoes.id_talhao'), nullable=False)
    tipo_ajuste = Column(String(20), nullable=False)
    quantidade_aplicada = Column(Numeric(10, 2), nullable=False)
    unidade_medida_aplicacao = Column(String(20), nullable=False)
    nome_nutriente_aplicado = Column(String(100), nullable=True)
    
    # Relationships
    talhao = relationship("Talhao", back_populates="aplicacoes")
    
    def __repr__(self):
        return f"<AjusteAplicacao(id={self.id_aplicacao}, tipo='{self.tipo_ajuste}')>"


class Deteccao(Base):
    """Deteccao model - Fase 6"""
    __tablename__ = 'deteccoes'
    
    id_deteccao = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    imagem_nome = Column(String(255), nullable=False)
    classe = Column(String(100), nullable=False)
    confianca = Column(Numeric(5, 2), nullable=False)
    bbox = Column(String(255), nullable=True)  # Stored as string "[x1, y1, x2, y2]"
    
    def __repr__(self):
        return f"<Deteccao(id={self.id_deteccao}, classe='{self.classe}')>"


class ProducaoAgricola(Base):
    """ProducaoAgricola model - dados históricos de produção"""
    __tablename__ = 'producao_agricola'

    id_producao = Column(Integer, primary_key=True, autoincrement=True)
    id_cultura = Column(Integer, ForeignKey('culturas.id_cultura'), nullable=False)
    quantidade_produzida = Column(Numeric(12, 2), nullable=True)
    data_colheita = Column(DateTime, nullable=True)
    valor_estimado = Column(Numeric(14, 2), nullable=True)
    area_plantada = Column(Numeric(10, 2), nullable=True)

    cultura = relationship("Cultura")

    def __repr__(self):
        return f"<ProducaoAgricola(id={self.id_producao}, cultura={self.id_cultura})>"


class Alert(Base):
    """Alert model - Fase 7"""
    __tablename__ = 'alertas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    mensagem = Column(String(1000), nullable=False)
    severidade = Column(String(20), nullable=False)  # baixa, media, alta, critica
    origem = Column(String(50), nullable=False)      # fase1, fase3, fase6
    message_id = Column(String(100), nullable=True)  # SNS/SES message ID
    data_hora = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Alert(id={self.id}, titulo='{self.titulo}', severidade='{self.severidade}')>"


class Funcionario(Base):
    """Funcionario model - Fase 7: Contatos para alertas"""
    __tablename__ = 'funcionarios'

    id_funcionario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, index=True)
    telefone = Column(String(20), nullable=True)  # Formato E.164: +5511999999999
    cargo = Column(String(100), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    recebe_alertas = Column(Boolean, nullable=False, default=True)

    # Preferências de notificação
    recebe_email = Column(Boolean, nullable=False, default=True)
    recebe_sms = Column(Boolean, nullable=False, default=False)

    # Tipos de alertas que recebe (JSON ou flags separadas)
    alertas_criticos = Column(Boolean, nullable=False, default=True)
    alertas_altos = Column(Boolean, nullable=False, default=True)
    alertas_medios = Column(Boolean, nullable=False, default=False)
    alertas_baixos = Column(Boolean, nullable=False, default=False)

    data_cadastro = Column(DateTime, nullable=False, default=datetime.utcnow)
    ultima_atualizacao = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Funcionario(id={self.id_funcionario}, nome='{self.nome}', cargo='{self.cargo}')>"
