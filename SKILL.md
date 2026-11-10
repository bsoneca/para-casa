---
name: para-casa
description: Busca no AVA da Escola Balão Vermelho (ava.grupobalaovermelho.com.br) o para casa do dia seguinte de cada filho e gera um PDF para imprimir, com a atividade, as páginas da apostila, uma explicação do tema e exercícios extras. Use quando o usuário pedir "para casa", "dever de casa", "/para-casa" ou o PDF do AVA.
---

# Para Casa

Objetivo: as crianças fazem o para casa no papel, sem computador. O PDF precisa
bastar sozinho: nada nele pode exigir abrir o AVA.

Arquivos desta pasta (`~/.claude/skills/para-casa/`):
- `kids.json` — cada filho (nome, `userid` do Moodle, turma, nível 🟡 Amarelo /
  🔵 Azul / ⚪ Branco), quantos dias olhar (`days`) e onde salvar (`out`). Fica
  só neste computador (o `.gitignore` o deixa fora do repositório).
  `kids.example.json` mostra o formato.
- `fetch.js` — roda dentro da aba do AVA e devolve o aluno logado e os eventos
  de amanhã até o próximo dia letivo, com o texto completo.
- `template.html` — o layout de impressão (A4). `render.sh` — HTML → PDF.
- `montar.py` — junta as partes com páginas das apostilas; `--achar` localiza
  uma atividade na apostila. Roda com `.venv/bin/python -I` (pypdf, pypdfium2).

Antes de começar:
- Se `kids.json` não existir, é a primeira vez: copie `kids.example.json` para
  `kids.json`, pergunte ao usuário o nome de cada filho, a turma e o nível, e
  deixe `userid` em `null`; ele é preenchido na primeira leitura do AVA de cada
  filho (passo 2).
- O AVA abre no Chrome do usuário (Claude in Chrome), onde ele já entrou. Se
  `list_connected_browsers` não mostrar navegador, peça para reconectar a
  extensão; não use o navegador do app (lá não há login).
- Se a `.venv` sumir: `python3 -m venv .venv && .venv/bin/pip install pypdf pypdfium2 pillow reportlab`.
- O filtro do Claude in Chrome bloqueia saídas com URLs com query string
  ("Cookie/query string data"). No JS, troque URLs por `[link]` ou corte o `?…`
  antes de devolver o texto.

## Passos

1. **Abrir o AVA no Chrome** (Claude in Chrome: `tabs_context_mcp`, nova aba,
   `https://ava.grupobalaovermelho.com.br/my/`). Se cair na tela de login, peça ao
   usuário para entrar com o Google da escola do filho; nunca digite senha.
2. **Ler os eventos:** cole o conteúdo de `fetch.js` em `javascript_tool`
   (ajuste `DAYS` com o `days` do `kids.json`). O para casa é sempre o do
   **próximo dia letivo**, não o de amanhã: o `fetch.js` pula fins de semana e
   feriados ou recessos do calendário do AVA (`target` diz a data). Os eventos
   dos dias pulados (um sábado letivo, um aviso) entram só como linhas na
   tabela-resumo. Se o usuário pedir outro dia ("para segunda"), use esse dia.
   Na capa, escreva "para <dia da semana>, DD/MM". Confira que `userid` bate com um
   filho do `kids.json` (um `userid` em `null` é preenchido pelo nome do aluno);
   se for um aluno novo, pergunte turma e nível e adicione.
   A saída da ferramenta corta textos longos (`[TRUNCATED]`): para esses, busque o
   texto inteiro daquele dia com `core_calendar_get_calendar_day_view` e
   imprima só a parte que faltou. Anexos (`files`, links `pluginfile.php`) são
   baixados com `fetch` na aba, e o texto ou as imagens entram no PDF.
