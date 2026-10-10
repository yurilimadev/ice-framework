# Administração de Sessões

Este documento coordena sessões de trabalho especializadas e registra dependências entre elas.

## Como administrar uma sessão

### 1. Iniciar

- Ler `../README.md` e `../CONTEXTO-ATUAL.md`.
- Identificar a fase ativa, a sessão responsável e o critério de saída.
- Ler apenas o contrato e o documento do papel necessários para a atividade.
- Confirmar o retorno necessário antes de iniciar qualquer implementação ou validação.

### 2. Executar

- Trabalhar somente no escopo da fase ativa.
- Não assumir regras que não estejam no contrato ou no discovery.
- Registrar alterações de contrato, schema, UI ou infraestrutura como handoff.
- Encaminhar defeitos para a sessão dona do comportamento, sem mascarar a falha.

### 3. Encerrar

- Registrar o que foi feito e as verificações executadas.
- Informar arquivos ou áreas afetadas.
- Indicar de quem precisa de retorno, o pedido e a condição de desbloqueio.
- Atualizar `../CONTEXTO-ATUAL.md`.
- Marcar a sessão como concluída somente quando o critério de saída estiver verificado.

### 4. Trocar de fase

- Administração confere os handoffs recebidos.
- Administração confirma que não há bloqueio aberto na fase atual.
- Administração atualiza `Fases-de-Desenvolvimento.md`, `CONTEXTO-ATUAL.md` e este registro.
- Somente depois a próxima sessão é ativada.

## Regra de continuidade

Quando o contexto da conversa estiver próximo do limite, não reconstituir o histórico inteiro. Atualizar `../CONTEXTO-ATUAL.md`, registrar os retornos pendentes e iniciar a próxima sessão por `../README.md`.

## Princípios

- Cada sessão trabalha dentro do escopo de seu documento.
- Nenhuma sessão deve assumir contrato, campo ou regra que não esteja registrado.
- Mudanças de contrato exigem handoff explícito para todas as sessões afetadas.
- A sessão que identifica um defeito encaminha a correção para a sessão dona do comportamento.
- A sessão de testes pode criar ou ajustar testes, mas não deve esconder uma falha alterando expectativas sem decisão registrada.
- Comandos só entram na documentação depois de serem confirmados pela configuração executável do projeto.
- As fases devem ser executadas uma por vez; a próxima só começa após o critério de saída da fase atual ser verificado.
- O papel do assistente é coordenar o registro, orientar a próxima sessão e apontar dependências; a implementação deve ser executada pela sessão responsável, não pelo assistente.
- Toda sessão deve indicar de quem precisa de retorno, qual retorno espera e qual condição permite continuar.

## Papéis

| Sessão | Responsabilidade principal | Documento |
|---|---|---|
| Backend | Domínio, persistência, rotas, validações e configuração de execução | `Sessao-Backend.md` |
| Frontend | Templates, estilos, interação, acessibilidade e estados visuais | `Sessao-Frontend.md` |
| Testes | Estratégia de verificação, testes, fixtures e evidências | `Sessao-Testes.md` |
| Administração | Ordem das fases, decisões, handoffs e bloqueios | Este documento |

## Ordem recomendada de execução

1. Administração fecha as regras do discovery.
2. Backend cria a fundação e o domínio mínimo.
3. Testes cobre as regras do domínio enquanto o backend evolui.
4. Backend publica o contrato das rotas e dos dados.
5. Frontend implementa a interface usando o contrato confirmado.
6. Testes executa integração e encaminha falhas para o dono correto.
7. Backend e testes validam Docker, persistência, backup e restauração.

## Matriz de impacto e handoff

| Alteração | Sessão que implementa | Informar obrigatoriamente | Ação dos destinatários |
|---|---|---|---|
| Regra de score, deadline ou status | Backend | Frontend e Testes | Atualizar exibição, fluxos e casos de teste |
| Campo, nome ou formato de rota | Backend | Frontend e Testes | Atualizar consumo, fixtures e verificações |
| Modelo SQLite, schema ou migração | Backend | Testes; Frontend se mudar dados exibidos | Validar persistência e impacto no fluxo |
| Filtro ou ordenação | Backend | Frontend e Testes | Atualizar controles, resultados e casos-limite |
| Template, seletor ou fluxo visual | Frontend | Testes | Atualizar testes de interface e acessibilidade |
| Estilo sem alteração de comportamento | Frontend | Testes, se houver seletor afetado | Fazer verificação visual/regressão apropriada |
| Falha de regra ou persistência | Testes | Backend | Criar reprodução e encaminhar correção |
| Falha de layout ou interação | Testes | Frontend | Criar reprodução e encaminhar correção |
| Falha de integração | Testes | Backend e Frontend | Identificar se a causa é contrato ou consumo |
| Docker, volume, ambiente ou backup | Backend | Testes e Frontend se afetar execução | Revalidar inicialização e operação completa |

## Tipos de handoff

- `CONTRATO`: campo, rota, resposta, status HTTP ou contexto de template mudou.
- `REGRA`: comportamento de score, deadline, status, filtro ou validação mudou.
- `SCHEMA`: estrutura do SQLite ou estratégia de migração mudou.
- `UI`: fluxo, seletor, texto, acessibilidade ou comportamento visual mudou.
- `INFRA`: Docker, volume, variável de ambiente ou backup mudou.
- `BUG`: uma sessão encontrou defeito pertencente a outra sessão.

## Modelo de handoff

Copiar este modelo para o registro da sessão ou para a mensagem de transição:

```markdown
### Handoff [ID] - [data]

- Origem:
- Destino:
- Tipo: CONTRATO | REGRA | SCHEMA | UI | INFRA | BUG
- Alteração:
- Arquivos ou áreas afetadas:
- Comportamento anterior:
- Comportamento novo:
- Ação obrigatória do destino:
- Retorno necessário de:
- Retorno solicitado:
- Condição de desbloqueio:
- Verificação executada:
- Bloqueios:
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03) | em validação | concluído
```

## Registro de sessões

