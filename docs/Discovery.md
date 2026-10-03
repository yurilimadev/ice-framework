# Discovery

**Status:** Fases 0, 1, 2 e 3 concluídas; Fase 4 em andamento

## Objetivo

Criar uma aplicação web leve e minimalista de lista de tarefas, orientada pelo framework ICE (Impacto, Confiança e Facilidade), com controle rigoroso de deadlines e persistência local portátil.

## Usuário inicial

- Usuário individual.
- Uso local, sem login e sem múltiplas contas.

## Decisões confirmadas

- Backend em Flask.
- Interface em HTML server-side, com CSS leve ou Tailwind.
- Persistência em um único arquivo SQLite.
- Empacotamento com Docker e Docker Compose.
- Pasta do banco montada em volume externo ao container.
- Backup feito com a aplicação parada.
- Restauração feita copiando o volume para outra máquina e executando `docker compose up`.
- O prazo não altera o Score ICE.
- O backup do SQLite é suficiente para o MVP; não haverá exportação adicional para CSV ou JSON.
- O fuso horário será `America/Sao_Paulo`, configurado pelo Docker Compose.
- A tarefa terá somente título no MVP.
- O título terá no máximo 120 caracteres.
- Cada tag terá no máximo 30 caracteres.
- Os filtros serão por status, atraso e tags.
- As ordenações serão por Score ICE, deadline e data de criação.
- Tarefas sem deadline ficarão depois das tarefas com deadline.
- Tarefas concluídas poderão ser reabertas.
- Mudanças futuras do schema usarão `PRAGMA user_version` e scripts SQL.

## Escopo do MVP

- Criar, editar, concluir e excluir tarefas.
- Excluir permanentemente somente após confirmação.
- Informar Impacto, Confiança e Facilidade em escala de 1 a 10.
- Exigir os três valores ICE ao salvar uma tarefa.
- Permitir deadline opcional.
- Permitir deadlines anteriores à data atual.
- Adicionar e reutilizar tags.
- Filtrar e ordenar tarefas.
- Exibir os valores ICE e o score calculado.
- Ocultar tarefas concluídas na lista padrão, mantendo-as disponíveis por filtro.

## Regras de negócio

### Score ICE

```text
Score ICE = Impacto x Confiança x Facilidade
```

- Cada dimensão aceita valores inteiros de 1 a 10.
- O score máximo é 1000.
- Facilidade igual a 10 representa uma tarefa muito fácil.
- O score deve ser recalculado automaticamente quando qualquer dimensão mudar.

### Deadlines

- O deadline representa uma data, sem horário.
- O deadline pode ser vazio.
- Um deadline anterior ao dia atual caracteriza a tarefa como atrasada enquanto ela estiver aberta.
- Tarefas atrasadas devem receber destaque visual e estar disponíveis em um filtro específico.
- O fuso horário usado para definir “hoje” será `America/Sao_Paulo`, configurado pelo Docker Compose.

### Lista padrão

- Exibir tarefas abertas.
- Ordenar primeiro pelo Score ICE, do maior para o menor.
- Em caso de empate, usar o deadline mais próximo.
- Tarefas concluídas ficam fora da lista padrão.

### Filtros e ordenações

- O usuário poderá filtrar por status.
- O usuário poderá filtrar tarefas atrasadas.
- O usuário poderá filtrar por tags.
- O usuário poderá ordenar por Score ICE, deadline ou data de criação.
- Quando houver tarefas sem deadline, elas ficarão depois das tarefas com deadline na ordenação por prazo.

## Restrições arquiteturais

- O banco deve ficar em uma pasta persistente fora do container.
- O volume deve permitir copiar o arquivo ou a pasta de dados para outra máquina.
- A configuração deve permitir subir a mesma instância sem depender de serviços externos.
- O procedimento de backup deve priorizar simplicidade e consistência, exigindo a parada da aplicação durante a cópia.

## Critérios de aceite iniciais

- Não é possível salvar valores ICE fora do intervalo de 1 a 10.
- Alterar qualquer valor ICE atualiza o score automaticamente.
- Uma tarefa aberta com deadline passado é identificada como atrasada.
- Uma tarefa concluída não é tratada como atrasada.
- O usuário consegue visualizar tarefas concluídas por meio de filtro.
- O usuário consegue filtrar tarefas por status, atraso e tags.
- O backup restaurado preserva tarefas, scores, status, deadlines e tags.
- A aplicação funciona usando apenas o container e o arquivo SQLite persistente.

## Decisões encerradas na Fase 0

