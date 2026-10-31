# Validacao E2E da Fase 5

**Status:** executada em 2026-10-31 — **aguardando aceite do usuario**

Backend real (Flask + SQLite da instancia local). Cada bloco foi exercitado por HTTP real contra `http://127.0.0.1:5000`. A evidencia de publicacao ponta a ponta (criar -> publicar -> conferir no servidor) ja registrada em `INFRA-PUBLISH-001` (2026-10-10).

## Bloco A - Ciclo completo do card (aprovado)

- Criar (ICE 8/7/6): 303; card com score 336 renderizado (id 7).
- Editar ICE 9/3/4: 303; recalculo para 108 renderizado no painel.
- Concluir: 303; aparece em `status=completed`; reabrir: 303; volta para abertas.
- Excluir: 303; ausente em `status=all` (0 ocorrencias).

## Bloco B - Prazo passado e filtro atrasadas (aprovado)

- Criar com deadline de ontem: 303.
- `/?status=open&overdue=1`: aparece + marcador `data-overdue`.
- Nota de contrato: sem o filtro overdue, a atrasada tambem aparece no listado de abertas (o filtro restringe; comportamento contratado, nao divergencia).
- Excluir: 303; limpa.

## Bloco C - Tags: filtrar, mesclar, excluir (aprovado apos correcao)

**Achado BE-F5-001 (defeito real da fase):** `POST /tags/merge` retornou 500 quando a tarefa ja tinha AS DUAS tags (origem e destino): `IntegrityError UNIQUE (task_id, tag_id)` no UPDATE de `merge_tags`. Correcao aplicada: conflitos removidos antes do UPDATE; regressao `test_merge_com_tags_compartilhadas_na_mesma_task_nao_duplica` na suite.
**Revalidacao:** tarefa com 2 tags -> mesclar -> 303; card fica com um unico chip (0 ocorrencias da origem); uso do destino = 1 tarefa; exclusoes limpam tudo (0 residuo).

## Bloco D - Ordenacoes (aprovado)

- `order=score`: scores [400, 350, 250] - desc OK.
- `order=deadline`: cards com prazo antes dos "Sem deadline" - OK.
- `order=created_at`: ids em insercao decrescente - OK.

## Bloco E - Persistencia e reciclagem (aprovado)

- Reinicio do servidor: `/health` 200 (schema 2); 3 abertas antes e depois; hash dos titulos identico.
- Suite completa: **60 testes OK** (59 + regressao de mescla).

## Pendencia fora do escopo da fase (infra)

No fechamento (2026-10-31), o Android estava fora da rede (`ice.yurilimadev.com` respondendo 530; sem SSH nos IPs). A disponibilidade do servidor online e um topico de infraestrutura monitorado fora desta fase; sincronizacao de dados nao dependente aqui.

## Conclusao

5/5 blocos aprovados, 1 achado corrigido e reverificado. Aceite do usuario pendente para encerramento formal da Fase 5.