| ID | Sessão | Fase | Status | Bloqueio ou próximo passo |
|---|---|---|---|---|
| ADM-001 | Discovery e planejamento | 0 | concluída | Fases 0 a 4 concluídas; Fase 5 pronta para ativação |
| BE-001 | Fundação e domínio | 1 | concluída | Fundação validada; sessão encerrada |
| FE-001 | Interface do MVP | 4 | concluída | Interface aprovada na inspeção visual de 2026-10-03 |
| QA-001 | Estratégia e execução de testes | 1 | concluída | Fundação validada; sessão encerrada |
| BE-002 | Domínio e persistência | 2 | concluída | Correções revalidadas; Fase 3 liberada |
| QA-002 | Testes do domínio e persistência | 2 | concluída | 14 testes passaram; Fase 3 liberada |
| BE-003 | Rotas e contrato de aplicação | 3 | concluída | Rotas validadas; suporte sob demanda na Fase 4 |
| FE-002 | Revisão do contrato de aplicação | 3 | concluída | Contexto confirmado; sessão encerrada |
| QA-003 | Testes do contrato de aplicação | 3 | concluída | 11 testes HTTP passaram; sessão encerrada |
| QA-004 | Testes de interface e integração | 4 | concluída | 53 testes e inspeção visual aprovados em 2026-10-03 |

### Handoff BE-F1-001 - 2026-09-21

- Origem: Backend
- Destino: Testes e Administração
- Tipo: INFRA
- Alteração: criada a fundação Flask com SQLite em caminho configurável, migração inicial controlada por `PRAGMA user_version`, Dockerfile e Compose com bind mount persistente.
- Arquivos ou áreas afetadas: `app/`, `migrations/001_foundation.sql`, `Dockerfile`, `compose.yaml`, `requirements.txt`, `wsgi.py`, `README.md`.
- Comportamento anterior: não havia aplicação executável, banco ou configuração de ambiente.
- Comportamento novo: a aplicação inicializa o banco, aplica schema `1` e expõe `GET /health`; localmente usa `data/app.sqlite3` e no Compose usa `/app/data/app.sqlite3` via `./data:/app/data:Z`.
- Ação obrigatória do destino: revalidar inicialização local e via Compose; manter a estratégia `PRAGMA user_version` ao adicionar o schema de tarefas.
- Verificação executada: `python3 -m flask --app wsgi routes`, cliente Flask em `GET /health`, servidor local com `curl`, `docker compose config`, `docker build` e `docker compose up --build --detach` com `curl` em `/health`.
- Bloqueios: nenhum para a Fase 1; a implementação do domínio ainda não foi iniciada.
- Status: concluído

### Handoff QA-F1-001 - 2026-09-21

- Origem: Testes
- Destino: Administração
- Tipo: INFRA
- Alteração: validada a fundação local e via Docker Compose, sem falhas de Backend identificadas.
- Arquivos ou áreas afetadas: `app/`, `migrations/001_foundation.sql`, `Dockerfile`, `compose.yaml`, `tests/test_foundation.py`.
- Comportamento anterior: fundação aguardava revalidação independente.
- Comportamento novo: a execução local e o container respondem `/health` com banco disponível e schema `1`; a inicialização repetida preserva o schema e o volume expõe o SQLite no container.
- Ação obrigatória do destino: considerar a Fase 1 validada e manter a sessão de Testes bloqueada para os cenários de tarefas até a implementação da Fase 2.
- Verificação executada: `python3 -m flask --app wsgi routes`; servidor Flask local com `curl` em `/health`; `docker compose config`; `docker compose build`; `docker compose up --detach`; `curl` em `http://127.0.0.1:8000/health`; `docker compose down`; nova subida do Compose; `python3 -m unittest discover -s tests -v`.
- Bloqueios: não há tarefas, tags, status, deadlines, score ou rotas de domínio para validar.
- Status: concluído

### Handoff ADM-F1-001 - 2026-09-21

- Origem: Administração
- Destino: Backend e Testes
- Tipo: INFRA
- Alteração: Fase 1 sincronizada como concluída; Fase 2 definida como próxima etapa.
- Arquivos ou áreas afetadas: `docs/Discovery.md`, `docs/Fases-de-Desenvolvimento.md`, registro de sessões.
- Comportamento anterior: Fase 1 validada, mas os registros administrativos ainda apontavam sessões em andamento.
- Comportamento novo: Backend e Testes da Fase 1 encerrados; novas sessões aguardam início da Fase 2.
- Ação obrigatória do destino: Backend deve solicitar autorização para iniciar o domínio; Testes deve informar a matriz de cenários prioritários da Fase 2.
- Retorno necessário de: Backend e Testes.
- Retorno solicitado: confirmação do escopo inicial da Fase 2 e dos cenários de validação prioritários.
- Condição de desbloqueio: registro de `BE-002` e `QA-002` como sessões da Fase 2.
- Verificação executada: comparação dos critérios da Fase 1 com as evidências dos handoffs `BE-F1-001` e `QA-F1-001`.
- Bloqueios: nenhum para a transição; a Fase 2 ainda não foi iniciada.
- Status: concluído

### Handoff ADM-F2-001 - 2026-09-21

- Origem: Administração
- Destino: Backend e Testes
- Tipo: REGRA
- Alteração: início formal da Fase 2 após a publicação da fundação da Fase 1.
- Arquivos ou áreas afetadas: domínio da tarefa, schema SQLite e testes de persistência.
- Comportamento anterior: Fase 2 aguardava autorização e as sessões `BE-002` e `QA-002` estavam bloqueadas.
- Comportamento novo: `BE-002` e `QA-002` estão ativas para implementar e validar o domínio e a persistência.
- Ação obrigatória do destino: Backend deve implementar somente o escopo da Fase 2; Testes deve preparar a matriz de cenários e validar após receber o schema.
- Retorno necessário de: Backend e Testes.
- Retorno solicitado: Backend deve enviar schema e regras implementadas; Testes deve enviar cenários prioritários e falhas encontradas.
- Condição de desbloqueio: schema de tarefas disponível para `QA-002`; critério de saída da Fase 2 verificado antes da Fase 3.
- Verificação executada: push da fundação concluído no commit `179b9f8`; critérios da Fase 1 já registrados como validados.
- Bloqueios: frontend permanece aguardando o contrato da Fase 3.
- Status: concluído