3. **Escolher o que entra:**
   - Trabalhos e materiais citados no enunciado ("orientações no AVA") são
     arquivos na seção da disciplina: baixe e imprima junto, como as apostilas.
   - Para casa (`📓 Para Casa`, tarefas `assign`, provas e avaliações dos
     próximos dias): entra. Quando o enunciado vem por nível, use só o nível do
     filho; não mostre os outros.
   - Avisos (tutoria, escalas, sábado letivo): só uma linha na tabela-resumo.
   - Eventos repetidos em cursos de anos anteriores (ex.: um evento "6º ANO -
     2025" visto por um aluno do 7º): ignore.
   - Se o enunciado pede algo que só existe no AVA (formulário, vídeo, planilha)
     ou é um envio (e-mail), escreva o que o aluno precisa saber e avise, na
     tabela-resumo, que essa parte exige o computador.
   - Gere o PDF sempre, mesmo quando a tarefa já saiu num PDF anterior ou só
     pede um envio: o usuário quer a folha impressa do dia.
   - Os professores publicam ao longo do dia: cada rodada lê o AVA de novo e
     refaz o PDF do dia por inteiro (sobrescreve `<out>/AAAA-MM-DD Nome.pdf`).
4. **Apostilas:** quando a tarefa cita páginas de uma apostila, imprima essas
   páginas junto. As apostilas são arquivos (`resource`) na seção do trimestre de
   cada disciplina. Liste com `fetch('/course/view.php?id=<curso>&section=<1|2|3>')`
   e os links `a[href*="/mod/resource/"]`, e escolha a do nível do filho (ex.:
   "Apostila Amarela - …"). Antes de baixar, veja se já está em
   `<out>/apostilas/` (o nome termina com `(<id do resource>).pdf`). Para baixar,
   rode na aba:
   `const r=await fetch('/mod/resource/view.php?id=<id>&redirect=1');const a=document.createElement('a');a.href=URL.createObjectURL(await r.blob());a.download='AVA-<id>.pdf';document.body.append(a);a.click();`
   Um arquivo por vez: o Chrome bloqueia o segundo download automático da mesma
   página, então recarregue a aba (`navigate`) antes de cada download.
   O arquivo às vezes fica com o nome temporário `~/Downloads/.com.google.Chrome.*`
   mesmo completo. Se o tamanho bater com o `b.size` do blob, use esse arquivo.
   Espere aparecer `~/Downloads/AVA-<id>.pdf` (pode levar 1 a 2 minutos) e mova
   para `<out>/apostilas/<Disciplina> <ano> - <título> (<id>).pdf`.
   Algumas disciplinas não têm o arquivo: a seção traz um link (`url`, ex.:
   "Apostila AMARELA (3ª etapa)") para um Google Doc, às vezes dentro de uma
   subseção (`fetch('/course/view.php?id=<curso>&section=<n>')` lista os
   `li.activity`; o link fica em `/mod/url/view.php?id=<id>`, em
   `.urlworkaround a`). Abra `https://docs.google.com/document/d/<doc>/export?format=pdf`
   na aba; se o Google pedir para confirmar o login, peça ao usuário para entrar
   com a conta da escola e baixar o PDF (Arquivo → Fazer download → PDF). Procure
   o arquivo em `~/Downloads` e em `~/Documents` (o Chrome pode salvar em
   qualquer um) e copie para `<out>/apostilas/` com o id do `url` no nome.
   O número impresso na apostila não é o do PDF. Ache a página com
   `.venv/bin/python -I montar.py --achar <apostila.pdf> "ATIVIDADE 36"`, que
   mostra os dois números. Leia o texto da atividade e das páginas de teoria
   logo antes dela. Páginas que são só imagem, renderize com pypdfium2 da `.venv`
   e leia a imagem. Imprima a página da atividade e as páginas de teoria que ela usa.
5. **Enriquecer**, para cada tarefa, no nível da turma e em português (inglês
   nas tarefas de inglês):
   - *O que o professor pediu:* o enunciado exato, sem resumir. Depois, diga
     quais páginas da apostila vêm em seguida e qual atividade fazer nelas, se a
     página tiver outras.
   - *Para entender o tema:* 1–3 parágrafos curtos e corretos sobre o assunto,
     com os termos e as classificações da apostila (não os de outro livro). Deve
     explicar a teoria que a tarefa usa. Nunca escreva a resposta da tarefa nem
     o conteúdo que o aluno deve produzir: dê uma dica de como pensar. Quando o
     enunciado pede algo além da apostila ("ao menos uma diferente da apostila",
     "pesquise"), não faça a pesquisa por ele: diga onde procurar sem computador
     (livro, um adulto) e que tipo de coisa procurar, sem nomes nem descrições
     prontas. Os exercícios extras também não podem conter as respostas uns dos
     outros nem da tarefa. (Os alunos notam respostas prontas.)
     Não resuma o texto da apostila: as páginas vão impressas logo depois, e
     o resumo vira a resposta das questões abertas, e o aluno se sente
     tratado como incapaz. Explique um conceito que a tarefa usa e o
     texto não explica, ou dê uma moldura para ler o capítulo. Nada de truques
     de prova ("procure palavras como total, todas"), roteiro ligando cada
     parte do texto a uma questão, ou instruções óbvias ("leia antes",
     "sublinhe"), sobretudo a partir do 8º ano.
   - *Exercícios extras:* 4–6 do mesmo assunto, com linhas para responder
     (que façam pensar além da tarefa: aplicar, comparar, argumentar; não
     repetir em outras palavras as perguntas da apostila)
     (`<div class="linhas" style="--n:N">`). Para provas, um roteiro de estudo.
   Não faça folha para os pais nem gabarito: o usuário não quer.
   Não cite números de página do PDF (a quebra muda ao imprimir).
   Se não achar a apostila no AVA, diga a página e peça para fazer nela; não
   invente o conteúdo da apostila.
6. **Gerar o PDF:** faça um HTML a partir de `template.html` para cada parte,
   no scratchpad: a primeira tem a capa, o quadro e a primeira tarefa, e cada
   tarefa seguinte fica num arquivo próprio (com `style="break-before:auto"` na
   seção). O comentário no topo do template contém `<section class="tarefa">`:
   ao cortar ou montar HTML por texto, procure depois de `<body>`.
   Rode `render.sh <html> <parte.pdf>` em cada um e junte tudo, com as
   páginas da apostila logo depois da sua tarefa:
   `.venv/bin/python -I montar.py "<out>/AAAA-MM-DD Nome.pdf" parte1.pdf "<apostila.pdf>:56-57,60" parte2.pdf`
   (data de hoje, `out` expandido, páginas do PDF). Use o `montar.py` mesmo
   quando houver uma parte só: é ele que numera as páginas ("Nome · página N de T"). Confira as páginas
   renderizando com pypdfium2 e mostre ao usuário com `SendUserFile`.
7. **Outro filho:** o Chrome guarda uma conta do AVA por vez. Diga ao usuário
   que, para o próximo filho, ele saia do AVA e entre com a conta dele; não saia
   da conta por ele.

## Imprimir

Depois de mostrar o PDF, pergunte se deve imprimir. Com o sim, mande para a
impressora padrão do Mac:
`lp -o media=A4 -o fit-to-page "<out>/AAAA-MM-DD Nome.pdf"`. Depois rode `lpstat -o` e informe o trabalho na fila. Se `lpstat -d` disser
que não há impressora padrão, peça ao usuário para adicioná-la em Ajustes do
Sistema → Impressoras e Scanners; não instale drivers.

Se o trabalho ficar em "Sending data to printer" por mais de 1 minuto, veja o
alerta em `lpstat -l -p` e conte ao usuário o que ele diz. Nas Epson da linha
EcoTank (ex.: L3250), os alertas comuns são:
- `com.epson.ER01_003-error`: a impressora está com um erro no painel. Peça ao
  usuário para ver as luzes. As duas luzes de Wi-Fi piscando são erro de Wi-Fi:
  ele aperta o botão de Wi-Fi uma vez para limpar.
- `com.epson.ER06_005-error media-empty`: acabou o papel. O usuário põe A4 e
  aperta o botão de continuar. Ela imprime da última página para a primeira,
  então as que faltaram são as primeiras: pergunte quais saíram e reimprima só
  as outras com `lp ... -P 1-3`.
- `com.epson.COM_001-error` depois que o painel ficou normal: a conexão USB antiga
  travou. Cancele o trabalho (`cancel <id>`) e mande de novo com `lp`.
