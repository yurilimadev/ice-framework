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
