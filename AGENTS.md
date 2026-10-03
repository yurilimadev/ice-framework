# Instrucoes do repositorio

- Converse com o usuario em portugues, salvo se ele pedir outro idioma.
- A fundacao atual usa Flask, `requirements.txt`, `python3 -m flask --app wsgi run` e Docker Compose.
- Envio de resumo por email: CLI `python3 -m flask --app wsgi send-digest` (ou `--to EMAIL`) ou botao "Enviar resumo" na barra superior (rota `POST /digest/send`, visivel apenas com SMTP configurado); requer `.env` local com `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` e `DIGEST_TO` (modelo em `.env.example`; `.env` fora do git). Nao commitar credenciais.
- Nao invente comandos, arquitetura ou convencoes; inspecione os arquivos existentes antes de orientar ou implementar qualquer mudanca.
- Desenvolva e implemente uma fase por vez; conclua e verifique os criterios da fase atual antes de iniciar a proxima. Nao implemente varias fases de uma vez.
- O papel do assistente neste repositorio e registrar decisoes, status, verificacoes e handoffs, alem de orientar a proxima sessao; nao cabe ao assistente codar ou iniciar implementacoes por iniciativa propria.
- Cada sessao deve registrar de quem precisa de retorno, qual retorno foi solicitado e qual condicao desbloqueia seu proximo passo.
- Ao iniciar uma sessao, leia primeiro `docs/README.md` e `docs/CONTEXTO-ATUAL.md`; depois consulte somente os contratos e o documento do papel envolvido.
- Antes de encerrar uma sessao, atualize `docs/CONTEXTO-ATUAL.md` com o estado, verificacoes, bloqueios, retornos e proximo passo.
- Ao adicionar a estrutura do projeto, atualize este arquivo somente com comandos e convencoes confirmados pela configuracao executavel.
