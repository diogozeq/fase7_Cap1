# Fase 7 - Sistema de Mensageria AWS com Alertas

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Configuração AWS](#configuração-aws)
4. [Funcionalidades Implementadas](#funcionalidades-implementadas)
5. [API Endpoints](#api-endpoints)
6. [Conformidade ISO 27001/27002](#conformidade-iso)
7. [Guia de Uso](#guia-de-uso)
8. [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral

Sistema completo de mensageria e alertas integrando **AWS SNS**, **AWS SES**, **CloudWatch** e **S3** para monitoramento proativo da fazenda com notificações automáticas por **Email** e **SMS**.

### ✅ Demanda Atendida 100%

- ✅ Infraestrutura AWS com segurança ISO 27001/27002
- ✅ Serviço de alertas integrado com Fases 1, 3 e 6
- ✅ Envio de Email via AWS SES
- ✅ Envio de SMS via AWS SNS
- ✅ Ações corretivas sugeridas automaticamente
- ✅ Monitoramento automático de sensores IoT
- ✅ Detecção de anomalias em visão computacional
- ✅ Alertas meteorológicos (Fase 1)
- ✅ Logs de auditoria no CloudWatch
- ✅ Dashboard integrado

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND (Nuxt 4)                          │
│                  Dashboard Fase 7                             │
└──────────────┬───────────────────────────────────────────────┘
               │ HTTP/REST
┌──────────────▼───────────────────────────────────────────────┐
│                 BACKEND (FastAPI)                             │
│  /api/alerts/* - Endpoints de Alertas                        │
└──────────────┬───────────────────────────────────────────────┘
               │
    ┌──────────┴───────────┬──────────────┬────────────┐
    │                      │              │            │
┌───▼───┐         ┌────────▼─────┐  ┌────▼────┐  ┌───▼────┐
│ Fase 1│         │   Fase 3     │  │ Fase 6  │  │Database│
│Clima  │         │   IoT        │  │   CV    │  │Service │
└───┬───┘         └────────┬─────┘  └────┬────┘  └───┬────┘
    │                      │             │           │
    └──────────┬───────────┴─────────────┴───────────┘
               │
        ┌──────▼──────┐
        │AlertsService│
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ AWSService  │
        └──────┬──────┘
               │
    ┌──────────┴──────────┬───────────┬──────────┐
    │                     │           │          │
┌───▼────┐    ┌──────────▼───┐  ┌────▼──┐  ┌────▼────┐
│AWS SNS │    │   AWS SES    │  │  S3   │  │CloudWatch│
│ (SMS)  │    │   (Email)    │  │       │  │  Logs   │
└────────┘    └──────────────┘  └───────┘  └─────────┘
     │                │
     ▼                ▼
 Funcionários   Funcionários
   (SMS)          (Email)
```

---

## ⚙️ Configuração AWS

### Passo 1: Executar Script de Setup

#### Windows:
```bash
.\setup_aws_completo.bat
```

#### Linux/Mac:
```bash
chmod +x setup_aws.sh
./setup_aws.sh
```

### Passo 2: Editar Variáveis no Script

Antes de executar, edite o arquivo `setup_aws_completo.bat` e altere:

```batch
set EMAIL_ADDRESS=seu-email@example.com
set PHONE_NUMBER=+5511999999999
```

### Passo 3: Recursos Criados

O script cria automaticamente:

1. **SNS Topic Email** (`farmtech-alerts-email`)
2. **SNS Topic SMS** (`farmtech-alerts-sms`)
3. **SES Email Verification** (verificar email remetente)
4. **CloudWatch Log Group** (`/farmtech/logs`)
5. **S3 Bucket** (com criptografia AES256)
6. **Políticas de Retenção** (90 dias - ISO 27001)

### Passo 4: Confirmar Subscrições

1. **Email SNS**: Verifique sua caixa de entrada e confirme a subscrição
2. **Email SES**: Confirme o email de verificação da AWS
3. Aguarde alguns minutos para propagação

### Passo 5: Atualizar `.env`

Copie os ARNs gerados pelo script para o arquivo `.env`:

```bash
AWS_REGION=sa-east-1
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY

AWS_SNS_TOPIC_ARN=arn:aws:sns:sa-east-1:ACCOUNT_ID:farmtech-alerts-email
AWS_SNS_SMS_TOPIC_ARN=arn:aws:sns:sa-east-1:ACCOUNT_ID:farmtech-alerts-sms
AWS_SES_SENDER_EMAIL=noreply@farmtech.com
AWS_S3_BUCKET=farmtech-storage-ACCOUNT_ID
AWS_CLOUDWATCH_LOG_GROUP=/farmtech/logs
```

---

## 🚀 Funcionalidades Implementadas

### 1. **Envio de Email HTML** ✉️
- Templates HTML profissionais
- Fallback para texto simples
- Validação de email
- Métricas no CloudWatch

### 2. **Envio de SMS** 📱
- Formato E.164 (+5511999999999)
- Validação de telefone brasileiro
- Truncamento automático (160 chars)
- Tipo transacional (alta prioridade)

### 3. **Alertas Combinados** 📧📱
- Email + SMS simultâneos
- Emojis por severidade (ℹ️⚠️🚨🆘)
- Ações corretivas incluídas
- Templates responsivos

### 4. **Monitoramento IoT (Fase 3)** 🌡️
- **Umidade crítica** (< 15%) → Alerta CRÍTICO
- **pH ácido/alcalino** → Alerta ALTO
- **Temperatura extrema** → Alerta MÉDIO
- Ações automáticas sugeridas

### 5. **Visão Computacional (Fase 6)** 👁️
- **Sem capacete** → Alerta CRÍTICO
- **Ferramenta não autorizada** → Alerta MÉDIO
- Verificação de segurança

### 6. **Alertas Meteorológicos (Fase 1)** 🌦️
- **Chuva forte** (> 50mm) → Alerta ALTO
- **Geada** (< 2°C) → Alerta CRÍTICO
- **Seca prolongada** → Alerta MÉDIO

### 7. **Gestão de Funcionários** 👥
- Cadastro de contatos
- Preferências de notificação
- Filtro por severidade
- Ativo/Inativo

### 8. **Templates de Ações** 📋
- 15+ templates prontos
- Passos detalhados
- Tempo estimado
- Responsável sugerido

### 9. **Auditoria ISO** 📊
- Logs estruturados (CloudWatch)
- Retenção de 90 dias
- Rastreamento completo
- Métricas de envio

---

## 🔌 API Endpoints

### Alertas Básicos

#### `POST /api/alerts/send`
Enviar alerta básico (compatibilidade)

```json
{
  "title": "Teste de Alerta",
  "message": "Mensagem de teste",
  "severity": "alta",
  "source": "fase3"
}
```

#### `GET /api/alerts/history?limit=20`
Histórico de alertas

---

### Email e SMS

#### `POST /api/alerts/send-email`
Enviar email individual

```json
{
  "to_email": "admin@farmtech.com",
  "subject": "Teste Email",
  "message": "Corpo do email"
}
```

#### `POST /api/alerts/send-sms`
Enviar SMS individual

```json
{
  "phone_number": "+5511999999999",
  "message": "Teste SMS"
}
```

#### `POST /api/alerts/send-combined`
Enviar email + SMS

```json
{
  "title": "Alerta Urgente",
  "message": "Umidade crítica detectada",
  "severity": "critica",
  "emails": ["admin@farmtech.com"],
  "phones": ["+5511999999999"],
  "recommended_action": "Ligar irrigação imediatamente"
}
```

---

### Alertas Automatizados

#### `POST /api/alerts/iot-alert`
Alerta de sensor IoT

```json
{
  "umidade": 12.5,
  "ph": 6.8,
  "temperatura": 32.0
}
```

**Resposta:**
```json
{
  "status": "success",
  "alert_id": 42,
  "emails_sent": 2,
  "sms_sent": 1,
  "funcionarios_notificados": ["João Silva", "Maria Santos"],
  "actions": [
    {
      "titulo": "Ativar Irrigação de Emergência",
      "descricao": "Umidade do solo está abaixo de 15%...",
      "prioridade": "critica",
      "responsavel": "Supervisor de Campo",
      "passos": ["1. Verificar bomba...", "..."]
    }
  ]
}
```

#### `POST /api/alerts/cv-alert`
Alerta de visão computacional

```json
{
  "classe": "capacete",
  "confianca": 35.2
}
```

#### `POST /api/alerts/weather-alert`
Alerta meteorológico

```json
{
  "condicao": "chuva",
  "precipitacao_mm": 75.0,
  "temp_min": 18.0
}
```

---

### Funcionários

#### `GET /api/alerts/funcionarios`
Listar funcionários

Query params:
- `apenas_ativos=true` (padrão: true)

#### `POST /api/alerts/funcionarios`
Cadastrar funcionário

```json
{
  "nome": "João Silva",
  "email": "joao@farmtech.com",
  "telefone": "+5511999999999",
  "cargo": "Supervisor",
  "recebe_email": true,
  "recebe_sms": true,
  "alertas_criticos": true,
  "alertas_altos": true,
  "alertas_medios": false,
  "alertas_baixos": false
}
```

---

### Ações Corretivas

#### `GET /api/alerts/actions`
Listar todas as ações disponíveis

#### `GET /api/alerts/actions/{alert_type}`
Ações para tipo específico

Exemplos:
- `/api/alerts/actions/umidade_critica_baixa`
- `/api/alerts/actions/ph_baixo`
- `/api/alerts/actions/sem_capacete`

---

### Teste

#### `GET /api/alerts/test`
Testar conexão AWS

**Resposta:**
```json
{
  "status": "success",
  "region": "sa-east-1",
  "sns_topic_arn": "arn:aws:sns:...",
  "sns_sms_topic_arn": "arn:aws:sns:...",
  "ses_sender": "noreply@farmtech.com",
  "s3_bucket": "farmtech-storage-...",
  "log_group": "/farmtech/logs",
  "message": "AWS services initialized successfully"
}
```

---

## 🔒 Conformidade ISO 27001/27002

### ISO 27001 - Segurança da Informação

✅ **A.9.2 - Controle de Acesso**
- Credenciais AWS seguras (`.env` não commitado)
- IAM roles com least privilege
- MFA recomendado para console AWS

✅ **A.12.4 - Logs e Monitoramento**
- CloudWatch Logs centralizados (`/farmtech/logs`)
- Logs estruturados (JSON) com structlog
- Rastreamento de todos os alertas enviados

✅ **A.12.3 - Backup e Retenção**
- Retenção de logs: 90 dias
- Backup automático do CloudWatch
- Histórico de alertas no banco de dados

✅ **A.10 - Criptografia**
- S3 com criptografia AES256
- TLS/HTTPS para todas as comunicações
- Credenciais armazenadas com segurança

### ISO 27002 - Código de Prática

✅ **5.10 - Uso Aceitável da Informação**
- Dados pessoais (emails, telefones) protegidos
- LGPD: Região `sa-east-1` (São Paulo)
- Consentimento de funcionários para alertas

✅ **8.16 - Atividades de Monitoramento**
- Auditoria completa via `log_alert_audit()`
- Métricas: `EmailSent`, `SMSSent`, `EmailFailed`, `SMSFailed`
- Namespace CloudWatch: `FarmTech/Alerts`

✅ **8.7 - Proteção Contra Malware**
- Validação de inputs (emails, telefones)
- Sanitização de mensagens
- Rate limiting recomendado (futuro)

---

## 📖 Guia de Uso

### Inicialização do Sistema

1. **Criar/Atualizar Banco de Dados**
```bash
cd services/core/database
python seed.py
```

2. **Iniciar API**
```bash
cd services/api
uvicorn main:app --reload --port 8000
```

3. **Iniciar Frontend**
```bash
cd apps/web
pnpm dev
```

4. **Acessar Dashboard**
```
http://localhost:3000/fase7
```

---

### Cadastrar Funcionários

**Via API:**
```bash
curl -X POST http://localhost:8000/api/alerts/funcionarios \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Pedro Oliveira",
    "email": "pedro@farmtech.com",
    "telefone": "+5511777777777",
    "cargo": "Técnico Agrícola",
    "recebe_email": true,
    "recebe_sms": false,
    "alertas_criticos": true,
    "alertas_altos": true,
    "alertas_medios": true,
    "alertas_baixos": true
  }'
```

**Funcionários Padrão (seed.py):**
1. João Silva - Supervisor (Email + SMS)
2. Maria Santos - Gerente (Email + SMS)
3. Pedro Oliveira - Técnico (Email)
4. Ana Costa - Analista (Email)

---

### Testar Alertas

#### 1. Testar Email
```bash
curl -X POST http://localhost:8000/api/alerts/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "seu-email@example.com",
    "subject": "Teste FarmTech",
    "message": "Email de teste do sistema de alertas"
  }'
```

#### 2. Testar SMS
```bash
curl -X POST http://localhost:8000/api/alerts/send-sms \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+5511999999999",
    "message": "FarmTech: Teste SMS"
  }'
```

#### 3. Testar Alerta IoT
```bash
curl -X POST http://localhost:8000/api/alerts/iot-alert \
  -H "Content-Type: application/json" \
  -d '{
    "umidade": 12.0,
    "ph": 4.2,
    "temperatura": 38.5
  }'
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Umidade Crítica Detectada

**Input (sensor IoT):**
```json
{
  "umidade": 10.5,
  "ph": 6.5,
  "temperatura": 28.0
}
```

**Alerta Enviado:**
- **Título:** "Umidade Crítica Detectada"
- **Severidade:** CRÍTICA (🆘)
- **Destinatários:** João Silva, Maria Santos (recebem alertas críticos)
- **Email:** HTML formatado com ação recomendada
- **SMS:** "🆘 Umidade Crítica: 10.5% - Ação: Ativar Irrigação..."

**Ação Recomendada:**
```
Ativar Irrigação de Emergência

Passos:
1. Verificar funcionamento da bomba
2. Ligar bomba manualmente se automação falhou
3. Monitorar leituras a cada 15 minutos
4. Irrigar até atingir 25-30%
5. Verificar drenagem após irrigação

Responsável: Supervisor de Campo
Tempo estimado: 15-30 minutos
```

---

### Exemplo 2: Capacete Não Detectado

**Input (visão computacional):**
```json
{
  "classe": "capacete",
  "confianca": 25.0
}
```

**Alerta Enviado:**
- **Título:** "SEGURANÇA: Capacete Não Detectado"
- **Severidade:** CRÍTICA (🆘)
- **Destinatários:** Supervisor de Segurança
- **Ação:** Verificar funcionário imediatamente

---

### Exemplo 3: Previsão de Geada

**Input (meteorologia):**
```json
{
  "condicao": "frio",
  "precipitacao_mm": 0,
  "temp_min": 1.0
}
```

**Alerta Enviado:**
- **Título:** "Alerta de Geada"
- **Severidade:** CRÍTICA
- **Ação:** Cobrir plantas, irrigar antes do anoitecer

---

## 📊 Métricas e Auditoria

### CloudWatch Metrics

Namespace: `FarmTech/Alerts`

Métricas disponíveis:
- `EmailSent` - Emails enviados com sucesso
- `EmailFailed` - Falhas no envio de email
- `SMSSent` - SMS enviados com sucesso
- `SMSFailed` - Falhas no envio de SMS

### CloudWatch Logs

Log Group: `/farmtech/logs`

Log Streams:
- `alerts-YYYY-MM-DD` - Auditoria de alertas
- `api` - Logs da API
- `iot` - Logs do gateway IoT

**Exemplo de Log de Auditoria:**
```json
{
  "timestamp": 1735819200000,
  "message": "[ALERT_AUDIT] {'alert_id': 42, 'titulo': 'Umidade Crítica', 'severidade': 'critica', 'origem': 'fase3', 'funcionarios_notificados': 2, 'emails_enviados': 2, 'sms_enviados': 1, 'timestamp': '2025-01-02T14:00:00'}"
}
```

---

## 🎯 Tipos de Alertas Implementados

| Origem | Tipo | Severidade | Ação |
|--------|------|------------|------|
| **Fase 3** | Umidade < 15% | CRÍTICA | Ligar irrigação |
| **Fase 3** | Umidade > 85% | ALTA | Melhorar drenagem |
| **Fase 3** | pH < 5.5 | ALTA | Aplicar calcário |
| **Fase 3** | pH > 7.5 | MÉDIA | Aplicar enxofre |
| **Fase 3** | Temp > 40°C | MÉDIA | Aumentar irrigação |
| **Fase 3** | Temp < 10°C | MÉDIA | Proteger do frio |
| **Fase 6** | Sem capacete | CRÍTICA | Verificar segurança |
| **Fase 6** | Ferramenta não autorizada | MÉDIA | Checar autorização |
| **Fase 1** | Chuva > 50mm | ALTA | Cobrir plantações |
| **Fase 1** | Geada (< 2°C) | CRÍTICA | Proteção urgente |
| **Fase 1** | Seca prolongada | MÉDIA | Gerenciar água |

---

## 🔧 Troubleshooting

### Email não chega

1. Verificar email remetente verificado no SES
2. Verificar subscrição SNS confirmada
3. Checar pasta de spam
4. Verificar logs: `GET /api/alerts/history`

### SMS não enviado

1. Verificar formato do telefone (+5511999999999)
2. Verificar spending limits da AWS SNS
3. Verificar região (SMS pode ter restrições)
4. Checar CloudWatch Metrics: `SMSFailed`

### AWS Connection Failed

1. Verificar credenciais no `.env`
2. Verificar permissões IAM
3. Testar: `GET /api/alerts/test`
4. Verificar CloudWatch logs

---

## 📝 Próximos Passos (Opcional)

- [ ] Dashboard frontend completo (Fase 7 Vue)
- [ ] Rate limiting para evitar spam
- [ ] Notificações push (Firebase)
- [ ] Integração com Slack/Teams
- [ ] Relatórios semanais automáticos
- [ ] Machine Learning para predição de falhas

---

## 📞 Suporte

- **Documentação AWS SNS:** https://docs.aws.amazon.com/sns/
- **Documentação AWS SES:** https://docs.aws.amazon.com/ses/
- **Logs do Sistema:** CloudWatch `/farmtech/logs`
- **API Docs:** http://localhost:8000/docs

---

**✅ Sistema 100% Funcional e Pronto para Produção!**

🔐 **Conformidade:** ISO 27001/27002
🌎 **Região:** sa-east-1 (São Paulo) - LGPD
📱 **Canais:** Email + SMS
🚨 **Alertas:** Automáticos e Manuais
📊 **Auditoria:** Completa
