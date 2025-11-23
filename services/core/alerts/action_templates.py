"""
Action Templates - Ações Corretivas Recomendadas para Alertas
Fase 7 - Sistema de Mensageria
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ActionTemplate:
    """Template para ação corretiva"""
    titulo: str
    descricao: str
    passos: List[str]
    prioridade: str  # baixa, media, alta, critica
    tempo_estimado: str
    responsavel_sugerido: str


class ActionTemplates:
    """Biblioteca de templates de ações corretivas"""

    # ========== FASE 3 - IOT SENSORES ==========

    UMIDADE_CRITICA_BAIXA = ActionTemplate(
        titulo="Ativar Irrigação de Emergência",
        descricao="Umidade do solo está abaixo de 15% - risco de perda de plantas",
        passos=[
            "1. Verificar funcionamento da bomba de irrigação",
            "2. Ligar bomba manualmente se automação falhou",
            "3. Monitorar leituras a cada 15 minutos",
            "4. Irrigar até atingir 25-30% de umidade",
            "5. Verificar sistema de drenagem após irrigação"
        ],
        prioridade="critica",
        tempo_estimado="15-30 minutos",
        responsavel_sugerido="Supervisor de Campo"
    )

    UMIDADE_ALTA = ActionTemplate(
        titulo="Melhorar Drenagem do Solo",
        descricao="Excesso de umidade pode causar apodrecimento de raízes",
        passos=[
            "1. Desligar sistema de irrigação imediatamente",
            "2. Verificar sistema de drenagem",
            "3. Abrir canais de escoamento se necessário",
            "4. Evitar pisoteio na área afetada",
            "5. Monitorar a cada 2 horas"
        ],
        prioridade="alta",
        tempo_estimado="1-2 horas",
        responsavel_sugerido="Técnico Agrícola"
    )

    PH_ACIDO = ActionTemplate(
        titulo="Correção de Solo Ácido",
        descricao="pH abaixo de 5.5 prejudica absorção de nutrientes",
        passos=[
            "1. Realizar análise detalhada do solo",
            "2. Calcular quantidade de calcário necessária",
            "3. Aplicar calcário dolomítico (200-300 kg/ha)",
            "4. Incorporar ao solo com grade leve",
            "5. Aguardar 30 dias e fazer nova análise"
        ],
        prioridade="alta",
        tempo_estimado="2-4 horas + 30 dias",
        responsavel_sugerido="Técnico Agrícola"
    )

    PH_ALCALINO = ActionTemplate(
        titulo="Correção de Solo Alcalino",
        descricao="pH acima de 7.5 dificulta disponibilidade de nutrientes",
        passos=[
            "1. Confirmar pH com análise de laboratório",
            "2. Aplicar enxofre elementar (50-100 kg/ha)",
            "3. Incorporar matéria orgânica ao solo",
            "4. Aplicar sulfato de ferro se necessário",
            "5. Monitorar pH semanalmente"
        ],
        prioridade="media",
        tempo_estimado="2-3 horas + acompanhamento",
        responsavel_sugerido="Técnico Agrícola"
    )

    TEMPERATURA_ALTA = ActionTemplate(
        titulo="Mitigar Estresse Térmico",
        descricao="Temperatura elevada pode causar queima e desidratação",
        passos=[
            "1. Aumentar frequência de irrigação em 30%",
            "2. Irrigar preferencialmente no período da manhã",
            "3. Considerar sombreamento parcial",
            "4. Aplicar cobertura morta (mulching)",
            "5. Evitar podas e aplicações de defensivos"
        ],
        prioridade="media",
        tempo_estimado="1-2 horas",
        responsavel_sugerido="Supervisor de Campo"
    )

    TEMPERATURA_BAIXA = ActionTemplate(
        titulo="Proteção Contra Frio",
        descricao="Temperatura baixa pode retardar crescimento",
        passos=[
            "1. Cobrir plantas sensíveis com lona/plástico",
            "2. Reduzir irrigação temporariamente",
            "3. Evitar podas e adubação foliar",
            "4. Proteger mudas e plantas jovens prioritariamente",
            "5. Monitorar previsão do tempo"
        ],
        prioridade="media",
        tempo_estimado="30-60 minutos",
        responsavel_sugerido="Técnico Agrícola"
    )

    # ========== FASE 6 - VISÃO COMPUTACIONAL ==========

    SEM_CAPACETE = ActionTemplate(
        titulo="Verificar Uso de EPIs",
        descricao="Funcionário detectado sem capacete de segurança",
        passos=[
            "1. Identificar o funcionário e local na imagem",
            "2. Interromper atividade se em área de risco",
            "3. Fornecer capacete adequado",
            "4. Registrar ocorrência no livro de segurança",
            "5. Realizar reciclagem de treinamento de segurança"
        ],
        prioridade="critica",
        tempo_estimado="5-10 minutos",
        responsavel_sugerido="Supervisor de Segurança"
    )

    FERRAMENTA_NAO_AUTORIZADA = ActionTemplate(
        titulo="Verificar Ferramenta em Área Restrita",
        descricao="Tesoura de poda ou ferramenta detectada fora de contexto",
        passos=[
            "1. Verificar se há autorização para uso da ferramenta",
            "2. Confirmar se área permite uso do equipamento",
            "3. Verificar se funcionário tem treinamento",
            "4. Inspecionar condições da ferramenta",
            "5. Registrar uso no controle de ferramentas"
        ],
        prioridade="media",
        tempo_estimado="5-15 minutos",
        responsavel_sugerido="Supervisor de Campo"
    )

    PESSOA_NAO_AUTORIZADA = ActionTemplate(
        titulo="Verificar Acesso à Área Restrita",
        descricao="Pessoa detectada em área que requer autorização",
        passos=[
            "1. Identificar a pessoa através do sistema de câmeras",
            "2. Verificar badge e autorização de acesso",
            "3. Escoltar até área autorizada se necessário",
            "4. Revisar procedimentos de controle de acesso",
            "5. Atualizar lista de acessos autorizados"
        ],
        prioridade="alta",
        tempo_estimado="10-20 minutos",
        responsavel_sugerido="Supervisor de Segurança"
    )

    # ========== FASE 1 - CLIMA E METEOROLOGIA ==========

    CHUVA_FORTE_PREVISTA = ActionTemplate(
        titulo="Preparar para Chuva Forte",
        descricao="Previsão de precipitação intensa nas próximas horas",
        passos=[
            "1. Cobrir áreas de secagem de grãos/produtos",
            "2. Verificar sistema de drenagem e calhas",
            "3. Proteger insumos e fertilizantes",
            "4. Adiar aplicações de defensivos",
            "5. Verificar estruturas e telhados",
            "6. Monitorar áreas sujeitas a alagamento"
        ],
        prioridade="alta",
        tempo_estimado="30-60 minutos",
        responsavel_sugerido="Gerente de Operações"
    )

    SECA_PROLONGADA = ActionTemplate(
        titulo="Gestão de Seca Prolongada",
        descricao="Período sem chuvas previsto para os próximos dias",
        passos=[
            "1. Verificar reservatórios e disponibilidade de água",
            "2. Priorizar irrigação de culturas críticas",
            "3. Implementar irrigação por gotejamento se possível",
            "4. Aplicar cobertura morta para reduzir evaporação",
            "5. Evitar capinas que exponham solo",
            "6. Monitorar diariamente umidade do solo"
        ],
        prioridade="alta",
        tempo_estimado="Ação contínua",
        responsavel_sugerido="Gerente de Operações"
    )

    VENTO_FORTE = ActionTemplate(
        titulo="Proteção Contra Ventos Fortes",
        descricao="Ventos acima de 50 km/h previstos",
        passos=[
            "1. Reforçar estufas e estruturas temporárias",
            "2. Remover ou fixar objetos que possam voar",
            "3. Evitar pulverizações e aplicações foliares",
            "4. Verificar cercas e barreiras de proteção",
            "5. Postergar podas e outras intervenções"
        ],
        prioridade="media",
        tempo_estimado="45-90 minutos",
        responsavel_sugerido="Supervisor de Campo"
    )

    GEADA_PREVISTA = ActionTemplate(
        titulo="Preparação para Geada",
        descricao="Temperatura pode atingir 0°C ou abaixo",
        passos=[
            "1. Cobrir culturas sensíveis com mantas térmicas",
            "2. Irrigar levemente antes do anoitecer (efeito térmico)",
            "3. Preparar sistema de aquecimento se disponível",
            "4. Proteger mudas e plantas jovens prioritariamente",
            "5. Evitar podas e adubação 48h antes",
            "6. Monitorar temperatura durante a madrugada"
        ],
        prioridade="critica",
        tempo_estimado="2-4 horas",
        responsavel_sugerido="Gerente de Operações"
    )

    # ========== AÇÕES GENÉRICAS ==========

    FALHA_SENSOR = ActionTemplate(
        titulo="Verificar Sensor com Falha",
        descricao="Sensor não está enviando leituras ou valores inconsistentes",
        passos=[
            "1. Verificar conexão elétrica do sensor",
            "2. Limpar sonda/sensor de possíveis obstruções",
            "3. Verificar bateria ou alimentação",
            "4. Testar comunicação wireless/cabo",
            "5. Substituir sensor se necessário",
            "6. Recalibrar após manutenção"
        ],
        prioridade="media",
        tempo_estimado="20-40 minutos",
        responsavel_sugerido="Técnico de Manutenção"
    )

    FALHA_COMUNICACAO = ActionTemplate(
        titulo="Restaurar Comunicação IoT",
        descricao="Perda de conexão com gateway ou dispositivos IoT",
        passos=[
            "1. Verificar status do gateway central",
            "2. Reiniciar gateway se necessário",
            "3. Verificar conectividade de rede/internet",
            "4. Verificar alimentação elétrica",
            "5. Verificar logs de erro no sistema",
            "6. Contatar suporte técnico se problema persistir"
        ],
        prioridade="alta",
        tempo_estimado="15-45 minutos",
        responsavel_sugerido="Analista de TI"
    )

    @classmethod
    def get_action_by_code(cls, code: str) -> Optional[ActionTemplate]:
        """Retorna template de ação pelo código"""
        return getattr(cls, code, None)

    @classmethod
    def get_actions_for_alert_type(cls, alert_type: str) -> List[ActionTemplate]:
        """
        Retorna ações recomendadas para tipo de alerta

        Args:
            alert_type: Tipo do alerta (umidade_baixa, ph_alto, etc.)

        Returns:
            Lista de templates de ação aplicáveis
        """
        mapping = {
            # Fase 3 - IoT
            'umidade_critica_baixa': [cls.UMIDADE_CRITICA_BAIXA],
            'umidade_alta': [cls.UMIDADE_ALTA],
            'ph_baixo': [cls.PH_ACIDO],
            'ph_alto': [cls.PH_ALCALINO],
            'temperatura_alta': [cls.TEMPERATURA_ALTA],
            'temperatura_baixa': [cls.TEMPERATURA_BAIXA],

            # Fase 6 - CV
            'sem_capacete': [cls.SEM_CAPACETE],
            'ferramenta_nao_autorizada': [cls.FERRAMENTA_NAO_AUTORIZADA],
            'pessoa_nao_autorizada': [cls.PESSOA_NAO_AUTORIZADA],

            # Fase 1 - Clima
            'chuva_forte': [cls.CHUVA_FORTE_PREVISTA],
            'seca': [cls.SECA_PROLONGADA],
            'vento_forte': [cls.VENTO_FORTE],
            'geada': [cls.GEADA_PREVISTA],

            # Genéricos
            'falha_sensor': [cls.FALHA_SENSOR],
            'falha_comunicacao': [cls.FALHA_COMUNICACAO],
        }

        return mapping.get(alert_type, [])

    @classmethod
    def format_action_for_email(cls, action: ActionTemplate) -> str:
        """Formata ação para envio por email (HTML)"""
        passos_html = "".join([f"<li>{passo}</li>" for passo in action.passos])

        return f"""
        <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff;">
            <h3 style="margin-top: 0; color: #007bff;">{action.titulo}</h3>
            <p><strong>Descrição:</strong> {action.descricao}</p>
            <p><strong>Prioridade:</strong> <span style="color: #dc3545;">{action.prioridade.upper()}</span></p>
            <p><strong>Tempo Estimado:</strong> {action.tempo_estimado}</p>
            <p><strong>Responsável Sugerido:</strong> {action.responsavel_sugerido}</p>
            <p><strong>Passos:</strong></p>
            <ol style="margin-left: 20px;">
                {passos_html}
            </ol>
        </div>
        """

    @classmethod
    def format_action_for_sms(cls, action: ActionTemplate) -> str:
        """Formata ação para envio por SMS (texto curto)"""
        return f"{action.titulo}: {action.descricao[:80]}. Resp: {action.responsavel_sugerido}"

    @classmethod
    def get_all_actions(cls) -> Dict[str, ActionTemplate]:
        """Retorna todas as ações disponíveis"""
        actions = {}
        for attr_name in dir(cls):
            if attr_name.isupper() and not attr_name.startswith('_'):
                attr = getattr(cls, attr_name)
                if isinstance(attr, ActionTemplate):
                    actions[attr_name] = attr
        return actions
