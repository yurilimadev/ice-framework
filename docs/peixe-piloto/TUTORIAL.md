# Tutorial do Peixe-piloto

Este guia explica como usar o módulo Peixe-piloto no dia a dia. Ele complementa o briefing técnico em `COMANDOS.md` e o contrato em `../CONTRATO-DOMINIO-PEIXE.md`.

## 1. O que é

O Peixe-piloto é o cockpit diário de prospecção do ICE. Ele organiza:

- um lead por vez na missão do dia;
- a mensagem pronta para copiar ou abrir no canal;
- o pipeline de leads e o próximo follow-up;
- XP, nível, streak, quest semanal e badges;
- o fechamento da semana e a agenda dos próximos 7 dias.

Ele usa o mesmo banco SQLite do ICE, mas não altera tarefas, tags ou grupos. As tarefas continuam no painel principal; o Peixe só mostra as 3 melhores como referência.

## 2. Como abrir

No computador local:

```bash
cd "/home/limaydr/Ciclo de Estudos"
python3 -m flask --app wsgi run
```

Ou use o lançador `ice`. Depois abra:

```text
http://127.0.0.1:5000/peixe
```

Se a tela antiga aparecer, recarregue com `Ctrl+Shift+R`. O link **Peixe** também está na barra superior.

> Estado atual: a interface e os e-mails diário/semanal estão disponíveis localmente e em `https://ice.yurilimadev.com/peixe`. O envio automático está agendado no Termux via `cronie` (diário 08:00, semanal sexta 17:00).

## 3. Primeiro uso: cadastrar um lead

1. Abra **Peixe** e clique em **Novo lead**.
2. Preencha:
   - **Empresa**: nome da clínica ou negócio.
   - **Contato**: nome da pessoa, se souber.
   - **Setor**: por exemplo, `odontologia`.
   - **Cidade**: por exemplo, `Natal`.
   - **Canal**: WhatsApp, LinkedIn, Email, Instagram ou Presencial.
   - **Contato no canal**:
     - WhatsApp: número com DDD, ex. `84999999999`.
     - Email: endereço completo.
     - LinkedIn/Instagram: `@perfil` ou URL do perfil.
   - **Observação**: o que chamou sua atenção. Essa frase entra na mensagem.
3. Clique em **Salvar lead**.

O lead nasce com status **Novo**. O detalhe abre com a mensagem sugerida.

### Corrigir os dados de um lead

1. No detalhe do lead, clique em **Editar lead** (ou em **Editar** na linha do pipeline).
2. Ajuste empresa, contato, setor, cidade, canal, contato no canal ou observação.
3. Clique em **Salvar alterações**.

O status, a próxima ação e a data de criação são preservados. A observação merece atenção especial: ela entra literalmente na mensagem, então escreva uma frase que faça sentido depois de "Vi que" — por exemplo, "vocês têm boas avaliações no Google" em vez de uma nota interna.

Para WhatsApp, o número pode ser gravado com DDD (`84999999999`), com o `0` de discagem (`084999999999`) ou com `55`; o link **Abrir WhatsApp** normaliza o formato.

## 4. Missão do dia

A tela `/peixe` mostra a missão do dia: o primeiro lead com status **A enviar** ou **Enviado** e sem próxima ação ou com data vencida.

- Se houver follow-up vencido, ele aparece primeiro.
- Se não houver missão, a tela mostra um estado vazio e o atalho para cadastrar um lead.
- A mensagem é gerada no servidor e pode ser copiada ou aberta no canal.

### Mensagem gerada

O padrão é:

```text
Oi {contato}, tudo bem? Vi que {observação}.
Estou estudando {dor} em {setor} e queria te fazer 2 perguntas rápidas — não é venda.
Pode ser por aqui?
```

Para odontologia, a dor padrão é **falta de paciente e agenda**.

## 5. Enviar a primeira mensagem

Na missão do dia ou no detalhe do lead:

1. Clique em **Copiar mensagem** e cole no canal; ou
2. Use **Abrir WhatsApp**, **Enviar email**, **Abrir LinkedIn** ou **Abrir Instagram**.
3. Depois de enviar de verdade, clique em **Registrar envio** (ou **Mensagem enviada**).

O que acontece ao registrar envio:

- o status passa para **Enviado**;
- a próxima ação fica para **hoje + 3 dias**;
- a interação entra na timeline;
- você ganha **10 XP**.

Não registre o envio antes de enviar. A recompensa é por **enviar**, não por receber resposta.

## 6. Registrar os próximos movimentos

No detalhe do lead, use os botões conforme a conversa avançar:

| Botão | Quando usar | Status resultante |
|---|---|---|
| **Respondeu** | a pessoa respondeu à mensagem | Respondeu |
| **Conversa** | houve uma conversa de verdade | Conversa |
| **Proposta** | você enviou uma proposta | Proposta |
| **Piloto** | o piloto foi fechado | Piloto |
| **Pausar** | o lead saiu do fluxo por enquanto | Pausado |
| **Salvar nota** | registrar aprendizado sem mudar o status | mantém o status |

Siga a ordem principal:

```text
Novo -> A enviar -> Enviado -> Respondeu -> Conversa -> Proposta -> Piloto -> Ganho
```

