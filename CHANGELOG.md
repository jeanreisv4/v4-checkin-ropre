# Histórico da skill checkin-ropre

Cada versão muda o que o cliente vê no check-in. Antes de publicar uma versão nova, rode
`python3 tests/regressao.py`.

## v1.2 · 22/09/2026 · O workflow vira arquivo, e o arquivo vira a documentação

- **`workflow/checkin-ropre.workflow.json` é a fonte da verdade** do check-in como workflow de
  agentes: 15 etapas com briefing, entradas, saídas e a marca de quem chama ferramenta, mais as 23
  conexões e as quatro leis. É este arquivo que se importa na plataforma.
- **`workflow/render_spec.py` gera a documentação a partir dele** — a especificação completa em
  `referencias/workflow_v4s.md`, o diagrama mermaid e os blocos do README. Documentação e arquivo de
  import não podem divergir porque não são escritos duas vezes.
- **README reescrito em torno do workflow**: o desenho em diagrama, a tabela das etapas, as leis, e o
  motivo de a etapa de cobertura vir antes do cálculo. A implementação em Python passa a ser
  apresentada como referência, não como o produto.

## v1.1 · 22/09/2026 · Flow ligado de verdade (MCP) e cobertura de fonte por canal

- **`extrair/flow_mcp.py` substitui o adaptador REST hipotético.** Os servidores do Flow falam MCP
  sobre HTTP (JSON-RPC + SSE), então o adaptador fala MCP direto: o ETL roda em cron ou terminal,
  sem depender de estar dentro de uma sessão do Claude. Traz mídia por dia e canal, metas do
  período, atividade do grupo de WhatsApp e as calls.
- **Mídia por SQL, leads por paginação com teto.** `flow_media_query` devolve custo, impressões e
  cliques por dia numa chamada só e exata. `flow_media_conversion_summary` desempacota os leads, mas
  devolve linha por anúncio e por dia, no máximo 100 por página e sem metadado de paginação — pedir
  500 truncava em silêncio. Agora pagina de 100 em 100 com teto e, se bater no teto, **descarta a
  contagem** em vez de publicar subcontagem.
- **Fonte por canal (`midia.fonte_por_canal`).** Um canal tem um dono. No primeiro cliente, um canal
  vinha do Flow (conexão em dia) e o outro da planilha, porque a conexão daquele canal no Flow estava
  falhando havia meses. Sem essa chave, o mês contava o mesmo canal duas vezes.
- **Cobertura de leads separada da cobertura de custo.** Um canal pode trazer custo e não trazer
  lead; quando isso acontece, CPL e entrada no CRM saem sem medição e o custo e o ROAS seguem.
- **Tolerância de consolidação (`midia.tolerancia_dias`, padrão 1).** Plataforma de anúncio fecha o
  dia com atraso; exigir dado de hoje reprovava todo período corrente.
- Credenciais do Flow saem do repositório: `~/.config/v4-flow/mcp.json`, com chmod 600.

### O que a primeira operação real mostrou

- Um cliente pode ter **mais de um projeto** no Flow (contratos separados); cada um é um check-in.
- Conexão de mídia pode estar **falhando há meses** sem ninguém notar — daí a etapa de cobertura.
- Projeto pode estar **sem meta cadastrada** no período: o bloco de Objetivos precisa dizer isso.
- Pode não haver **call registrada** no período, e o grupo de WhatsApp existir com os campos de
  resumo vazios. Nos dois casos, o check-in diz que não há, em vez de inventar.

## v1.0 · 22/09/2026 · ETL do Flow ao ROPRE

- **Arquitetura em três camadas**, com contrato explícito entre elas (`transformar/canonico.py`):
  extrair (um adaptador por fonte), transformar (métricas do período) e carregar (os cinco blocos
  do ROPRE). Trocar o CRM ou a origem dos dados não encosta no check-in.
- **Adaptadores:** `flow_nect` (Flow/NECT, dirigido por configuração — endpoints e mapa de campos no
  `cliente.json`), `crm_nectarcrm` (implementação de referência para CRM fora do Flow),
  `midia_planilha` (planilha de acompanhamento, diário) e `conversas_mcp` (calls e WhatsApp lidos
  por MCP, gravados em arquivo de entrada para poderem ser conferidos antes de virar slide).
- **Cadências quinzenal, mensal e quarter.** Período parcial sai marcado e a meta é proporcional aos
  dias corridos.
- **Regra de atribuição declarada por cliente**, viajando junto com cada registro e impressa no deck.
  No primeiro cliente ela ficou assim: tag vale sozinha, e origem de mídia paga conta mesmo quando o
  texto não nomeia a agência.
- **Fonte incompleta vira "não medido".** A primeira execução em setembro devolveu ROAS de 37 e
  entrada no CRM de 720%, porque a aba do Meta está parada em 31/08. Agora `cobertura_midia` confere
  se todo canal configurado tem dado até o fim do período; sem isso, investimento, CPL, CTR, ROAS e
  CAC saem sem medição, com aviso nomeando o canal e o último dia.
- **Tabela "Planilha do cliente contra CRM"** no bloco R: responde, antes de a pergunta aparecer na
  reunião, por que o check-in mostra mais venda que o lançamento manual (a planilha não soma
  recompra).
- **Renderizadores:** `.pptx` na ordem do template da V4 (capa, índice, 01 a 05 e uma página final de
  fontes) e markdown para revisão. Os dois saem do mesmo `checkin.json`, então não existe versão com
  número diferente.
- **Regressão** com fixture sintética: leitura de data, atribuição, novo/recorrente, quinzena, mídia
  incompleta, OKRs, pendências de call e WhatsApp e os dois renderizadores. A regressão contra
  cliente real fica local, fora do repositório.

### Em aberto

- **Ekyte** (entregas e horas do projeto) veio sem token no JSON de configuração.
- **CRM no Flow:** quando o projeto não tem conexão de CRM lá, o CRM segue sendo lido direto pela
  API dele. Com CRM no Flow, usar `flow_crm_list_tables` + `flow_crm_query`.
