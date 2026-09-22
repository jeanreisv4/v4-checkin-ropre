# -*- coding: utf-8 -*-
"""Gera a documentação do workflow a partir do JSON, para as duas nunca divergirem.

  python3 workflow/render_spec.py

Fonte da verdade: `workflow/checkin-ropre.workflow.json` — é ele que se importa no V4S.
Saídas: `referencias/workflow_v4s.md` (a especificação com os briefings) e o diagrama
mermaid que o README usa.
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, "workflow", "checkin-ropre.workflow.json")
SPEC = os.path.join(RAIZ, "referencias", "workflow_v4s.md")
DIAGRAMA = os.path.join(RAIZ, "workflow", "diagrama.mmd")
README = os.path.join(RAIZ, "README.md")

CORES = {
    "Briefing": "briefing", "Dados": "dados", "Pesquisa": "pesquisa",
    "Análise": "analise", "Revisão": "revisao", "Entrega": "entrega",
}


def curto(titulo, largura=22):
    """Quebra o título em duas linhas para o nó do diagrama não ficar comprido."""
    palavras, linhas, atual = titulo.split(), [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    linhas.append(atual)
    return "<br/>".join(linhas)


def mermaid(wf):
    linhas = ["flowchart TD"]
    for e in wf["etapas"]:
        marca = " 🔧" if e["chama_ferramenta"] else ""
        linhas.append(f'    E{e["id"]}["<b>{e["id"]}</b> {curto(e["titulo"])}{marca}"]')
    linhas.append("")
    for c in wf["conexoes"]:
        linhas.append(f'    E{c["de"]} --> E{c["para"]}')
    linhas.append("")
    for cat, classe in CORES.items():
        ids = [f'E{e["id"]}' for e in wf["etapas"] if e["categoria"] == cat]
        if ids:
            linhas.append(f'    class {",".join(ids)} {classe};')
    linhas += [
        "",
        "    classDef briefing fill:#1f2937,stroke:#60a5fa,color:#e5e7eb;",
        "    classDef dados fill:#1f2937,stroke:#34d399,color:#e5e7eb;",
        "    classDef pesquisa fill:#1f2937,stroke:#fbbf24,color:#e5e7eb;",
        "    classDef analise fill:#1f2937,stroke:#f87171,color:#e5e7eb;",
        "    classDef revisao fill:#1f2937,stroke:#a78bfa,color:#e5e7eb;",
        "    classDef entrega fill:#1f2937,stroke:#e5e7eb,color:#e5e7eb;",
    ]
    return "\n".join(linhas)


def tabela_etapas(wf):
    linhas = ["| # | Etapa | Categoria | Origem | Chama ferramenta |", "| --- | --- | --- | --- | --- |"]
    for e in wf["etapas"]:
        origem = f'catálogo · `{e["etapa_do_catalogo"]}`' if e["origem"] == "catalogo" else "do zero"
        linhas.append(f'| {e["id"]} | {e["titulo"]} | {e["categoria"]} | {origem} | '
                      f'{"sim" if e["chama_ferramenta"] else "—"} |')
    return "\n".join(linhas)


def spec(dados):
    wf = dados["workflow"]
    p = [
        "<!-- Gerado por workflow/render_spec.py a partir de workflow/checkin-ropre.workflow.json.",
        "     Edite o JSON, não este arquivo. -->",
        "",
        "# Check-in ROPRE — especificação do workflow para o V4S",
        "",
        "Especificação da versão que roda **dentro do V4S**: os dados chegam pelo Nekt e as etapas",
        "executam lá. Nenhum passo depende de script externo. O arquivo de import é",
        "[`workflow/checkin-ropre.workflow.json`](../workflow/checkin-ropre.workflow.json).",
        "",
        "O ETL em Python deste repositório deixa de ser motor e passa a ser **implementação de",
        "referência**: serve para conferir se o workflow chegou aos mesmos números num período já",
        "fechado.",
        "",
        "**Cabeçalho**",
        "",
        "| Campo | Valor |",
        "| --- | --- |",
        f'| Nome | {wf["nome"]} |',
        f'| Produto | {wf["produto"]} *(confirmar)* |',
        f'| Promessa | {wf["promessa"]} |',
        f'| Escopo | {wf["escopo"]} no primeiro ciclo; solicitar canonização depois de rodar em dois clientes |',
        f'| Cadências | {", ".join(wf["cadencias"])} |',
        f'| Etapas | {len(wf["etapas"])} |',
        f'| Conexões | {len(wf["conexoes"])} |',
        "",
        "## O desenho",
        "",
        "```mermaid",
        mermaid(wf),
        "```",
        "",
        "🔧 = etapa que chama ferramenta (MCP) durante a execução.",
        "",
        "---",
        "",
        "## As leis do workflow",
        "",
        "Entram no briefing de **toda** etapa que toca número. Com o cálculo acontecendo em etapa de",
        "modelo, a regra precisa viajar junto com a tarefa — o agente não pode depender de lembrar.",
        "",
    ]
    for i, lei in enumerate(wf["leis"], 1):
        p.append(f"{i}. {lei}")
    p += ["", "---", ""]

    for e in wf["etapas"]:
        origem = (f'**do catálogo** (`{e["etapa_do_catalogo"]}`)' if e["origem"] == "catalogo" else "do zero")
        ferramenta = " · *chama ferramenta*" if e["chama_ferramenta"] else ""
        p += [
            f'## {e["id"]} · {e["titulo"]}',
            "",
            f'**Categoria:** {e["categoria"]} · {origem}{ferramenta}',
            f'**Entradas:** {", ".join(e["entradas"])}',
            f'**Saídas:** {", ".join(e["saidas"])}',
            "",
        ]
        p += ["> " + l if l.strip() else ">" for l in e["briefing"].splitlines()]
        p.append("")

    p += [
        "---",
        "",
        "## Conexões",
        "",
        "```",
        "  " + "  ".join(f'{c["de"]}→{c["para"]}' for c in wf["conexoes"]),
        "```",
        "",
        "## Como validar antes de publicar",
        "",
        "Rode o workflow num **período já fechado** e compare com a implementação de referência deste",
        "repositório, número a número: vendas, receita, novos, recorrentes, ganhos da safra e taxa de",
        "ganho. Se o workflow chegar sozinho aos mesmos valores, as definições estão corretamente",
        "escritas nos briefings. Se não chegar, a diferença aponta exatamente qual definição ficou",
        "ambígua.",
        "",
        "## O que ainda depende do Studio",
        "",
        "1. **O schema de import do V4S.** O JSON deste repositório é neutro e auto-descritivo; o",
        "   mapeamento para o formato do Studio é mecânico assim que houver um workflow exportado de lá",
        "   para servir de molde.",
        "2. **O catálogo completo de etapas.** Só uma etapa foi reusada (`Resumo de call → briefing`);",
        "   com a lista inteira, provavelmente 06, 07 e 08 também têm equivalente pronto.",
        "3. **Como a etapa declara a ferramenta que chama** — vale para as sete etapas marcadas com 🔧.",
        "4. **Confirmar o produto** do workflow.",
        "",
    ]
    return "\n".join(p)


def preencher(texto, marca, conteudo):
    """Troca o miolo entre <!-- marca:inicio --> e <!-- marca:fim -->."""
    padrao = re.compile(rf"(<!-- {marca}:inicio -->)(.*?)(<!-- {marca}:fim -->)", re.S)
    if not padrao.search(texto):
        raise SystemExit(f"README sem os marcadores de {marca}")
    return padrao.sub(lambda m: f"{m.group(1)}\n{conteudo}\n{m.group(3)}", texto)


def atualizar_readme(wf):
    texto = open(README, encoding="utf-8").read()
    texto = preencher(texto, "diagrama", "```mermaid\n" + mermaid(wf) + "\n```")
    texto = preencher(texto, "etapas", tabela_etapas(wf))
    leis = "\n".join(f"{i}. {lei}" for i, lei in enumerate(wf["leis"], 1))
    texto = preencher(texto, "leis", leis)
    open(README, "w", encoding="utf-8").write(texto)


def main():
    dados = json.load(open(FONTE, encoding="utf-8"))
    wf = dados["workflow"]
    open(SPEC, "w", encoding="utf-8").write(spec(dados))
    open(DIAGRAMA, "w", encoding="utf-8").write(mermaid(wf) + "\n")
    atualizar_readme(wf)
    print(f'{os.path.relpath(SPEC, RAIZ)}: {len(wf["etapas"])} etapas, {len(wf["conexoes"])} conexões')
    print(f'{os.path.relpath(DIAGRAMA, RAIZ)}: diagrama mermaid')
    print(f'{os.path.relpath(README, RAIZ)}: diagrama, tabela de etapas e leis atualizados')


if __name__ == "__main__":
    main()
