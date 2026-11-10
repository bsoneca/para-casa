# Para Casa

**Aponte o seu Claude Desktop para esta URL e seja feliz com para casas sem computador.**

Abra o app Claude, vá na aba **Code** e cole:

```
Instale o skill https://github.com/bsoneca/para-casa
```

Depois é só pedir "faz o para casa da Ana", e seguir as instruções do Claude.

---

Um skill do [Claude Code](https://claude.com/claude-code) que lê o para casa no
AVA da Escola Balão Vermelho e monta um PDF para imprimir: o enunciado do
professor, as páginas da apostila, uma explicação curta do tema e exercícios
extras. A criança faz tudo no papel, sem computador.

O skill nunca escreve as respostas: a explicação dá a teoria e uma forma de
pensar, e os exercícios extras pedem para aplicar, comparar e argumentar.

## Para o Claude: como instalar

Quando alguém pedir para instalar este skill, faça isto, sem pedir que a pessoa
rode comandos:

1. `git clone https://github.com/bsoneca/para-casa.git ~/.claude/skills/para-casa`
   (se a pasta já existir, `git -C ~/.claude/skills/para-casa pull`).
2. Crie a `.venv` nessa pasta e instale `pypdf pypdfium2 pillow reportlab`:
   no macOS/Linux `python3 -m venv .venv && .venv/bin/pip install ...`; no
   Windows `py -3 -m venv .venv` (ou `python -m venv .venv`) e
   `.venv/Scripts/pip.exe install ...`. Sem Python no Windows, peça para a
   pessoa instalar pela Microsoft Store ou por python.org.
   Sem `git`, baixe `https://github.com/bsoneca/para-casa/archive/refs/heads/main.zip`
   e extraia em `~/.claude/skills/para-casa`.
3. Veja se a extensão Claude in Chrome está conectada. Se não estiver, explique
   como instalá-la no Chrome e que o filho precisa estar logado no AVA nesse
   Chrome, com a conta Google da escola.
4. Pergunte o nome, a turma e o nível (🟡 Amarelo, 🔵 Azul, ⚪ Branco) de cada
   filho e crie `kids.json` a partir de `kids.example.json` (`userid` em `null`).
5. Diga que está pronto: é só pedir "faz o para casa da <nome>" ou `/para-casa <nome>`.
   (Se o `/para-casa` não aparecer, abra uma sessão nova para o skill carregar.)

## Do que precisa

- Um computador com Windows ou Mac e o [Claude Code](https://claude.com/claude-code)
  (o app Claude para desktop, aba Code, ou o `claude` no terminal).
- Google Chrome com a extensão **Claude in Chrome**, e o filho com o login do
  AVA feito nesse Chrome (a conta Google da escola).
- Python 3 (já vem no macOS; no Windows, instale pela Microsoft Store ou por python.org).
- Uma impressora configurada no computador, se quiser imprimir direto.

## Instalar à mão

```bash
git clone https://github.com/bsoneca/para-casa.git ~/.claude/skills/para-casa
```

No Mac:

```bash
cd ~/.claude/skills/para-casa && python3 -m venv .venv && .venv/bin/pip install pypdf pypdfium2 pillow reportlab
```

No Windows (PowerShell):

```powershell
cd ~\.claude\skills\para-casa; py -3 -m venv .venv; .venv\Scripts\pip.exe install pypdf pypdfium2 pillow reportlab
```

Na primeira vez que você pedir o para casa, o Claude pergunta o nome, a turma e
o nível (🟡 Amarelo, 🔵 Azul, ⚪ Branco) de cada filho e cria o `kids.json`.
Esse arquivo fica só no seu computador e nunca vai para o repositório. Se
preferir, copie `kids.example.json` para `kids.json` e preencha você mesmo.

## Usar

No Claude Code, digite:

```
/para-casa Ana
```

ou peça "faz o para casa da Ana". O Claude abre o AVA no seu Chrome, lê as
tarefas do próximo dia letivo, baixa as apostilas, gera o PDF em
`~/Documents/Para Casa/` e pergunta se deve imprimir.

O Chrome guarda uma conta do AVA por vez: para o próximo filho, saia do AVA e
entre com a conta dele.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `SKILL.md` | As instruções que o Claude segue. |
| `fetch.js` | Roda na aba do AVA e lê os eventos do calendário. |
| `template.html` | O layout de impressão (A4). |
| `render.py` | Transforma o HTML em PDF com o Chrome ou o Edge. |
| `montar.py` | Junta as partes com as páginas das apostilas e numera. |
| `kids.example.json` | O formato do `kids.json`. |

## Outras escolas

O AVA da Balão Vermelho é um Moodle. Para outra escola com Moodle, troque o
endereço do AVA no `SKILL.md` e confira como as tarefas e apostilas aparecem
lá.
