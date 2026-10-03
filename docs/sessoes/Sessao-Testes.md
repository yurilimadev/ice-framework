# Sessão de Testes

## Missão

Provar que o comportamento implementado corresponde ao `../Discovery.md`, identificar regressões e encaminhar cada falha para a sessão responsável.

## Escopo da sessão

- Estratégia de testes.
- Testes unitários das regras de negócio.
- Testes de persistência e rotas.
- Testes de integração com os templates.
- Testes dos fluxos principais da interface.
- Fixtures e dados de teste.
- Testes de Docker, volume, backup e restauração.
- Registro de evidências, falhas e handoffs.

## Fora do escopo direto

- Alterar a regra esperada para acomodar uma implementação sem decisão.
- Corrigir lógica de backend ou layout de frontend sem encaminhamento.
- Considerar um teste verde como prova suficiente quando o cenário de aceite não foi exercitado.

## Retorno necessário

- **De:** Backend.
- **Retorno solicitado:** schema de tarefas, regras implementadas e contrato das rotas ou serviços a validar.
- **De:** Frontend.
- **Retorno solicitado:** fluxos, seletores e estados visuais disponíveis para os testes de interface.
- **De:** Administração.
- **Retorno solicitado:** confirmação da fase ativa, critérios de aceite e prioridade dos cenários.
- **Condição para continuar:** receber o contrato ou a superfície executável correspondente à fase atual.

## Atividades

### Testes-01 - Matriz de comportamento

- Transformar cada critério de aceite em pelo menos um cenário verificável.
- Cobrir caminho feliz, entradas inválidas e estados vazios.
- Registrar dependências de ambiente ou serviços necessários.
- Não inventar comandos de teste antes da configuração do projeto existir.

### Testes-02 - Score ICE

- Testar valores mínimos `1 x 1 x 1`.
- Testar valores máximos `10 x 10 x 10`.
- Testar valores fora do intervalo.
- Testar recálculo após edição de cada dimensão.
- Testar empate e ordenação por score.

### Testes-03 - Deadlines e fuso

- Testar deadline ausente.
- Testar deadline futuro.
- Testar deadline igual ao dia atual.
- Testar deadline passado.
- Testar tarefa concluída com deadline passado.
- Testar comportamento no fuso configurado.
- Testar tarefas sem deadline no desempate definido.

### Testes-04 - Ciclo da tarefa

- Criar tarefa válida.
- Rejeitar tarefa inválida.
- Editar título, ICE, deadline e tags.
- Concluir tarefa e verificar sua saída da lista padrão.
- Filtrar tarefas concluídas, atrasadas e por tags.
- Confirmar exclusão permanente.

### Testes-05 - Persistência e integração

- Verificar dados após reiniciar a aplicação.
- Verificar que score e atraso são reconstruídos corretamente.
- Verificar que filtros não alteram dados persistidos.
- Verificar respostas de validação no frontend.
- Verificar que a interface não usa dados falsos para esconder falhas do backend.

### Testes-06 - Docker, backup e restauração

- Subir a aplicação usando o Compose.
- Criar dados de teste no volume persistente.
- Parar a aplicação antes da cópia.
- Restaurar o volume em uma instância limpa.
- Confirmar tarefas, tags, status, deadlines e scores após a restauração.
- Registrar os comandos reais utilizados.

### Testes-07 - Revalidação das correções da Fase 2

Validar os handoffs `QA-002-F01` e `QA-002-F02` após a correção do Backend.

- Manter o teste de `tags=123` e confirmar `ValidationError`, sem `TypeError` não tratado.
- Verificar `None`, string e iterável de strings conforme o contrato de normalização de tags.
- Reexecutar o caso de equivalência Unicode usando `Straße` e `STRASSE`.
- Confirmar que as tags equivalentes ocupam uma única linha persistida.
- Confirmar que a primeira grafia registrada continua preservada.
- Se houver nova migração, validar banco novo e upgrade de banco existente a partir do schema anterior.
- Executar novamente os testes focados e, depois, a suíte completa.
- Atualizar os handoffs com evidências, resultado e status de cada falha.

**Retorno necessário:**

- **De:** `BE-002`.
- **Retorno solicitado:** correção implementada, arquivos alterados e estratégia de schema/normalização usada.
- **Para:** Administração.
- **Retorno solicitado:** resultado da revalidação e indicação explícita sobre a liberação ou permanência do bloqueio da Fase 3.
- **Condição de conclusão:** ambos os testes de regressão passam e a suíte completa não apresenta falhas relacionadas à Fase 2.

