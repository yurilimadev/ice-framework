# Identidade Visual ICE

**Status:** referência ativa da Fase 4

Esta orientação registra a referência visual fornecida para a aplicação. Ela orienta o Frontend sem alterar o contrato do domínio ou da aplicação.

## Direção visual

- Remeter visualmente a gelo, gelo marinho e superfícies frias.
- Usar uma composição minimalista, clara e espaçada.
- Priorizar legibilidade e foco na lista de tarefas.
- Manter a interface limpa, sem excesso de ornamentos ou efeitos.

## Paleta semântica

- Fundo principal: azul-petróleo escuro.
- Superfícies de conteúdo: branco.
- Destaque e ação primária: azul-ciano vibrante.
- Marca e textos de maior destaque: azul-marinho profundo.
- Ícones e textos auxiliares: preto ou azul muito escuro.

Os valores exatos de cor devem ser definidos pelo Frontend a partir da referência visual e registrados nos tokens CSS antes da conclusão da Fase 4.

## Marca e composição

- O logo deve preservar a ideia de uma forma facetada semelhante a um bloco de gelo.
- A barra superior deve comportar a marca e as ações globais.
- A navegação secundária deve separar a criação de tarefas das ações auxiliares.
- A área principal deve usar uma superfície branca destacada sobre o fundo azul-petróleo.
- Cards e painéis podem usar cantos arredondados e sombra discreta.
- Ícones devem ser simples e consistentes, sem competir com os dados da tarefa.

## Tipografia e interação

- Usar uma família sans-serif limpa e legível.
- Manter hierarquia visual clara entre título, score, dimensões ICE e deadline.
- Estados de atraso e conclusão não podem depender somente de cor.
- Foco de teclado, contraste e labels devem permanecer visíveis.
- A composição deve se adaptar a telas menores sem exigir rolagem horizontal da lista.

## Limites da referência

- Esta identidade não altera nomes de rotas, campos ou contexto definidos em `CONTRATO-APLICACAO.md`.
- O Backend não deve incorporar CSS, layout ou decisões visuais.
- Alterações que afetem seletores ou significado de estados exigem retorno para Testes.
- Logo, família tipográfica e valores exatos da paleta devem ser confirmados pelo Frontend antes do encerramento da Fase 4.
