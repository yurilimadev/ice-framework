# Validação Visual da Fase 4

**Status:** aberta

Este roteiro orienta a inspeção local da interface antes do encerramento da Fase 4. A validação deve usar o Backend e o banco reais, não dados simulados.

## Acesso local

Execução local:

```bash
python3 -m flask --app wsgi run
```

Abrir no navegador:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/tasks/new`

Alternativa via Compose:

```bash
docker compose up --build
```

Abrir `http://127.0.0.1:8000/`.

## Dados para inspeção

Criar pela interface pelo menos:

- Uma tarefa aberta com score alto e deadline futuro.
- Uma tarefa aberta com deadline passado.
- Uma tarefa concluída.
- Uma tarefa sem deadline.
- Tarefas com tags iguais em grafias diferentes, como `Work` e `work`.

## Viewports

Inspecionar no mínimo:

- Desktop amplo: `1440px`.
- Desktop compacto: `1024px`.
- Tablet: `768px`.
- Celular: `390px`.
- Limite mínimo suportado: `320px`.

## Checklist visual

### Estrutura e identidade

- [ ] Fundo azul-petróleo, superfícies brancas e destaque ciano estão coerentes.
- [ ] Logo facetado e marca permanecem legíveis.
- [ ] Hierarquia de título, score, dimensões ICE e deadline é clara.
- [ ] Espaçamentos, cards, bordas e sombras não prejudicam a leitura.
- [ ] A interface não apresenta rolagem horizontal indevida.

### Lista e estados

- [ ] Lista padrão mostra tarefas abertas ordenadas pelo score.
- [ ] Score e dimensões ICE são visíveis.
- [ ] Tarefa atrasada possui texto e destaque compreensíveis.
- [ ] Tarefa concluída possui indicação textual clara.
- [ ] Estado vazio apresenta ação para criar a primeira tarefa.
- [ ] Filtros de status, atraso, tags e ordenação são compreensíveis.

### Formulário

- [ ] Campos possuem labels visíveis e associados.
- [ ] Impacto, Confiança e Facilidade indicam o intervalo de 1 a 10.
- [ ] Deadline opcional e tags estão explicados.
- [ ] Erros aparecem próximos aos campos e preservam os valores enviados.
- [ ] Foco de teclado é visível.
- [ ] A confirmação de exclusão é clara e não acidental.

### Acessibilidade

- [ ] Navegação por teclado alcança todos os controles.
- [ ] Contraste permanece legível nos estados normal, atrasado e concluído.
- [ ] Status e atraso não dependem somente de cor.
- [ ] O conteúdo continua compreensível com zoom do navegador.
- [ ] Movimento reduzido não quebra a interação.

### Respiros e espaçamentos

- [ ] Hero separa claramente título e lista sem excedente.
- [ ] Aviso efêmero tem respiro próprio e não invasão o hero.
- [ ] Cards de tarefa possuem respiro interno uniforme entre topline, corpo, medidor e ações.
- [ ] Gaps entre cards e blocos de filtros são confortáveis.
- [ ] Formulário separa título, ICE, campos secundários e ações com respiros visíveis.
- [ ] Tela de tags (tabela e mescla) usa a mesma escala de espaçamento do restante do app.
- [ ] Em mobile, respiros entre seções e cards continuam legíveis.

### Avisos efêmeros

- [ ] Mensagem de sucesso aparece após criar, editar, concluir, reabrir ou excluir.
- [ ] Mensagem desaparece automaticamente após aproximadamente 4 segundos.
- [ ] Botão de fechar remove a mensagem imediatamente.
- [ ] Recarregar a página não exibe novamente o aviso anterior.
- [ ] Erros de validação não desaparecem automaticamente.

## Registro da inspeção

```markdown
### Inspeção [ID]

- Data:
- Rota:
- Viewport:
- Cenário:
- Resultado: passou | falhou
- Evidência:
- Sessão responsável:
- Handoff:
```

## Critério de encerramento

A Fase 4 pode ser encerrada quando a inspeção estiver registrada para desktop e celular, não houver falhas críticas abertas e Administração atualizar o status de `FE-001`, `QA-004` e da fase.
