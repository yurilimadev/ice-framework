# Roteador da Documentação

Este é o ponto de entrada para qualquer nova sessão. Leia primeiro este arquivo e `CONTEXTO-ATUAL.md`; depois siga o caminho correspondente ao seu papel.

## Estado atual

- Fases 0, 1, 2 e 3 concluídas.
- Fase 4 em validação.
- Interface visual implementada pelo Frontend.
- Suíte automatizada atual: 53 testes aprovados.
- Pendência atual: inspeção visual renderizada e aceitação formal da Fase 4.
- Próxima fase: integração ponta a ponta.

O status operacional detalhado fica em `CONTEXTO-ATUAL.md`.

## Roteamento por papel

| Papel | Leia primeiro | Depois consulte |
|---|---|---|
| Administração/Tech Lead | `CONTEXTO-ATUAL.md` | `Fases-de-Desenvolvimento.md`, `sessoes/Administracao-de-Sessoes.md` |
| Backend | `CONTEXTO-ATUAL.md` | `CONTRATO-DOMINIO.md`, `CONTRATO-APLICACAO.md`, `sessoes/Sessao-Backend.md` |
| Frontend | `CONTEXTO-ATUAL.md` | `CONTRATO-APLICACAO.md`, `IDENTIDADE-VISUAL.md`, `sessoes/Sessao-Frontend.md` |
| Testes | `CONTEXTO-ATUAL.md` | `CONTRATO-APLICACAO.md`, `sessoes/Sessao-Testes.md` |

## Mapa dos documentos

### Produto e decisões

- `Discovery.md`: decisões de produto, regras de negócio e critérios de aceite.
- `IDENTIDADE-VISUAL.md`: direção visual e limites da interface.
- `VALIDACAO-VISUAL-F4.md`: roteiro para inspeção local antes do encerramento da Fase 4.

### Fases e contratos

- `Fases-de-Desenvolvimento.md`: objetivos, critérios de saída e histórico das fases.
- `CONTRATO-DOMINIO.md`: campos, regras e operações do domínio.
- `CONTRATO-APLICACAO.md`: rotas, formulários, respostas e contexto dos templates.

### Backlog

- `BACKLOG.md`: demandas futuras registradas para próximas sessões.

### Sessões

- `sessoes/Administracao-de-Sessoes.md`: status, handoffs, retornos e encerramentos.
- `sessoes/Sessao-Backend.md`: responsabilidades do Backend.
- `sessoes/Sessao-Frontend.md`: responsabilidades do Frontend.
- `sessoes/Sessao-Testes.md`: responsabilidades de Testes e evidências.

## Fluxo de trabalho

1. Administração define a fase ativa e o objetivo da sessão.
2. A sessão lê o contexto atual e o contrato aplicável.
3. A sessão registra de quem precisa de retorno e qual condição a desbloqueia.
4. A sessão executa somente o escopo da fase atual.
5. A sessão registra verificações, arquivos afetados e handoffs.
6. Administração valida o critério de saída antes de abrir a próxima fase.

Não iniciar uma nova fase enquanto houver bloqueio aberto na fase atual.

## Continuidade entre sessões

Antes de encerrar uma sessão, atualize `CONTEXTO-ATUAL.md` com:

- O que foi concluído.
- O que foi verificado.
- O que permanece pendente.
- Quem deve ser acionado.
- Qual retorno é esperado.
- Qual condição desbloqueia o próximo passo.

Não copie detalhes completos de contratos ou logs para o snapshot. Aponte para o documento responsável.