### Handoff BE-002 - 2026-09-21

- Origem: Backend
- Destino: Administração, Testes e Frontend
- Tipo: SCHEMA
- Alteração: implementado o domínio e a persistência da tarefa na migração `002_tasks.sql`.
- Arquivos ou áreas afetadas: `app/tasks.py`, `migrations/002_tasks.sql`, `docs/CONTRATO-DOMINIO.md` e `tests/test_tasks.py`.
- Comportamento anterior: SQLite possuía apenas o schema de fundação e `/health`.
- Comportamento novo: tarefas persistem título, fatores ICE, deadline, status, criação e tags; score e atraso são derivados pelo backend.
- Ação obrigatória do destino: Testes deve manter a matriz da Fase 2; Frontend deve consumir futuramente os nomes e regras do contrato sem recalcular score ou atraso.
- Retorno necessário de: Testes
- Retorno solicitado: confirmação dos cenários prioritários e resultado da suíte da Fase 2.
- Condição de desbloqueio: `QA-002` concluído; rotas permanecem para a Fase 3.
- Verificação executada: `python3 -m unittest discover -s tests -v`, compilação Python e Compose respondendo `/health` com schema `2`.
- Bloqueios: nenhum; `QA-002-F01` e `QA-002-F02` foram corrigidos e revalidados.
- Status: concluído

### Handoff QA-002 - 2026-09-21

- Origem: Testes
- Destino: Backend e Administração
- Tipo: REGRA
- Alteração: cenários prioritários da Fase 2 foram executados contra o domínio e a persistência.
- Arquivos ou áreas afetadas: `tests/test_tasks.py`, `tests/test_foundation.py`, `app/tasks.py`, `migrations/002_tasks.sql`.
- Comportamento anterior: não havia superfície de tarefas para validar.
- Comportamento novo: 11 testes cobrem ICE, score, deadlines, atraso, status, tags, filtros, ordenações, exclusão e persistência após nova instância.
- Ação obrigatória do destino: manter essas regras ao publicar as rotas da Fase 3 e encaminhar qualquer divergência como `CONTRATO` ou `REGRA`.
- Verificação executada: `python3 -m unittest discover -s tests -v` com resultado `OK`.
- Bloqueios: rotas HTTP de tarefas ainda não existem e ficam para a Fase 3.
- Status: concluído

### Handoff QA-002-F01 - 2026-09-21

- Origem: Testes
- Destino: Backend e Administração
- Tipo: BUG
- Alteração: entrada de tags com tipo não iterável escapa da validação de domínio.
- Arquivos ou áreas afetadas: `app/tasks.py`, função `normalize_tags`.
- Comportamento anterior: a função recebe `tags=123`.
- Comportamento novo: tipos não iteráveis são rejeitados com `ValidationError` controlado.
- Ação obrigatória do destino: rejeitar tipos incompatíveis com erro de validação controlado, sem deixar exceção de implementação chegar à camada de aplicação.
- Retorno necessário de: Backend.
- Retorno solicitado: informar a correção e preservar a validação para strings, iteráveis de strings e `None`.
- Condição de desbloqueio: teste `test_non_iterable_tags_are_rejected_as_validation_error` passar.
- Verificação executada: teste focado de tipo inválido e suíte completa; ambos passaram.
- Bloqueios: nenhum; rotas ainda não fazem parte desta falha.
- Status: revalidado

### Handoff QA-002-F02 - 2026-09-21

- Origem: Testes
- Destino: Backend e Administração
- Tipo: BUG
- Alteração: deduplicação de tags no domínio usa `casefold`, mas a restrição SQLite `COLLATE NOCASE` não cobre equivalências Unicode.
- Arquivos ou áreas afetadas: `app/tasks.py`, `_replace_tags`; `migrations/002_tasks.sql`, tabela `tags`.
- Comportamento anterior: a primeira grafia deveria ser preservada para tags equivalentes sem diferenciar maiúsculas e minúsculas.
- Comportamento novo: `Straße` e `STRASSE` reutilizam uma única linha persistida e a primeira grafia.
- Ação obrigatória do destino: alinhar a unicidade persistida à regra de normalização Unicode e manter a primeira grafia armazenada.
- Retorno necessário de: Backend.
- Retorno solicitado: informar a estratégia de correção de domínio e schema, incluindo eventual migração necessária.
- Condição de desbloqueio: teste `test_casefold_equivalent_tags_are_reused` passar e a migração permanecer reproduzível.
- Verificação executada: teste focado Unicode, suíte completa e validação do banco existente; schema `2` permaneceu sem nova migração.
- Bloqueios: nenhum; a correção foi feita no domínio sem alteração de schema.
- Status: revalidado

### Handoff QA-002-R1 - 2026-09-27

- Origem: Testes
- Destino: Administração, Backend e Frontend
- Tipo: REGRA
- Alteração: revalidação independente das correções `QA-002-F01` e `QA-002-F02` concluída sem regressões.
- Arquivos ou áreas afetadas: `app/tasks.py`, `tests/test_tasks.py`, `migrations/002_tasks.sql`, `compose.yaml`.
- Comportamento anterior: Fase 2 aguardava confirmação independente após as correções de tags.
- Comportamento novo: tipos inválidos de tags retornam `ValidationError`; equivalências Unicode reutilizam uma única tag preservando a primeira grafia; schema 2 funciona em banco novo e existente.
- Ação obrigatória do destino: iniciar a Fase 3 usando o contrato de domínio confirmado; rotas devem preservar score, atraso e normalização do Backend.
- Retorno necessário de: Administração e Frontend.
- Retorno solicitado: confirmar o início da Fase 3 e consumir `docs/CONTRATO-DOMINIO.md` sem duplicar as regras no frontend.
- Condição de desbloqueio: suíte focada e completa aprovadas, schema validado e Compose respondendo `/health` com schema 2.
- Verificação executada: 3 testes focados; `python3 -m unittest discover -s tests -v` com 14 testes `OK`; banco novo; upgrade de schema 1 para 2; `docker compose config`; `docker compose build`; `docker compose up --detach`; `curl http://127.0.0.1:8000/health`; `docker compose down`.
- Bloqueios: nenhum para iniciar a Fase 3; rotas HTTP ainda precisam ser implementadas e testadas na próxima fase.
- Status: concluído