### Testes-08 - Contrato de aplicação da Fase 3

- Criar a matriz HTTP a partir de `../CONTRATO-APLICACAO.md`.
- Validar métodos, rotas, status `200`, `303`, `400` e `404` previstos.
- Validar criação e edição com preservação dos valores do formulário em erro.
- Validar listagem padrão, filtros, tags repetidas e ordenações.
- Validar conclusão, reabertura e exclusão por `POST`.
- Confirmar que score, atraso e normalização de tags continuam derivados pelo domínio.
- Validar o contexto entregue aos templates sem depender de dados falsos.
- Encaminhar divergências de campos, rotas ou respostas como `CONTRATO`.

**Retorno necessário:**

- **De:** `BE-003`.
- **Retorno solicitado:** rotas implementadas e superfície HTTP disponível para teste.
- **De:** `FE-002`.
- **Retorno solicitado:** fluxos e campos que precisam de cobertura no contexto dos templates.
- **Para:** Administração.
- **Retorno solicitado:** cobertura, falhas e decisão sobre a liberação da Fase 4.
- **Condição de conclusão:** matriz HTTP aprovada e handoff para a Fase 4 registrado.

### Testes-09 - Interface e integração inicial da Fase 4

- Validar os fluxos reais da interface implementada pelo `FE-001`.
- Confirmar que criação, edição, conclusão, reabertura, exclusão e filtros continuam usando o Backend real.
- Validar estados vazios, mensagens, confirmação de exclusão e preservação de erros.
- Verificar responsividade sem rolagem horizontal indevida.
- Verificar labels, foco, contraste e que status ou atraso não dependem somente de cor.
- Confirmar que os seletores definidos no contrato e no handoff `FE-002` permanecem disponíveis.
- Encaminhar regressões de contrato para Backend e falhas de interface para Frontend.
- Não encerrar a Fase 4 enquanto a validação visual e funcional não estiver registrada.
- Usar `../VALIDACAO-VISUAL-F4.md` para registrar a inspeção local em desktop e mobile.

**Retorno necessário:**

- **De:** `FE-001`.
- **Retorno solicitado:** telas e fluxos implementados, seletores estáveis e estados visuais disponíveis.
- **De:** Administração.
- **Retorno solicitado:** critérios de aceite da Fase 4 e confirmação da identidade visual de referência.
- **Para:** Administração.
- **Retorno solicitado:** cobertura, falhas, evidências e decisão sobre a liberação da Fase 5.
- **De:** Administração.
- **Retorno solicitado:** confirmação das viewports e cenários que precisam de evidência local.
- **Condição de conclusão:** fluxos principais, responsividade e acessibilidade aprovados.

### Superfície recebida do BE-003

- Rotas publicadas conforme `../CONTRATO-APLICACAO.md`, incluindo métodos, redirecionamentos e respostas de validação.
- Templates mínimos disponíveis em `app/templates/` para permitir testes HTTP; a validação visual final permanece fora desta fase.
- Testes HTTP do Backend: 11; suíte completa atual: 35 testes, resultado `OK`.
- QA-003 deve repetir a matriz de métodos, status `200`, `303`, `400`, `404`, filtros, contexto e persistência sem assumir os testes do Backend como evidência final.

### Matriz executada - Contrato de aplicação (QA-003)

| Cenário | Resultado | Evidência |
|---|---|---|
| Rotas de leitura `/`, `/tasks/new` e edição | Passou | HTTP `200` e HTML com dados reais |
| Criação e edição por `POST` | Passou | HTTP `303` conforme Post/Redirect/Get |
| Conclusão, reabertura e exclusão | Passou | HTTP `303` e estado persistido |
| Formulário inválido na criação | Passou | HTTP `400`, erros por campo e valores preservados |
| Formulário inválido na edição | Passou | HTTP `400`, tarefa persistida não foi alterada |
| Filtros inválidos | Passou | HTTP `400` sem exceção não tratada |
| Tarefa inexistente | Passou | HTTP `404` em edição, atualização, conclusão, reabertura e exclusão |
| Filtro padrão e status concluído | Passou | Concluídas fora da lista padrão e disponíveis por filtro |
| Filtro de atraso | Passou | Apenas tarefa aberta atrasada retornada |
| Filtro por tags repetidas | Passou | Todas as tags informadas exigidas |
| Ordenações por deadline e criação | Passou | Parâmetros aceitos e resultados HTML retornados |
| Persistência após nova instância | Passou | Título, score, tags e status recuperados |

