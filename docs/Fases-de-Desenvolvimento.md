# Fases de Desenvolvimento

**Status:** Fases 0, 1, 2, 3 e 4 concluídas; Fase 5 pronta para ativação

Este documento organiza a construção do MVP e define os critérios para avançar entre fases.

## Ordem geral

```text
Discovery -> Fundação -> Backend -> Frontend -> Integração -> Testes -> Empacotamento -> Entrega
```

Uma fase pode ter atividades paralelas somente quando não houver dependência de contrato ou comportamento entre elas.

## Fase 0 - Discovery e contrato do produto

**Objetivo:** transformar a visão do produto em regras implementáveis.

**Atividades:**

- Confirmar campos, estados e regras da tarefa.
- Fechar comportamento do Score ICE.
- Fechar comportamento dos deadlines e do fuso horário.
- Definir filtros, ordenações e desempates.
- Registrar decisões no `Discovery.md`.

**Sessão principal:** administração/produto.

**Saída obrigatória:** regras de negócio e pontos pendentes identificados.

**Critério de saída:** nenhuma regra necessária para o primeiro fluxo de tarefa permanece ambígua.

**Status:** concluída em 2026-09-20.

## Fase 1 - Fundação do projeto

**Status:** concluída em 2026-09-21.

**Objetivo:** criar a estrutura mínima executável sem implementar o produto inteiro.

**Atividades:**

- Escolher a estrutura de diretórios do Flask.
- Configurar dependências e ambiente local.
- Configurar Dockerfile e Docker Compose.
- Definir o caminho do SQLite e o volume persistente.
- Definir configuração de ambiente, incluindo o fuso horário.
- Definir como mudanças futuras de schema serão controladas.

**Sessões envolvidas:** backend e testes.

**Saída obrigatória:** aplicação inicia e consegue acessar o banco persistente.

**Critério de saída:** o container e a execução local estão documentados e verificáveis.

**Verificação registrada:** a execução local respondeu `GET /health` com banco
disponível e schema `1`; o Compose foi construído e iniciado com a pasta
`./data` persistida em `/app/data`, e respondeu ao mesmo endpoint. O Compose
usa `:Z` no bind mount para suportar hosts com SELinux habilitado.

## Fase 2 - Domínio e persistência do backend

**Status:** concluída em 2026-09-27.

**Objetivo:** implementar a entidade tarefa e suas regras sem depender da interface final.

**Atividades:**

- Criar o modelo de tarefa.
- Implementar validação dos valores ICE de 1 a 10.
- Implementar cálculo do score.
- Implementar deadline opcional e detecção de atraso.
- Implementar status aberta/concluída.
- Implementar tags.
- Implementar persistência, consulta e exclusão.

**Sessões envolvidas:** backend e testes.

**Atualização de 2026-09-21:**

- A Fase 2 foi autorizada após o push da fundação no commit `179b9f8`.
- `BE-002` está responsável pelo domínio e pela persistência.
- `QA-002` está responsável por preparar e validar os cenários da fase.
- O escopo atual não inclui rotas de aplicação, templates, frontend ou identidade visual.
- O próximo retorno esperado do Backend é o schema e as regras implementadas para validação dos Testes.

**Saída obrigatória:** regras cobertas por testes de unidade e integração de persistência.

**Critério de saída:** o backend fornece dados consistentes sem depender de regras duplicadas no frontend.

**Verificação registrada:** a migração `002_tasks.sql` criou o modelo de tarefas
e tags; score, validações, atraso, status, filtros, ordenações, CRUD e
persistência após nova instância foram exercitados por 14 testes. Os casos
`QA-002-F01` e `QA-002-F02` foram corrigidos e revalidados; o Compose e o banco
existente permanecem no schema `2`, sem nova migração.

## Fase 3 - Rotas e contrato de aplicação

**Status:** concluída em 2026-09-27.

**Objetivo:** disponibilizar os fluxos que o frontend consumirá.

**Atividades:**

- Definir rotas de listagem, criação, edição, conclusão e exclusão.
- Definir entradas, mensagens de validação e respostas.
- Definir filtros e ordenações.
- Definir o contexto entregue aos templates.
- Registrar qualquer contrato em formato legível no código ou na documentação apropriada.

**Sessões envolvidas:** backend, frontend e testes.

**Atualização de 2026-09-27:**

- A Fase 2 foi encerrada após 14 testes aprovados e revalidação do schema `2`.
- O domínio foi congelado em `CONTRATO-DOMINIO.md`.
- O contrato de rotas, formulários e contexto foi criado em `CONTRATO-APLICACAO.md`.
- Backend, Frontend e Testes devem trabalhar somente no contrato da aplicação nesta fase.
- A identidade visual será aplicada somente na Fase 4, após o contrato ser validado.