### Handoff ADM-F3-001 - 2026-09-27

- Origem: Administração
- Destino: Backend, Frontend e Testes
- Tipo: CONTRATO
- Alteração: Fase 3 iniciada após a conclusão e validação da Fase 2.
- Arquivos ou áreas afetadas: `docs/CONTRATO-DOMINIO.md`, `docs/CONTRATO-APLICACAO.md`, rotas Flask, templates e testes HTTP.
- Comportamento anterior: o domínio estava validado, mas as rotas de aplicação ainda não existiam.
- Comportamento novo: o contrato de rotas, formulários, respostas e contexto está definido para implementação e validação.
- Ação obrigatória do destino: Backend implementa as rotas; Frontend revisa o consumo do contexto; Testes prepara e executa a matriz HTTP.
- Retorno necessário de: Backend, Frontend e Testes.
- Retorno solicitado: Backend deve informar rotas implementadas; Frontend deve apontar necessidades de contexto; Testes deve informar cobertura e falhas.
- Condição de desbloqueio: rotas, respostas e contexto validados pelas três sessões antes da Fase 4.
- Verificação executada: Fase 2 validada com 14 testes, schema `2` e Compose respondendo `/health`.
- Bloqueios: interface visual final permanece reservada para a Fase 4.
- Status: concluído

### Handoff BE-003 - 2026-09-27

- Origem: Backend
- Destino: Frontend, Testes e Administração
- Tipo: CONTRATO
- Alteração: primeira superfície HTTP da Fase 3 implementada conforme `CONTRATO-APLICACAO.md`.
- Arquivos ou áreas afetadas: `app/routes.py`, `app/__init__.py`, `app/tasks.py`, `app/templates/`, `tests/test_routes.py`.
- Comportamento anterior: o domínio existia, mas não havia rotas de aplicação nem contexto renderizado.
- Comportamento novo: listagem, criação, edição, conclusão, reabertura, exclusão, filtros, ordenações, validações `400`, `404` e redirecionamentos `303` estão disponíveis.
- Ação obrigatória do destino: FE-002 deve revisar campos e contexto; QA-003 deve executar a matriz HTTP independente e encaminhar divergências como `CONTRATO`.
- Retorno necessário de: Frontend e Testes
- Retorno solicitado: confirmar suficiência do contexto para a Fase 4 e resultado da matriz HTTP.
- Condição de desbloqueio: contrato e rotas validados por Backend, Frontend e Testes antes da Fase 4.
- Verificação executada: 11 testes HTTP, suíte completa com 25 testes `OK`, `python3 -m flask --app wsgi routes` e Compose com `/health` e `/` respondendo.
- Bloqueios: nenhum para continuar a validação da Fase 3; a identidade visual permanece fora desta fase.
- Status: concluído

### Handoff FE-002 - 2026-09-27

- Origem: Frontend
- Destino: Administração, Backend e Testes
- Tipo: CONTRATO
- Alteração: revisão do contrato da aplicação e da superfície HTTP entregue pelo `BE-003` concluída, sem divergências bloqueadoras.
- Arquivos ou áreas afetadas: `docs/CONTRATO-DOMINIO.md`, `docs/CONTRATO-APLICACAO.md`, `app/routes.py`, `app/templates/` e `tests/test_routes.py`.
- Comportamento anterior: Frontend aguardava a superfície executável para confirmar se os dados necessários à Fase 4 estavam disponíveis.
- Comportamento novo: o contexto recebido foi confirmado como suficiente para a Fase 4.
- Ação obrigatória do destino: QA-003 deve validar independentemente a matriz HTTP; Frontend deve preservar os nomes e os seletores registrados ao implementar a interface final.
- Contexto confirmado da listagem: `tasks` com `id`, `title`, `impact`, `confidence`, `ease`, `deadline`, `status`, `created_at`, `tags`, `score` e `overdue`; além de `available_tags`, `filters`, `errors` e `messages`.
- Contexto confirmado do formulário: `task`, `errors` e `form_values`, com preservação dos valores enviados em respostas `400`.
- Fluxos e seletores para cobertura: criação, edição, conclusão, reabertura, exclusão, filtros e estados vazios; `data-task-id`, `data-task-status`, `data-overdue`, `data-empty`, `data-error-field` e `data-message`.
- Necessidade para a Fase 4: a seleção visual de tags deve comparar equivalência Unicode com `casefold`, pois o filtro aceita `WORK` para a tag persistida como `Work`. Isso é uma regra de consumo do template, não uma alteração solicitada ao contrato do Backend.
- Retorno necessário de: QA-003.
- Retorno solicitado: resultado da matriz HTTP, incluindo métodos, status, contexto, preservação de formulário e filtros.
- Condição de desbloqueio: QA-003 aprovar a matriz HTTP e a Administração encerrar a Fase 3 antes do início da identidade visual final.
- Verificação executada: revisão dos contratos e dos templates; `python3 -m unittest discover -s tests -v`, 25 testes, resultado `OK`; `python3 -m flask --app wsgi routes` confirmou as rotas previstas.
- Bloqueios: nenhum bloqueio de contexto para o Frontend; a Fase 4 continua bloqueada até a validação do QA-003.
- Status: concluído

### Handoff QA-003-001 - 2026-09-27