- **Pausado** pode ocorrer depois de Enviado ou de uma etapa posterior.
- **Perdido** pode ocorrer a partir de um status ativo.
- O botão **Pausar** não tem um botão de retomar na interface. Para recolocar o lead no fluxo, registre uma nova **Mensagem enviada** quando fizer sentido.
- Os status **Ganho** e **Perdido** existem no domínio, mas ainda não têm botão próprio na interface.

## 7. Pipeline de leads

Abra **Ver pipeline** ou `/peixe/leads`.

- Cada linha mostra empresa, canal, status, próxima ação e atalho para abrir.
- As abas no topo filtram por status e mostram a contagem.
- **Todos** mostra o pipeline completo.
- Clique em **Abrir** para ver a mensagem, a timeline e as ações.

## 8. XP, níveis, streak e quest

### XP por ação

| Ação | XP |
|---|---:|
| Mensagem enviada | 10 |
| Resposta registrada | 15 |
| Conversa realizada | 30 |
| Proposta enviada | 50 |
| Piloto fechado | 150 |
| Nota ou pausa | 0 |

### Níveis

| XP | Nível |
|---|---|
| menos de 100 | Aprendiz |
| 100 a 299 | Piloto |
| 300 a 699 | Timoneiro |
| 700 ou mais | Capitão |

### Streak

O streak conta os dias locais consecutivos com pelo menos uma mensagem registrada. Ele considera hoje ou ontem como ponto de partida. Um dia sem mensagem quebra a sequência.

### Quest semanal

A meta padrão é:

- 5 mensagens;
- 2 respostas;
- 1 conversa.

O anel da quest mostra o progresso. Quando as 5 mensagens da semana são atingidas, o **doce** é liberado.

### Badges

As conquistas atuais são:

- primeira mensagem;
- primeira resposta;
- primeira conversa;
- primeiro piloto;
- streak de 4 semanas.

## 9. Fechamento da semana

Abra **Fechamento da semana** ou `/peixe/semana`.

A tela mostra:

- mensagens, respostas, conversas, propostas e pilotos da semana;
- XP, nível, streak e quest;
- campos de **aprendizado** e **bloqueio**;
- os próximos 5 nomes do pipeline.

Clique em **Salvar fechamento** para guardar o aprendizado e o bloqueio. O texto é global e substitui o anterior quando você salvar de novo.

## 10. Agenda dos próximos 7 dias

Abra **Agenda de 7 dias** ou `/peixe/agenda`.

- Mostra os leads com próxima ação entre hoje e os próximos 6 dias.
- O dia de hoje recebe destaque.
- Cada item leva ao detalhe do lead.

## 11. Relação com o ICE principal

- O Peixe não altera tarefas, tags ou grupos.
- O dashboard mostra as **3 melhores tarefas abertas** do ICE, somente leitura.
- Para mudar uma tarefa, use o **Painel** normal.

## 12. Rotina sugerida

### Diária (10 a 15 minutos)

1. Abra `/peixe`.
2. Copie a mensagem da missão do dia.
3. Envie pelo canal e clique em **Registrar envio**.
4. Confira os follow-ups vencidos.
5. Registre respostas, conversas ou notas do que aconteceu.
6. Use `/peixe/agenda` para ver o que vem nos próximos dias.

### Semanal (10 minutos)

1. Abra `/peixe/semana`.
2. Confira mensagens, respostas, conversas, propostas e pilotos.
3. Escreva o aprendizado e o bloqueio.
4. Escolha os próximos 5 nomes.
5. Volte ao pipeline e ajuste os leads parados.

## 13. Problemas comuns

**A tela não mostra nenhum lead.**
O banco começa vazio. Cadastre o primeiro lead em **Novo lead**.

**Não aparece missão do dia.**
A missão só considera leads **A enviar** ou **Enviado** com próxima ação vazia ou vencida. Ajuste o status ou a próxima ação.

**Cliquei em Respondeu e deu erro.**
A transição não é válida para o status atual. A ordem precisa seguir o fluxo: Enviado -> Respondeu -> Conversa -> Proposta -> Piloto.

**Registrei o envio e o lead sumiu da missão.**
Isso é esperado: o envio define follow-up para daqui a 3 dias. O lead volta quando o follow-up vencer ou se você ajustar a próxima ação.

**O online ainda não mostra `/peixe`.**
A publicação do módulo no servidor entra na Fase 16. Por enquanto, use o app local.

## 14. Cuidados com dados

- Use apenas dados públicos do lead: empresa, contato profissional e observação.
- Não coloque dado sensível de cliente na observação ou nas notas.
- O banco fica no mesmo SQLite do ICE; os backups e a publicação seguem o procedimento do projeto.
- O módulo não envia mensagem sozinho: você continua no controle do envio.

## 15. E-mails e publicação

Os e-mails já podem ser disparados manualmente:

```bash
python3 -m flask --app wsgi send-peixe-daily
python3 -m flask --app wsgi send-peixe-weekly
```

Os botões **Enviar resumo diario** e **Enviar fechamento** aparecem em `/peixe` quando o SMTP e o destino estão configurados. O destino é `PEIXE_TO`, com fallback para `DIGEST_TO`.

O agendamento no Termux usa `scripts/peixe-daily.sh` e `scripts/peixe-weekly.sh`, ativos via `cronie`/`crond`:

- diário às 08:00;
- semanal às sextas às 17:00.

O módulo também está publicado em `https://ice.yurilimadev.com/peixe`.
