# Sessão de Backend

## Missão

Implementar o domínio, a persistência e os fluxos Flask que sustentam a lista de tarefas, mantendo as regras de negócio em um único lugar.

## Escopo da sessão

- Estrutura executável do Flask.
- Configuração da aplicação e do fuso horário.
- Conexão e persistência SQLite.
- Modelo e operações da tarefa.
- Score ICE e validações.
- Deadlines, atraso e status.
- Tags, filtros e ordenações.
- Rotas, mensagens e contexto entregue aos templates.
- Dockerfile, Compose, volume e operação do banco.
- Procedimento técnico de backup e restauração.

## Fora do escopo direto

- Definir aparência final ou estilos da interface.
- Duplicar no JavaScript regras que pertencem ao domínio.
- Alterar testes para fazer uma implementação incorreta passar.
- Adicionar autenticação ou funcionalidades não previstas no discovery sem decisão registrada.

## Retorno necessário

- **De:** Administração.
- **Retorno solicitado:** confirmação do início da Fase 2 e do escopo de domínio aprovado.
- **De:** Testes.
- **Retorno solicitado:** cenários prioritários para score, validação, deadlines, status, tags e persistência.
- **Condição para continuar:** escopo e cenários registrados nos handoffs `BE-002` e `QA-002`.

### Retornos recebidos para a Fase 2

- Administração confirmou o início da Fase 2 e o uso do escopo fechado no `Discovery.md`.
- Testes priorizou limites ICE, deadline ausente/atual/futuro/passado, atraso por status, reabertura, tags, filtros, ordenações e persistência após nova instância.
- Os retornos foram registrados nos handoffs `ADM-F2-001` e `QA-002`.

### Retorno ao QA-002 após as correções

- `QA-002-F01`: `normalize_tags` agora rejeita tipos não iteráveis com `ValidationError` controlado e preserva `None`, strings e iteráveis de strings.
- `QA-002-F02`: a busca persistida de tags usa `casefold()`; `Straße` e `STRASSE` reutilizam a primeira linha e a primeira grafia, sem alteração do schema `2`.
- Arquivo alterado: `app/tasks.py`.
- Testes focados: passaram.
- Suíte completa: `python3 -m unittest discover -s tests -v`, 14 testes, `OK`.
- Banco novo e banco existente: schema `2` validado; nenhuma migração nova foi necessária.

## Atividades

### Backend-01 - Fundação

- Criar a estrutura mínima da aplicação.
- Configurar dependências somente após confirmar o gerenciador escolhido.
- Configurar execução local e em container.
- Definir o caminho configurável do SQLite.
- Montar a pasta de dados como volume persistente.
- Registrar variáveis de ambiente necessárias.

### Backend-02 - Domínio da tarefa

- Definir os campos da tarefa conforme o `../Discovery.md`.
- Validar Impacto, Confiança e Facilidade entre 1 e 10.
- Calcular o Score ICE no backend.
- Representar deadline vazio e deadline passado sem perder informação.
- Definir claramente quando uma tarefa é considerada atrasada.
- Implementar os estados aberta e concluída.

### Backend-03 - Persistência

- Implementar criação, leitura, atualização, conclusão e exclusão.
- Persistir tags sem duplicação indevida.
- Implementar filtros e ordenações confirmados.
- Definir o desempate de tarefas sem deadline.
- Definir e registrar a estratégia de evolução do schema SQLite antes da primeira mudança estrutural.

### Backend-03A - Correções bloqueadoras da Fase 2

Resolver os handoffs `QA-002-F01` e `QA-002-F02` antes de qualquer atividade da Fase 3.

- Fazer `normalize_tags` rejeitar tipos não iteráveis com erro de validação controlado, sem expor `TypeError` de implementação.
- Preservar a validação esperada para `None`, strings e iteráveis de strings conforme o contrato do domínio.
- Corrigir a deduplicação persistida para equivalências Unicode tratadas por `casefold`, incluindo `Straße` e `STRASSE`.
- Preservar a primeira grafia da tag ao reutilizar uma tag equivalente.
- Se a correção exigir mudança de schema, criar migração sequencial, reproduzível e compatível com bancos existentes.
- Não alterar rotas HTTP, templates ou frontend nesta atribuição.
- Executar os testes focados e encaminhar o resultado para `QA-002`.

**Retorno necessário:**

- **Para:** `QA-002`.
- **Retorno solicitado:** informar arquivos alterados, estratégia de normalização/unicidade e resultado dos testes focados.
- **Para:** Administração.
- **Retorno solicitado:** indicar se houve mudança de schema, novo número de versão e qualquer bloqueio restante.
- **Condição de conclusão:** `QA-002-F01` e `QA-002-F02` revalidados com sucesso e suíte completa aprovada.