- Origem: Testes
- Destino: Administração, Backend e Frontend
- Tipo: CONTRATO
- Alteração: matriz HTTP da Fase 3 executada contra as rotas Flask e os templates atuais.
- Arquivos ou áreas afetadas: `app/routes.py`, `app/templates/`, `tests/test_routes.py`, `docs/CONTRATO-APLICACAO.md`.
- Comportamento anterior: rotas implementadas aguardavam validação independente dos métodos, respostas, filtros e persistência.
- Comportamento novo: métodos e rotas previstos respondem conforme o contrato; erros retornam `400`, recursos inexistentes `404` e operações válidas `303`.
- Ação obrigatória do destino: Backend e Frontend devem preservar o contrato validado ao concluir a Fase 3; qualquer mudança de rota, campo, status ou contexto exige novo handoff `CONTRATO`.
- Retorno necessário de: Backend e Frontend.
- Retorno solicitado: Backend deve confirmar o encerramento das rotas; Frontend deve confirmar que o contexto permanece suficiente para a Fase 4.
- Condição de desbloqueio: QA-003 concluído; a Fase 4 ainda depende do encerramento formal da Fase 3 pela Administração.
- Verificação executada: `python3 -m unittest tests.test_routes -v` com 11 testes `OK`; `python3 -m unittest discover -s tests -v` com 25 testes `OK`.
- Bloqueios: nenhum defeito de rota encontrado; validação visual e encerramento formal do contrato ainda pendentes.
- Status: concluído

### Handoff ADM-F4-001 - 2026-09-27

- Origem: Administração
- Destino: Frontend, Testes e Backend
- Tipo: UI
- Alteração: Fase 3 encerrada e Fase 4 iniciada após alinhamento de Backend, Frontend e Testes.
- Arquivos ou áreas afetadas: `docs/IDENTIDADE-VISUAL.md`, templates, CSS, interação do MVP e testes de interface.
- Comportamento anterior: contrato HTTP validado; identidade visual e interface final aguardavam ativação.
- Comportamento novo: `FE-001` implementa a interface visual e `QA-004` valida os fluxos reais da aplicação.
- Ação obrigatória do destino: Frontend deve seguir o contrato e a identidade visual; Testes deve validar comportamento, acessibilidade e responsividade; Backend deve atender somente regressões ou alterações de contrato.
- Retorno necessário de: Frontend, Testes e Backend.
- Retorno solicitado: Frontend deve informar telas e seletores implementados; Testes deve informar cobertura e falhas; Backend deve responder a qualquer divergência de contrato.
- Condição de desbloqueio: interface principal, fluxos do MVP e validações de acessibilidade aprovados antes da Fase 5.
- Verificação executada: Fase 3 encerrada com 25 testes aprovados, revisão de contexto e confirmação do Backend.
- Bloqueios: nenhum para iniciar a Fase 4; integração ponta a ponta permanece para a Fase 5.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

### Handoff ADM-F4-VISUAL-001 - 2026-09-27

- Origem: Administração
- Destino: Frontend e Testes
- Tipo: UI
- Alteração: ativado o roteiro local para a inspeção visual final da Fase 4.
- Arquivos ou áreas afetadas: `docs/VALIDACAO-VISUAL-F4.md`, `app/templates/`, `app/static/styles.css`.
- Comportamento anterior: testes automatizados aprovados, mas inspeção visual renderizada ainda não registrada.
- Comportamento novo: a inspeção deve ser executada em viewports desktop e mobile com o Backend real.
- Ação obrigatória do destino: registrar evidências, corrigir falhas e retornar a decisão sobre a conclusão da Fase 4.
- Retorno necessário de: Frontend e Testes.
- Retorno solicitado: resultado do checklist visual, acessibilidade, responsividade e eventuais correções.
- Condição de desbloqueio: checklist concluído sem falhas críticas e Fase 4 encerrada pela Administração.
- Verificação executada: rotas locais confirmadas e roteiro publicado.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

### Handoff FE-001 - 2026-09-27

- Origem: Frontend
- Destino: Testes, Administração e Backend
- Tipo: UI
- Alteração: placeholders da Fase 3 substituídos pela interface visual responsiva da Fase 4, usando a identidade visual ICE.
- Arquivos ou áreas afetadas: `app/templates/`, `app/static/styles.css`, `tests/test_routes.py`, `docs/IDENTIDADE-VISUAL.md`.
- Comportamento anterior: templates funcionais sem identidade visual, hierarquia de conteúdo ou responsividade definida.
- Comportamento novo: painel de foco, filtros com tags case-insensitive, cards ICE, estados de atraso/conclusão, formulário responsivo, mensagens de erro acessíveis, estado vazio e confirmação visual de exclusão.
- Ação obrigatória do destino: QA-004 deve validar responsividade, acessibilidade, contraste, foco, estados e fluxos reais; Backend deve ser acionado somente se houver divergência do contrato.
- Retorno necessário de: Testes e Administração
- Retorno solicitado: resultado da validação visual e decisão sobre a conclusão da Fase 4.
- Condição de desbloqueio: QA-004 aprovar a interface em telas grandes e pequenas sem regressão dos seletores do contrato.
- Verificação executada: suíte completa com 33 testes `OK`, compilação Python, rotas preservadas e renderização HTTP validada; inspeção visual independente ainda pendente.
- Bloqueios: nenhum bloqueio de backend; validação visual, acessibilidade e responsividade pendentes.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

### Handoff QA-004-F01 - 2026-09-27

- Origem: Testes
- Destino: Frontend e Administração
- Tipo: UI
- Alteração: validação de acessibilidade encontrou dois tokens de texto abaixo do contraste WCAG AA para texto normal.
- Arquivos ou áreas afetadas: `app/static/styles.css`, `tests/test_frontend.py`.
- Comportamento anterior: a interface usava `--muted: #70878b` e o status concluído usava `#638078` sobre superfícies brancas.
- Comportamento novo: `--muted: #536e73` e status concluído `#52706f`, ambos com contraste superior a `4,5:1` sobre branco.
- Ação obrigatória do destino: ajustar os tokens/estilos de texto para atingir contraste mínimo AA sem remover a distinção textual de atraso e conclusão.
- Retorno necessário de: Frontend.
- Retorno solicitado: informar as cores ajustadas e solicitar nova execução do teste de contraste.
- Condição de desbloqueio: `test_normal_text_colors_meet_wcag_aa_contrast` passar e a suíte completa não apresentar falha de acessibilidade.
- Verificação executada: `python3 -m unittest tests.test_frontend -v`; 5 testes passaram, incluindo contraste. A suíte completa passou com 33 testes; o Compose serviu `/` e `/static/styles.css`.
- Bloqueios: nenhum bloqueio de contraste; a Fase 4 ainda aguarda validação visual independente dos demais cenários.
- Status: revalidado