- O fuso horário não será inferido da máquina hospedeira.
- A descrição ou notas ficam fora do MVP.
- Tarefas concluídas podem retornar ao estado aberta.
- A restauração do volume e a evolução do schema são responsabilidades distintas: o volume preserva a instância e `PRAGMA user_version` controla mudanças estruturais.

## Registro de atividades

### 2026-09-20

- Realizado discovery inicial do produto.
- Definido o usuário inicial como individual e local.
- Escolhidos Flask, HTML server-side, SQLite e Docker Compose.
- Definida a fórmula ICE com escala de 1 a 10.
- Definidas as regras iniciais de deadlines, tarefas atrasadas e backup.
- Registrados os pontos que precisam de decisão antes da implementação.

### 2026-09-20 - Conclusão da Fase 0

- Definidos fuso, filtros, ordenações, limites de texto e comportamento de reabertura.
- Confirmado que o MVP terá somente título, sem descrição ou notas.
- Definida a estratégia de evolução do schema com `PRAGMA user_version` e scripts SQL.
- Fase 0 concluída sem pendências de produto necessárias para iniciar a Fundação.

### 2026-09-21 - Conclusão da Fase 1

- Fundação Flask, SQLite, Docker Compose e volume persistente validados.
- Endpoint `/health` respondeu localmente e no container.
- Schema inicial `1` e execução repetida do banco foram validados.
- Fase 1 concluída; a próxima etapa é implementar o domínio e a persistência das tarefas.

### 2026-09-21 - Início da Fase 2

- Fase 2 autorizada após o push da fundação no commit `179b9f8`.
- `BE-002` e `QA-002` foram acionadas.
- O escopo permanece limitado ao domínio, persistência e testes correspondentes.

### 2026-09-27 - Início da Fase 3

- Fase 2 concluída após 14 testes aprovados e revalidação do schema `2`.
- Criado o `CONTRATO-APLICACAO.md` com rotas, formulários, respostas e contexto dos templates.
- Ativadas as sessões `BE-003`, `FE-002` e `QA-003`.
- A identidade visual permanece reservada para a Fase 4.

### 2026-09-27 - Início da Fase 4

- Fase 3 concluída após revisão do Frontend e aprovação independente de 25 testes.
- Ativadas as sessões `FE-001` e `QA-004`.
- Criado `IDENTIDADE-VISUAL.md` a partir da referência visual fornecida.
- Backend permanece em suporte para regressões ou mudanças de contrato.

### 2026-09-27 - Implementação inicial da Fase 4

- `FE-001` substituiu os templates de fundação pela interface visual responsiva do MVP.
- Adicionados tokens CSS, estados de tarefa, filtros, formulário, mensagens, estado vazio e confirmação de exclusão.
- A suíte completa passou com 33 testes; a validação visual independente permanece com `QA-004`.

### 2026-09-21 - Validação inicial da Fase 2

- Implementados o modelo da tarefa, score ICE derivado, deadlines, atraso, status e tags.
- Definidas a normalização de título e tags, as ordenações determinísticas e o filtro combinado de tags.
- Criada a migração SQLite `002_tasks.sql` com tabelas `tasks`, `tags` e `task_tags`.
- Regras de domínio e persistência foram exercitadas por 11 testes automatizados.
- A revalidação encontrou duas falhas de validação e deduplicação de tags, registradas para o Backend antes do encerramento da fase.

### 2026-09-27 - Conclusão da Fase 2

- `QA-002-F01` e `QA-002-F02` foram corrigidos e revalidados.
- A suíte completa passou com 14 testes.
- O schema `2` foi mantido; nenhuma migração adicional foi necessária.
- Fase 2 concluída e Fase 3 liberada para rotas e contrato de aplicação.

## Documentos relacionados

- `README.md`: roteador da documentação.
- `CONTEXTO-ATUAL.md`: snapshot operacional para continuidade entre sessões.
- `Fases-de-Desenvolvimento.md`: fases, dependências e critérios de avanço.
- `CONTRATO-DOMINIO.md`: campos, regras e operações do domínio validado.
- `CONTRATO-APLICACAO.md`: rotas, formulários, respostas e contexto dos templates.
- `IDENTIDADE-VISUAL.md`: direção visual e limites para a implementação do Frontend.
- `sessoes/Administracao-de-Sessoes.md`: responsabilidades, handoffs e registro das sessões.
- `sessoes/Sessao-Backend.md`: atividades e limites da sessão de backend.
- `sessoes/Sessao-Frontend.md`: atividades e limites da sessão de frontend.
- `sessoes/Sessao-Testes.md`: estratégia, cenários e encaminhamento de falhas.