Testes HTTP: `python3 -m unittest tests.test_routes -v`, 11 testes, `OK`.
Suíte completa: `python3 -m unittest discover -s tests -v`, 25 testes, `OK`.

## Matriz executada - Fundação (Fase 1)

| Cenário | Resultado | Evidência |
|---|---|---|
| Carregar as rotas Flask localmente | Passou | `GET /health` é publicado |
| Consultar `/health` em banco isolado | Passou | HTTP 200, banco `ok`, schema `1` |
| Inicializar novamente o mesmo SQLite | Passou | Schema permaneceu em `1` |
| Criar banco em caminho configurável | Passou | Diretórios intermediários e arquivo foram criados |
| Rejeitar fuso horário inválido | Passou | `RuntimeError` foi levantado |
| Resolver a configuração do Compose | Passou | Bind mount, portas e variáveis conferidos |
| Construir e iniciar o container | Passou | Container `web` iniciou e respondeu em `8000` |
| Recriar o container com o volume persistente | Passou | `/app/data/app.sqlite3` e schema `1` permaneceram disponíveis |
| Backup/restauração com tarefas reais | Bloqueado | Schema de tarefas ainda não implementado |

Testes automatizados executados: `python3 -m unittest discover -s tests -v`.

## Matriz executada - Domínio e persistência (Fase 2)

| Cenário | Resultado | Evidência |
|---|---|---|
| Score mínimo e máximo | Passou | `1 x 1 x 1` e `10 x 10 x 10` |
| Valores ICE inválidos | Passou | Valores fora de `1..10`, booleano, decimal e texto rejeitados |
| Título e tags inválidos | Passou | Título vazio/longo e tag acima de 30 caracteres rejeitados |
| Recálculo após edição ICE | Passou | Score reconstruído pela tarefa atualizada |
| Deadline e atraso por status | Passou | Passado atrasado, data atual não atrasada, concluída não atrasada |
| Ciclo aberta/concluída/reaberta/excluída | Passou | Operações do `TaskRepository` |
| Filtros e ordenações | Passou | Status, atraso, tags, score e deadline |
| Reutilização de tags | Passou | Uma linha para tags equivalentes sem diferenciar caixa |
| Persistência após nova instância | Passou | Dados, score derivado e tags recuperados do SQLite |

### Revalidação QA-002 - casos-limite

| Cenário | Resultado | Evidência |
|---|---|---|
| Tipo não iterável em tags | Falhou | `normalize_tags(123)` levanta `TypeError`, não `ValidationError` |
| Tags Unicode equivalentes | Falhou | `Straße` e `STRASSE` geram duas linhas em `tags` |

As duas falhas foram encaminhadas ao Backend como `QA-002-F01` e `QA-002-F02`.

### Revalidação QA-002 - correções do Backend

| Cenário | Resultado | Evidência |
|---|---|---|
| Tipo não iterável em tags | Revalidado | `normalize_tags(123)` retorna `ValidationError` controlado |
| `None`, string e iterável de strings | Revalidado | Normalização preservada conforme o contrato |
| Tags Unicode equivalentes | Revalidado | `Straße` e `STRASSE` compartilham uma linha persistida |
| Primeira grafia da tag | Revalidado | A segunda tarefa recupera `Straße` |
| Banco novo e banco existente | Revalidado | Schema `2` preservado; nenhuma migração adicional necessária |

O Backend corrigiu os dois defeitos em `app/tasks.py`, mantendo o schema `2`.
Os testes focados e a suíte completa passaram: `14` testes, resultado `OK`.

Revalidação independente em 2026-09-27:

- Testes focados de normalização e reutilização Unicode: `3`, resultado `OK`.
- Suíte completa: `python3 -m unittest discover -s tests -v`, `14`, resultado `OK`.
- Banco novo e upgrade de schema `1` para `2`: passaram.
- Compose: configuração, build, subida e `/health` com schema `2`: passaram.
- Decisão: Fase 2 validada; Fase 3 liberada.

### Superfície recebida do FE-001

- A interface final inicial está em `app/templates/` e `app/static/styles.css`, seguindo `IDENTIDADE-VISUAL.md`.
- Os seletores do contrato foram preservados: `data-task-id`, `data-task-status`, `data-overdue`, `data-empty`, `data-error-field` e `data-message`.
- QA-004 deve validar em telas grandes e pequenas: contraste, foco, labels, responsividade, estado vazio, atraso, conclusão, confirmação de exclusão e preservação dos fluxos HTTP.
- A validação visual não foi inferida pelos 33 testes automatizados; permanece como etapa independente.