### Handoff QA-004-R1 - 2026-09-27

- Origem: Testes
- Destino: Administração, Frontend e Backend
- Tipo: UI
- Alteração: avaliação independente dos fluxos e da interface executável concluída sem regressões funcionais ou falhas estruturais de acessibilidade.
- Arquivos ou áreas afetadas: `tests/test_frontend.py`, `tests/test_routes.py`, `app/templates/`, `app/static/styles.css`, `compose.yaml`.
- Comportamento anterior: QA-004 aguardava validação independente após a correção de contraste.
- Comportamento novo: 33 testes passaram; estados vazio, atraso, conclusão, formulários, confirmação, seletores, labels, foco declarado, breakpoints e contraste foram verificados; Compose serviu `/` e o CSS responsivo.
- Ação obrigatória do destino: manter os seletores e o contrato ao finalizar a interface; Administração deve providenciar inspeção visual renderizada antes da Fase 5.
- Retorno necessário de: Administração.
- Retorno solicitado: disponibilizar um navegador/renderizador para validar telas grande e pequena ou registrar a aceitação da limitação como decisão explícita.
- Condição de desbloqueio: inspeção visual renderizada sem regressão de layout, rolagem horizontal indevida ou foco/contraste; nenhum defeito funcional permanece aberto.
- Verificação executada: `python3 -m unittest discover -s tests -v` com 33 testes `OK`; `docker compose config`; `docker compose build`; `docker compose up --detach`; `curl` em `/` e `/static/styles.css`; `docker compose down`; verificação de disponibilidade sem Chromium, Selenium ou Playwright.
- Bloqueios: inspeção visual real não executável neste ambiente; a Fase 4 permanece em validação.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

## Definition of Done da sessão

- O escopo da sessão está concluído ou os itens restantes estão registrados.
- Mudanças fora do escopo foram encaminhadas, não absorvidas silenciosamente.
- Handoffs foram criados para todas as sessões afetadas.
- Verificações executadas e seus resultados foram registrados.
- A documentação relacionada foi atualizada quando o comportamento mudou.
- O retorno necessário de outras sessões foi registrado, incluindo origem, pedido e condição de desbloqueio.

### Handoff BE-F4-SPACING-001 - 2026-09-27

- Origem: Backend/Frontend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI
- Alteração: ajustados os respiros (`UI`) do app com tokens de espaçamento (`--space-1` a `--space-6`), mantendo `radius`, cores e sombra.
- Arquivos ou áreas afetadas: `app/static/styles.css`.
- Comportamento anterior: gaps e paddings menores, painel mais compacto, flash-stack com margem negativa.
- Comportamento novo: espaçamentos moderados entre hero, flash, cards (topline, medidor, ações), filtros, formulário e tela de tags; flash-stack sem margem negativa.
- Ação obrigatória do destino: QA-004 validar respiros visuais via roteiro `VALIDACAO-VISUAL-F4.md`; sem impacto de contrato ou teste.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: evidência da inspeção visual local (desktop e mobile).
- Condição de desbloqueio: checklist de respiros aprovado e fase encerrada formalmente.
- Verificação executada: `python3 -m unittest discover -s tests` com 35 testes, resultado `OK`.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

### Handoff BE-F4-DIGEST-001 - 2026-09-27

- Origem: Backend
- Destino: Testes, Administração e Frontend
- Tipo: CONTRATO
- Alteração: adicionado comando CLI `flask --app wsgi send-digest` com env vars de SMTP, e completadas rotas de gerenciamento de tags (`/tags`, rename, delete, merge) com template `tags.html`.
- Arquivos ou áreas afetadas: `app/__init__.py`, `app/digest.py`, `app/config.py`, `app/routes.py`, `app/tasks.py`, `app/templates/tags.html`, `app/templates/base.html`, `app/static/styles.css`.
- Comportamento anterior: sem comando de email; tela/tags sem estilo completo.
- Comportamento novo: `flask send-digest --to EMAIL` envia resumo HTML das tarefas abertas e atrasadas; página `/tags` estilizada com a identidade ICE.
- Ação obrigatória do destino: Testes devem registrar evidência do comando quando SMTP local for configurado; Frontend deve validar `/tags` no roteiro visual.
- Retorno necessário de: Testes e Administração.
- Retorno solicitado: validação da tela `/tags` e do comando com SMTP real ou locally fake.
- Condição de desbloqueio: teste local de email bem-sucedido e inspeção visual de `/tags`.
- Verificação executada: suíte 35 testes OK; sem SMTP configurado o comando falha com mensagem clara; com SMTP de exemplo, tenta conectar (falhou por ausência de servidor local).
- Bloqueios: Fase 5 permanece bloqueada até o encerramento da Fase 4; teste real de email depende de SMTP configurado pelo usuário.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)

### Handoff FE-F4-TAGS-001 - 2026-09-27

- Origem: Frontend/Backend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI
- Alteração: tela `/tags` reestruturada para coluna única (elimina o estouro do contêiner em duas colunas); Excluir agora é disponível para todas as tags, com confirmação e aviso de quantas tarefas serão desvinculadas; contagem de uso exibida com destaque para tags sem uso.
- Arquivos ou áreas afetadas: `app/templates/tags.html`, `app/static/styles.css`, `app/tasks.py` (`delete_tag` desvincula via `task_tags`).
- Comportamento anterior: tabela de tags estourava o card e tinha o botão Excluir cortado; Excluir só aparecia para tags sem tarefa.
- Comportamento novo: layout sem estouro em desktop e mobile; Excluir sempre visível, com confirmação explícita quando a tag está em uso.
- Ação obrigatória do destino: `QA-004` validar `/tags` no roteiro visual (incluindo exclusão de tag em uso); Administração decide se a nova regra de exclusão deve constar no discovery.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: evidência visual e validação da nova regra de exclusão de tags.
- Condição de desbloqueio: checklist visual aprovado e fase encerrada.
- Verificação executada: suíte completa com 38 testes `OK`; `git diff --check` limpo; página `/tags` servida localmente.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff BE-F4-DIGEST-002 - 2026-09-29

