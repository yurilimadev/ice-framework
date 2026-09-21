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

### Backend-04 - Rotas e contrato

- Publicar rotas e métodos usados pelo frontend.
- Validar entradas no servidor.
- Retornar mensagens compreensíveis para erros de validação.
- Entregar ao template todos os dados necessários para score, atraso, filtros e estados.
- Registrar qualquer alteração de campo ou rota como handoff `CONTRATO`.

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

## Checklist de encerramento

- [ ] Regras do `../Discovery.md` foram respeitadas.
- [ ] Não há score calculado com valores inválidos.
- [ ] O backend não depende de lógica exclusiva do frontend.
- [ ] Alterações de contrato foram comunicadas.
- [ ] Docker e volume persistente foram verificados.
- [ ] Backup e restauração foram encaminhados para validação.
