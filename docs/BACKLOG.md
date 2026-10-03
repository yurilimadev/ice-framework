# Backlog e Próximos Passos

Este documento registra demandas futuras que ainda não fazem parte do escopo atual.

## 1. Gerenciamento de Tags

**Status:** implementado e reestruturado na Fase 4 (2026-09-27): `/tags` em largura única, excluir disponível para todas as tags (desvincula das tarefas após confirmação), renomear e mesclar. Pendente inspeção visual no roteiro da fase.

## 2. Otimização do Filtro de Tags

**Status:** pendente de discovery.

## 3. Notificações por Email

**Status:** implementado e testado com envio real via Gmail (2026-09-29): CLI `python3 -m flask --app wsgi send-digest` E botão "Enviar resumo" na barra superior (`POST /digest/send`, rota nova no contrato). Email redesenhado na identidade ICE (HTML inline + versão texto puro anexada). Credenciais em `.env` local (modelo em `.env.example`, fora do git). Pendente decisão de agendamento (cron/systemd timer).

## Registro

- Data: 2026-09-27
- Origem: solicitação do usuário durante sessão de validação da Fase 4.