- Origem: Backend/Frontend (sessão unificada)
- Destino: Administração
- Tipo: Configuração + Infra
- Alteração: opção de resumo por email integrada a Gmail real: `.env` local com SMTP_* e DIGEST_TO (fora do git, protegido no `.gitignore`), `.env.example` como modelo, `python-dotenv==1.2.1` em `requirements.txt` (CLI Flask carrega o `.env`), `compose.yaml` com `env_file`.
- Domínio/rotas: nenhuma mudança de contrato.
- Verificações executadas: suíte com 43 testes `OK`; `git check-ignore .env` confirma isolamento do segredo; envio real executado com sucesso (`Resumo enviado para ...@gmail.com`).
- Nota de segurança: a senha de app passou pelo chat; recomendado rotacionar em myaccount.google.com/apppasswords quando conveniente.
- Retorno necessário de: Administração.
- Retorno solicitado: decisão sobre agendamento do envio (cron/systemd timer) — fica para depois da inspeção visual da Fase 4.
- Condição de desbloqueio: Fase 5 aguarda apenas a inspeção visual pendente.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff BE-F4-LAUNCHER-001 - 2026-09-29

- Origem: Backend (builtin)
- Destino: Administracao
- Tipo: Infraestrutura local (fora do repositorio)
- Alteracao: lanchador `ice` em `~/.local/bin` (sobe servidor Flask se necessario e abre o navegador), icone `ice-framework.svg` e atalho `ice-framework.desktop` no GNOME; ciclo de vida sob demandado.
- Verificacoes executadas: arranque a frio com `/health` 200; segunda chamada sem duplicar processos; `desktop-file-validate` aprovado.
- Retorno necessario de: Administracao.
- Retorno solicitado: nada pendente; registro para contexto de sessoes futuras.
- Condicao de desbloqueio: n/a (arquivos fora do git, sem impactese no contrato).
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff FE-F4-DYNFILTER-001 - 2026-09-29

- Origem: Frontend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI/Interação
- Alteração: painel de tarefas com modo fixo (`body.panel-mode` no desktop: topbar, hero e filtros estáticos; `.task-area` com scroll próprio e heading fixo no topo; mobile mantém rolagem normal) e filtro dinâmico sem recarregar página (fetch da própria URL + troca das regiões `data-dynamic-region`, indicador discreto de espera, estado de erro orientador, URL compartilhável via `replaceState`, última requisição vale via `AbortController`).
- Contrato HTTP: nenhuma mudança (a troca reutiliza a resposta integral de `GET /`).
- Arquivos ou áreas afetadas: `app/templates/base.html` (bloco `body_class`), `app/templates/index.html` (regiões dinâmicas), `app/static/styles.css` (modo painel + estados de sincronização), `app/static/app.js` (módulo de filtros dinâmicos), `tests/test_frontend.py` (+3 testes).
- Comportamento anterior: página rolava inteira; filtros exigiam clique em "Aplicar filtros" com recarregamento completo.
- Comportamento novo: sem rolagem de página no desktop; qualquer clique/tecla em filtro atualiza a lista imediatamente, sem recarregar.
- Ação obrigatória do destino: `QA-004` incluir na inspeção visual o modo painel (desktop/mobile), a troca dinâmica e o fallback sem JS.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: validação visual do modo painel e do filtro dinâmico no roteiro da Fase 4.
- Condição de desbloqueio: checklist visual aprovado e fase encerrada.
- Verificação executada: suíte completa com 46 testes `OK`; `git diff --check` limpo; HTML servido contém as regiões dinâmicas; servidor reiniciado.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff FE-F4-DYNFILTER-002 - 2026-09-29

- Origem: Frontend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI
- Alteração: botão "Aplicar filtros" removido do fluxo com JS (filtro auto-aplica) e mantido apenas dentro de `<noscript>` como fallback para navegadores sem JavaScript.
- Contrato HTTP: nenhuma mudança.
- Arquivos ou áreas afetadas: `app/templates/index.html`, `tests/test_frontend.py` (teste atualizado: botão aparece exatamente uma vez, dentro de noscript).
- Comportamento anterior: botão visível sempre, duplicando a ação automática.
- Comportamento novo: sem botão visível com JS; `<noscript>` garante aplicação manual sem JavaScript.
- Ação obrigatória do destino: `QA-004` confirmar no roteiro visual a ausência do botão e o funcionamento dos filtros por clique.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: validação visual da remoção do botão.
- Condição de desbloqueio: checklist visual aprovado e fase encerrada.
- Verificação executada: suíte com 46 testes `OK`; `git diff --check` limpo; servidor reiniciado com o template novo.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff FE-F4-FILTERCOMPACT-001 - 2026-09-29

- Origem: Frontend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI
- Alteração: no modo painel, hero e formulário de filtros compactados (padding do hero reduzido, título menor, respiros do formulário menores) e área de tags com limite de altura (8.5rem) com scroll fino apenas quando houver muitas tags.
- Objetivo: painel de filtros sem scroll no uso normal; overflow do painel permanece apenas como segurança.
- Contrato HTTP: nenhuma mudança.
- Arquivos ou áreas afetadas: `app/static/styles.css`, `tests/test_frontend.py` (asserções novas).
- Comportamento anterior: painel de filtros podia rolar para caber tudo.
- Comportamento novo: filtros cabem sem scroll; apenas listas longas de tags rolam dentro do próprio campo.
- Ação obrigatória do destino: `QA-004` confirmar na inspeção visual que o painel dispensa scroll.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: validação visual da compactação.
- Condição de desbloqueio: checklist visual aprovado e fase encerrada.
- Verificação executada: suíte com 46 testes `OK`; `git diff --check` limpo; servidor reiniciado.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff CONTRATO-F4-DIGESTROUTE-001 - 2026-09-29

