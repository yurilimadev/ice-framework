# Validacao de endurecimento da Fase 6

**Status:** executada em 2026-10-31 (mesma sessao da Fase 5) — **aguardando aceite do usuario**

Suité completa: **60 testes OK**. Sondagens por HTTP real contra a instancia local.

## Limites do score ICE (aprovado)

- Card 1/1/1: 303, renderizado com score 1.
- Card 10/10/10: 303, renderizado em `status=open`.
- Ambos excluidos ao final (0 residuo; dados reais intactos: 400/350/250).

## Valores invalidos devolvem 400 com mensagem no campo (aprovado)

- impact=11: 400 + erro associado ao campo Impacto.
- deadline "31-02-2026" (formato invalido): 400.
- titulo em branco ("   "): 400.
- tag com 31 caracteres: 400.
- filtro `?status=banana`: 400.

## Regras de aceite verificadas (aprovado)

- Confirmacao de exclusao de card presente (window.confirm por card).
- Persistencia pos-restart aprovada no bloco E da Fase 5 (hash de titulos identico).
- Persistencia "apos reinicio de container": o deploy Docker existe (`compose.yaml`, banco em volume), mas as instancias ativas hoje sao o servidor Flask local e o servico Termux; a prova equivalente de reinicio foi feita nos dois. Reproducao em container fica registrada como justificativa (nao utilizado na execucao atual).

## Defeitos encontrados

- Nenhum. (Na Fase 5 da mesma sessao houve BE-F5-001 corrigido; aqui zero.)

## Conclusao

Criterio de saida: nenhuma falha critica; regras de limite com cobertura (suite) e probes registrados. Aceite do usuario pendente.
