# Check-in ROPRE

**Do dado bruto do Flow ao check-in do cliente — em deck e documento, com a regra de atribuição
declarada e o que não foi medido escrito na cara.**

Skill do [Claude Code](https://claude.com/claude-code). Roda sozinha no terminal também: é Python
puro, com `python-pptx` só na hora de gerar o deck.

## O problema

Todo check-in de cliente responde as mesmas cinco perguntas — resultados, objetivos, premissas e
riscos, entregas, próximos passos. Na prática, cada um monta do seu jeito: número que sai de uma
planilha lançada à mão, ROAS calculado sobre uma base parada, e uma reunião inteira discutindo por
que a apresentação mostra mais venda que o CRM.

Esta skill existe para que o check-in saia sempre do mesmo lugar, com as mesmas definições, e para
que cada número possa ser defendido linha por linha.

## Como está montada

```
extrair/       E — um adaptador por fonte, todos devolvem o mesmo formato
  flow_nect.py         Flow/NECT (CRM, mídia, chat) — dirigido por configuração
  crm_nectarcrm.py     CRM direto (implementação de referência)
  midia_planilha.py    mídia paga em planilha (Growth Pack e similares)
  conversas_mcp.py     calls e WhatsApp lidos por MCP
transformar/   T — modelo canônico e as métricas do período
  canonico.py          o contrato entre extrair e carregar; períodos e validação
  metricas.py          vendas, funil, mídia, break-even, safra, atribuição
carregar/      L — os cinco blocos do ROPRE e os dois renderizadores
  blocos.py            monta o checkin.json
  documento.py         markdown para revisar
  deck.py              .pptx na ordem do template da V4
clientes/<cliente>/    cliente.json, extrato do CRM e entradas do período (fora do git)
tests/regressao.py     as regras que não podem quebrar
```

## Uso

```bash
./gerar.sh exemplo mensal 2026-08-15
./gerar.sh exemplo quinzenal 2026-09-21
python3 tests/regressao.py
```

Saída em `saida/<cliente>/`: `checkin.json`, `checkin.md` e `checkin.pptx`.

## As regras

| Regra | Por quê |
| --- | --- |
| Faturamento lê data de fechamento | é o que o cliente reconhece como resultado do mês |
| Safra lê data de criação | é a leitura que isola o efeito da mídia do mês |
| Novo e recorrente separados e somados | a planilha do cliente costuma lançar só o novo |
| Atribuição declarada no `cliente.json` | número sem regra escrita não se defende |
| Fonte incompleta vira "não medido" | evita ROAS inflado por base parada |
| Período parcial é marcado, meta é proporcional | quinzena não se compara com meta mensal |

## Configurar um cliente novo

Copie `clientes/exemplo/cliente.json` e ajuste: fee, verba, margem, funis de venda e de
recorrência, a regra de atribuição, os OKRs do ciclo e os riscos conhecidos. Para ligar o Flow,
preencha o bloco `flow` com o `project_document_id` — o topo de `extrair/flow_mcp.py` explica como
achar o projeto e onde ficam as credenciais.

## Licença

MIT.