**Saída obrigatória:** handoff para frontend e testes com rotas, campos e comportamentos confirmados.

**Critério de saída:** frontend e testes conseguem trabalhar sem adivinhar nomes de campos ou regras.

**Verificação registrada:** `BE-003` entregou as rotas e o contexto; `FE-002` confirmou a suficiência do contrato; `QA-003` aprovou 11 testes HTTP e a suíte completa passou com 25 testes.

## Fase 4 - Interface do frontend

**Status:** concluída em 2026-10-03.

**Objetivo:** criar uma interface limpa para o fluxo diário de tarefas.

**Atividades:**

- Criar listagem padrão de tarefas abertas por score.
- Criar formulário de tarefa com os campos ICE, deadline e tags.
- Exibir score, dimensões ICE e estado de atraso.
- Implementar filtros e ordenações definidos.
- Implementar ações de concluir, editar e excluir.
- Exibir validações e estados vazios.
- Garantir uso em telas menores.

**Sessões envolvidas:** frontend e testes.

**Atualização de 2026-09-27:**

- A Fase 3 foi encerrada após os retornos aprovados de Backend, Frontend e Testes.
- `FE-001` está responsável pela implementação da interface visual.
- `QA-004` está responsável pela validação da interface e dos fluxos reais.
- `IDENTIDADE-VISUAL.md` é a referência visual oficial desta fase.
- Backend permanece disponível somente para correções de contrato ou regressões.

**Atualização de 2026-09-27:**

- `FE-001` entregou a primeira interface visual em `app/templates/` e `app/static/styles.css`.
- Os fluxos e seletores do contrato foram preservados; a suíte completa passou com 33 testes.
- `QA-004` deve validar contraste, foco, responsividade, acessibilidade e fluxos reais antes do encerramento.
- A inspeção local deve seguir `VALIDACAO-VISUAL-F4.md` em telas desktop e mobile.

**Saída obrigatória:** fluxo principal navegável sem dados falsos escondendo falhas de integração.

**Critério de saída:** os fluxos definidos em `Discovery.md` funcionam usando o backend real.

**Atualização de 2026-10-03:**

- A Fase 4 foi encerrada com a inspeção visual local aprovada pelo usuário, seguindo `VALIDACAO-VISUAL-F4.md`.
- Entregas da fase além do roteiro original: gerenciamento de tags (`/tags`), resumo por email (CLI + botão `POST /digest/send`), painel dinâmico com filtro sem recarregar e modo painel fixo (desktop >= 801px).
- A suíte completa fechou com 53 testes `OK`; o envio real de email foi confirmado via Gmail.

**Verificação registrada:** interface aprovada na inspeção visual de 2026-10-03; suíte com 53 testes aprovados; contrato HTTP atualizado com a rota `POST /digest/send`.

## Fase 5 - Integração ponta a ponta

**Objetivo:** validar que persistência, rotas e interface representam o mesmo comportamento.

**Atividades:**

- Testar criação até a exibição na lista.
- Testar edição dos valores ICE e recálculo do score.
- Testar deadlines passados e filtro de atraso.
- Testar conclusão, reabertura se suportada e exclusão.
- Testar tags, filtros e ordenações.
- Corrigir divergências de contrato por meio de handoffs.

**Sessões envolvidas:** backend, frontend e testes.

**Critério de saída:** fluxos ponta a ponta passam sem dados ou regras duplicadas de forma conflitante.

## Fase 6 - Testes e endurecimento

**Objetivo:** garantir comportamento previsível nos limites do MVP.

**Atividades:**

- Executar testes unitários, de integração e de interface disponíveis.
- Validar limites do Score ICE.
- Validar datas, fuso horário e tarefas sem deadline.
- Validar persistência após reinício do container.
- Validar confirmação de exclusão.
- Registrar defeitos e encaminhá-los à sessão responsável.

**Sessão principal:** testes.

**Critério de saída:** nenhuma falha crítica ou regra de aceite sem cobertura ou justificativa registrada.

## Fase 7 - Backup, restauração e entrega

**Objetivo:** comprovar a portabilidade da instância.

**Atividades:**

- Parar a aplicação de forma segura.
- Copiar ou arquivar o volume SQLite.
- Subir uma instância limpa com o volume restaurado.
- Confirmar a preservação de tarefas, tags, status, deadlines e scores.
- Documentar os comandos reais de backup e restauração.

**Sessões envolvidas:** backend e testes.

**Critério de saída:** uma cópia do volume restaura a mesma instância sem perda de dados.

## Regra de avanço

Nenhuma sessão deve marcar uma fase como concluída apenas porque o código foi escrito. A fase só avança após seu critério de saída ser verificado e registrado no documento de administração das sessões.