- Origem: Frontend/Backend (sessão unificada)
- Destino: Administração e Testes
- Tipo: Contrato
- Alteração: rota nova `POST /digest/send` (envio do resumo por email via botão da barra superior, quando SMTP configurado; post/redirect/get 303; flash de sucesso/erro; volta para a tela de origem). `CONTRATO-APLICACAO.md` atualizado na tabela de rotas.
- Retorno necessário de: Administração (ciência da rota nova); Testes (cobertura em `tests/test_routes.py`).
- Condição de desbloqueio: n/a — contrato já atualizado e testado.
- Status: concluído

### Handoff FE-F4-DIGESTBUTTON-001 - 2026-09-29

- Origem: Frontend/Backend (sessão unificada)
- Destino: Testes e Administração
- Tipo: UI/Correção
- Alteração: botão "Enviar resumo" na barra superior (visível apenas com SMTP configurado; "Enviando..." durante o POST); tela de tags em modo painel (cabeçalho fixo, tabela rola no card); painel fixo escopado a desktop >= 801px (correção: estava ativo também no mobile); flashes de erro agora renderizam com estilo próprio (correção: tela de tags nunca exibia flashes); email do resumo redesenhado na identidade ICE com versão texto puro anexada.
- Arquivos ou áreas afetadas: `app/routes.py`, `app/templates/base.html`, `app/templates/tags.html`, `app/templates/index.html`, `app/static/styles.css`, `app/static/app.js`, `app/digest.py`, `tests/test_routes.py`, `tests/test_frontend.py`, `tests/test_digest.py`.
- Verificação executada: suíte completa com 53 testes `OK`; `git diff --check` limpo; servidor reiniciado.
- Ação obrigatória do destino: `QA-004` incluir na inspeção visual o botão, a tela de tags fixa e o email recebido.
- Retorno necessário de: `QA-004` e Administração.
- Retorno solicitado: validação visual e confirmação do email de teste recebido.
- Condição de desbloqueio: checklist visual aprovado e fase encerrada.
- Bloqueios: Fase 5 permanece bloqueada até a inspeção visual.
- Status: concluído (inspeção visual da Fase 4 aprovada em 2026-10-03)


### Handoff ADM-F4-CLOSE-001 - 2026-10-03

- Origem: Administração (retorno do usuário)
- Destino: Todas as sessões
- Tipo: Encerramento de fase
- Alteração: Fase 4 concluída formalmente com base na inspeção visual aprovada pelo usuário, sem problemas encontrados. Retornos pendentes de `FE-001`, `QA-004` e dos handoffs `BE-F4-*`/`FE-F4-*` foram liquidados.
- Verificação registrada: suíte com 53 testes `OK`; envio real de email confirmado; `VALIDACAO-VISUAL-F4.md` marcado como concluído.
- Próximo passo: ativar as sessões da Fase 5 - Integração ponta a ponta (backend, frontend e testes), conforme `Fases-de-Desenvolvimento.md`.
- Condição de desbloqueio: aprovação do usuário para abrir a Fase 5.
- Status: aberto


### Handoff INFRA-MIGRACAO-001 - 2026-10-09

- Origem: Administração/Frontend (sessão unificada)
- Destino: Administração
- Tipo: Infraestrutura (fora do escopo de fase)
- Alteração: instância online do app em Android/Termux acessível por `https://ice.yurilimadev.com`: repo clonado em `~/ice-framework` (venv com gunicorn e tzdata), serviços `ice-framework` e `ice-tunnel` no termux-services, banco copiado do app local via scp (4 tarefas, 4 tags), `.env` no servidor com SECRET_KEY gerado localmente nele, tunnel Cloudflare `ice` com CNAME na zona, acesso SSH por chave (`~/.ssh/ice_termux`, porta 8022) e `termux-wake-lock` ativo.
- Descobertas registradas: Termux sem Docker/systemd/tzdata do sistema (corrigido pelo wheel `tzdata`); o roteiro do drive (`meu-drive`) roda como processo manual e não foi alterado.
- Pendências: Cloudflare Access (email-OTP) a ser ativada pelo usuário no dashboard; verificação ponta a ponta pelo usuário; proteção de bateria do Termux (otimização desativada manualmente no Android).
- Retorno necessário de: Administração (usuário).
- Retorno solicitado: confirmação do Access ativo e do teste por dados móveis.
- Retorno recebido (2026-10-09): Access ativo, testes ponta a ponta aprovados pelo usuário — app no ar.
- Status: concluído


### Handoff CONTRATO-INFRA-PUBLISH-001 - 2026-10-10

- Origem: Administração/Frontend (sessão unificada)
- Destino: Administração e Testes
- Tipo: Contrato
- Alteração: rota nova `POST /publish` (publica o banco local no servidor Termux; post/redirect/get 303; flash de sucesso/erro; disponibilidade da UI depende de `DEPLOY_*`). `CONTRATO-APLICACAO.md` atualizado.
- Retorno necessário de: Administração (ciência); Testes (cobertura em `tests/test_publish.py` e `tests/test_routes.py`).
- Status: concluído

### Handoff INFRA-PUBLISH-001 - 2026-10-10

- Origem: Administração/Frontend (sessão unificada)
- Destino: Administração
- Tipo: Infraestrutura/Produto
- Alteração: sincronização local -> servidor entregue (BACKLOG item 5): CLI `publish` (`app/publish.py`: snapshot por backup API + scp + `sv down/up ice-framework`), botão `Publicar` no topbar do app local (`data-busy-form` genérico também usado pelo Enviar resumo), variáveis `DEPLOY_*` no `.env` local e em `.env.example`; código do servidor sincronizado via `git pull`; `requirements.txt` inalterado (sem novas dependências).
- Verificação executada: suíte com 59 testes `OK`; publicação real com tarefa-teste visível em `https://ice.yurilimadev.com` e remoção confirmada após republicação.
- Regra registrada: local publica, servidor espelha (sobrescrita é esperada).
- Pendência futura: cron de publicação automática (decidir se faz sentido).
- Retorno necessário de: Administração.
- Retorno solicitado: ciência da entrega; nada bloqueante.
- Status: concluído