### Backend-04 - Rotas e contrato

- Publicar rotas e métodos usados pelo frontend.
- Validar entradas no servidor.
- Retornar mensagens compreensíveis para erros de validação.
- Entregar ao template todos os dados necessários para score, atraso, filtros e estados.
- Registrar qualquer alteração de campo ou rota como handoff `CONTRATO`.

### Backend-04A - Implementação do contrato da aplicação

- Implementar somente as rotas definidas em `../CONTRATO-APLICACAO.md`.
- Implementar listagem, criação, edição, conclusão, reabertura e exclusão.
- Adaptar formulários HTML para os tipos aceitos pelo `TaskRepository`.
- Transformar `ValidationError` em erros de formulário sem expor exceções internas.
- Preservar filtros, ordenações, score, atraso e normalização de tags do domínio.
- Entregar aos templates o contexto definido no contrato.
- Criar ou atualizar testes HTTP sem alterar a regra do domínio.
- Informar qualquer divergência ao Frontend, Testes e Administração como `CONTRATO`.

**Retorno necessário:**

- **Para:** `FE-002`.
- **Retorno solicitado:** rotas implementadas, campos do formulário, contexto dos templates e mensagens disponíveis.
- **Para:** `QA-003`.
- **Retorno solicitado:** métodos, status esperados, redirecionamentos e cenários de erro.
- **Condição de conclusão:** contrato implementado e validado por Frontend e Testes.

## Suporte à Fase 4

- Não iniciar novas regras de domínio ou rotas sem uma necessidade registrada.
- Responder a regressões de contrato encontradas pelo `FE-001` ou `QA-004`.
- Preservar os nomes de campos, status, respostas e contexto validados na Fase 3.
- Registrar qualquer alteração necessária como handoff `CONTRATO` para Frontend e Testes.

**Retorno necessário:**

- **De:** `FE-001` e `QA-004`.
- **Retorno solicitado:** divergências de contrato, erros de integração ou falhas que exijam alteração no Backend.
- **Condição para continuar:** atender somente correções confirmadas e devolver nova evidência às sessões afetadas.

### Retorno BE-003 inicial

- Rotas implementadas conforme `../CONTRATO-APLICACAO.md`: listagem, criação, edição, conclusão, reabertura, exclusão e `/health`.
- Formulários convertem ICE, deadline e tags antes de chamar o domínio; erros retornam `400` com valores e mapa `errors` preservados.
- Templates mínimos foram colocados em `app/templates/` somente para executar o contrato; identidade visual permanece com o Frontend.
- Testes HTTP: 11; suíte completa: 25 testes, resultado `OK`.
- Container validado com `/health` e `/` respondendo; schema `2` preservado.
- Próximo retorno: FE-002 deve revisar campos/contexto e QA-003 deve executar a matriz HTTP independente.

### Backend-05 - Operação e portabilidade

- Configurar Dockerfile e Compose.
- Garantir que o banco não seja perdido ao recriar o container.
- Documentar o procedimento de parada, cópia e restauração.
- Validar a instância restaurada com a sessão de testes.

## Handoffs obrigatórios

- Mudou regra de score, deadline, status, filtro ou ordenação: informar frontend e testes.
- Mudou campo, rota, método, validação ou contexto de template: informar frontend e testes.
- Mudou schema ou caminho do banco: informar testes e administração; informar frontend se houver impacto nos dados exibidos.
- Mudou variável de ambiente, Compose ou volume: informar testes e registrar impacto operacional.
- Encontrou defeito visual: encaminhar para frontend, sem corrigir estilos nesta sessão.

## Saída esperada

- Backend executável e persistente.
- Contrato de rotas e dados documentado.
- Regras de negócio cobertas por testes ou encaminhadas para a sessão de testes.
- Handoffs registrados no formato de `Administracao-de-Sessoes.md`.
- Retornos necessários de Administração e Testes registrados.

## Checklist de encerramento

- [ ] Regras do `../Discovery.md` foram respeitadas.
- [ ] Não há score calculado com valores inválidos.
- [ ] O backend não depende de lógica exclusiva do frontend.
- [ ] Alterações de contrato foram comunicadas.
- [ ] Docker e volume persistente foram verificados.
- [ ] Backup e restauração foram encaminhados para validação.
- [x] `QA-002-F01` foi corrigido e revalidado.
- [x] `QA-002-F02` foi corrigido e revalidado.
- [x] Qualquer migração nova foi testada em banco novo e banco existente.
- [x] O retorno para Testes e Administração foi registrado.
