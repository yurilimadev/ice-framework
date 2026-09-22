# Administração de Sessões

Este documento coordena sessões de trabalho especializadas e registra dependências entre elas.

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
- Status: aberto | em validação | concluído
```

## Registro de sessões

| ID | Sessão | Fase | Status | Bloqueio ou próximo passo |
|---|---|---|---|---|
| ADM-001 | Discovery e planejamento | 0 | concluída | Fases 0 e 1 concluídas; Fase 2 em andamento |
| BE-001 | Fundação e domínio | 1 | concluída | Fundação validada; sessão encerrada |
| FE-001 | Interface do MVP | 4 | aguardando | Depende do contrato do backend |
| QA-001 | Estratégia e execução de testes | 1 | concluída | Fundação validada; sessão encerrada |
| BE-002 | Domínio e persistência | 2 | em andamento | Implementar domínio e persistência; retornar schema ao QA-002 |
| QA-002 | Testes do domínio e persistência | 2 | em andamento | Preparar cenários; aguardar schema do Backend para executar |

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
- Status: aberto

## Definition of Done da sessão

- O escopo da sessão está concluído ou os itens restantes estão registrados.
- Mudanças fora do escopo foram encaminhadas, não absorvidas silenciosamente.
- Handoffs foram criados para todas as sessões afetadas.
- Verificações executadas e seus resultados foram registrados.
- A documentação relacionada foi atualizada quando o comportamento mudou.
- O retorno necessário de outras sessões foi registrado, incluindo origem, pedido e condição de desbloqueio.