### Matriz executada - Interface e integração inicial (QA-004)

| Cenário | Resultado | Evidência |
|---|---|---|
| Estrutura base, idioma, viewport e skip link | Passou | HTML com `lang`, `viewport`, `main-content` e link de salto |
| Estado vazio e criação da primeira tarefa | Passou | `data-empty` e ação para `/tasks/new` |
| Labels associados aos campos do formulário | Passou | Campos `title`, ICE, deadline e tags possuem `label for` |
| Estados aberto, atrasado e concluído | Passou | Texto semântico e seletores `data-task-status`/`data-overdue` |
| Seletores de contrato e confirmação de exclusão | Passou | Seletores preservados e `window.confirm` presente |
| Responsividade e foco | Passou | Breakpoints 800/520, `:focus-visible` e redução de movimento |
| Contraste do texto auxiliar `--muted` | Corrigido | `#536e73` sobre branco: `5,46:1` |
| Contraste do status concluído | Corrigido | `#52706f` sobre branco: `5,38:1` |

Testes de interface: `python3 -m unittest tests.test_frontend -v`, 5 testes,
passaram após a correção. Suíte completa: 33 testes, resultado `OK`. O Compose
construiu e serviu `/` e `/static/styles.css` com sucesso.

`QA-004-F01` foi corrigido e revalidado; a validação independente dos demais
cenários visuais permanece com o `QA-004`.

### Revalidação independente QA-004-R1

- Suíte completa: `python3 -m unittest discover -s tests -v`, 33 testes, `OK`.
- Fluxos funcionais, estados, seletores, labels, foco declarado, responsividade
  por breakpoints e contraste foram aprovados.
- Compose: configuração, build, página `/` e `styles.css` responsivo servidos
  com sucesso; o container foi encerrado após a verificação.
- Não há Chromium, Selenium ou Playwright disponíveis neste ambiente. A
  inspeção visual renderizada em telas grande e pequena não foi possível e
  permanece como limitação explícita, não como aprovação presumida.
- Decisão: não há falha funcional ou de acessibilidade estrutural aberta; a
  Fase 4 aguarda somente inspeção visual renderizada antes da liberação da Fase 5.

## Classificação de falhas

- `BACKEND`: regra, validação, persistência, rota ou resposta incorreta.
- `FRONTEND`: layout, interação, acessibilidade ou consumo incorreto do contrato.
- `CONTRATO`: backend e frontend discordam sobre campos, rotas ou respostas.
- `INFRA`: Docker, volume, ambiente ou backup falha.
- `TESTE`: fixture, seletor ou expectativa do próprio teste está incorreta.

## Handoffs obrigatórios

- Falha de regra ou persistência: encaminhar para backend com reprodução mínima.
- Falha de layout ou interação: encaminhar para frontend com cenário e evidência.
- Divergência entre rota e consumo: informar backend e frontend.
- Mudança de contrato recebida: atualizar fixtures e testes afetados antes de validar novamente.
- Falha de infraestrutura: informar backend e administração, incluindo ambiente e passos usados.

## Modelo de evidência

```markdown
### Falha [ID]

- Data:
- Classificação: BACKEND | FRONTEND | CONTRATO | INFRA | TESTE
- Cenário:
- Pré-condições:
- Passos:
- Resultado esperado:
- Resultado obtido:
- Evidência:
- Sessão responsável:
- Handoff:
- Status: aberta | corrigida | revalidada
```

## Saída esperada

- Matriz de cenários atualizada.
- Testes executáveis e reprodutíveis quando a infraestrutura estiver configurada.
- Falhas classificadas e encaminhadas.
- Evidência de backup e restauração.
- Relatório final sem falhas críticas abertas.

## Checklist de encerramento

- [ ] Regras ICE foram cobertas nos limites e fora dos limites.
- [ ] Deadlines, atrasos, fuso e tarefas sem prazo foram verificados.
- [ ] O ciclo completo da tarefa foi verificado.
- [ ] Persistência após reinício foi verificada.
- [ ] Backup e restauração foram verificados.
- [ ] Toda falha aberta tem classificação e sessão responsável.
- [ ] Retornos necessários de Backend, Frontend e Administração foram registrados.
- [x] `QA-002-F01` foi revalidado após a correção.
- [x] `QA-002-F02` foi revalidado após a correção.
- [x] A suíte completa foi executada após os testes focados.
- [x] A Administração recebeu a decisão sobre o desbloqueio da Fase 3.
