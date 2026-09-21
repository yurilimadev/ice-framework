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
- Verificação executada:
- Bloqueios:
- Status: aberto | em validação | concluído
```

## Registro de sessões

| ID | Sessão | Fase | Status | Bloqueio ou próximo passo |
|---|---|---|---|---|
| ADM-001 | Discovery e planejamento | 0 | concluída | Fase 0 concluída; iniciar Fundação quando autorizado |
| BE-001 | Fundação e domínio | 1-3 | próxima | Aguardar início explícito da Fase 1 |
| FE-001 | Interface do MVP | 4 | aguardando | Depende do contrato do backend |
| QA-001 | Estratégia e execução de testes | 2-7 | aguardando | Depende da primeira superfície executável |

## Definition of Done da sessão

- O escopo da sessão está concluído ou os itens restantes estão registrados.
- Mudanças fora do escopo foram encaminhadas, não absorvidas silenciosamente.
- Handoffs foram criados para todas as sessões afetadas.
- Verificações executadas e seus resultados foram registrados.
- A documentação relacionada foi atualizada quando o comportamento mudou.
