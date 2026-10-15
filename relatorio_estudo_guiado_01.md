# Estudo Guiado 01 — Pipeline CI: Integração Contínua, Testes e Deploy com Docker

**Grupo:** Sheila Barroso, Arthur Rebouças, Carlos Rodrigo Ferreira e Vitória Cavalcante
**Repositório:** https://github.com/sheilabarroso/fastorder-api

---

## Seção 4 — Pesquisa Inicial

### 4.1 O que é um Runner? Onde o código executa na nuvem gratuita do GitHub?

Runner é a máquina (física, virtual ou contêiner) que recebe um job de um pipeline de CI/CD, executa seus passos em ordem e devolve o resultado (sucesso ou falha) e os logs. O workflow descreve *o que* fazer; o runner é *quem* faz.

Na nuvem gratuita do GitHub, o código roda em **GitHub-hosted runners**: máquinas virtuais efêmeras, gerenciadas pelo GitHub, que já vêm com Git, Python, Docker e outras ferramentas (no nosso caso, `runs-on: ubuntu-latest`). Cada job recebe uma VM limpa, que é destruída ao terminar. Por isso nada fica salvo entre execuções e, se quisermos manter a imagem Docker, precisamos publicá-la em um registry.

### 4.2 O que é Linting? Por que rodar o flake8 antes dos testes economiza tempo?

Linting é a análise estática do código-fonte, sem executá-lo, para encontrar erros de sintaxe, variáveis não usadas, imports desnecessários e violações de estilo (PEP 8). O flake8 faz isso em Python.

Ele roda em poucos segundos, enquanto instalar dependências, rodar testes e construir imagens leva bem mais. Em uma esteira, os passos mais baratos e rápidos vêm primeiro: se o código tem erro de sintaxe ou de formatação, o pipeline falha logo (*fail fast*) e não gasta minutos de runner em etapas caras que já estariam condenadas. É o *Shift-Left* na prática: o erro é encontrado o mais cedo possível.

### 4.3 Diferença entre VM e contêiner Docker. Por que o Docker virou padrão?

| | Máquina Virtual | Contêiner Docker |
|---|---|---|
| Isolamento | Hardware virtualizado com um sistema operacional completo (kernel próprio) para cada VM | Isola processos, compartilhando o kernel do host |
| Tamanho | GBs | MBs |
| Inicialização | Minutos | Segundos ou milissegundos |
| Consumo de recursos | Alto | Baixo |
| Portabilidade | Imagens pesadas | Imagem leve e padronizada |

O Docker virou padrão para entregas contínuas porque a imagem empacota aplicação, dependências e configuração em um artefato imutável e reprodutível. O mesmo artefato roda no notebook, no runner de CI e em produção, o que elimina o "na minha máquina funciona". Além disso, é leve, sobe rápido, escala fácil e é aceito por praticamente todas as plataformas de nuvem.

---

## Seção 10 — Questões para Análise

### Questão 1 — Como o `ci-pipeline.yml` altera o Lead Time?

Lead Time = Tempo de Processamento (PT) + Tempo de Espera (WT) entre o commit e o código validado e empacotado.

No fluxo tradicional do VSM, o WT dominava: o código esperava alguém rodar os testes manualmente, esperava revisão, esperava a equipe de Ops montar o ambiente e fazer o deploy. Cada espera podia levar horas ou dias, então:

`LT_manual = PT + (WT_testes + WT_build + WT_ambiente + WT_deploy) ≈ dias`

Com o pipeline, essas esperas viram uma execução automática e disparada pelo próprio `push`:

`LT_CI = PT_lint + PT_testes + PT_build ≈ alguns minutos`

Os termos de espera (WT) tendem a zero e o PT passa a ser o tempo de máquina. Também diminuem o retrabalho e o ciclo de feedback: o desenvolvedor descobre o erro minutos após o commit, ainda com o contexto fresco, e não dias depois. O ganho é de ordens de grandeza, de dias para minutos.

### Questão 2 — Por que Lint e testes vêm antes do `docker build`? O que ocorreria com os custos se invertêssemos?

Porque as etapas são ordenadas da mais barata e rápida para a mais cara (fail fast). O flake8 leva segundos, o pytest leva segundos e o `docker build` leva bem mais (baixar a imagem base, instalar dependências, gerar camadas).

Se invertêssemos, um commit com erro de lint ou com teste quebrado ainda gastaria o tempo completo do build antes de ser reprovado. Cada falha desperdiçaria minutos de runner e aumentaria o custo de computação e o tempo de espera do desenvolvedor, que seria multiplicado a cada commit quebrado. Em planos gratuitos, esses minutos são limitados (o que acelera o esgotamento da cota) e, em planos pagos, são cobrados. Na ordem correta, o build só acontece quando o código já provou ser válido.

### Questão 3 — Como `COPY requirements.txt .` e `RUN pip install` resolvem o "Muro da Confusão"?

O Muro da Confusão é o conflito entre Dev, que entrega código, e Ops, que o executa em outro ambiente ("para mim funcionava"). Ele nasce de diferenças de versão, bibliotecas e configuração entre os ambientes.

O Dockerfile transforma o ambiente em código versionado: `COPY requirements.txt .` seguido de `RUN pip install -r requirements.txt` declara exatamente quais dependências (e versões fixadas) a aplicação precisa e as instala dentro da imagem. Dev e Ops passam a usar o mesmo artefato, construído do mesmo jeito, então não há mais "ambiente do Dev" e "ambiente do Ops". O ambiente é definido, revisável e reproduzível, o que torna o Dockerfile um contrato compartilhado entre as duas equipes.

Há também um ganho de eficiência: copiar o `requirements.txt` e instalar as dependências *antes* de copiar o resto do código aproveita o cache de camadas do Docker. Se só o código mudou, o `pip install` não é refeito.

---

## Missão 5.1 — Explicação do código (`/api/soma`)

Os parâmetros `a` e `b` chegam pela URL como string via `request.args.get(...)`. A função `_ler_numeros()` valida que ambos existem e os converte para `float`; se faltar algum ou se não forem numéricos, a rota devolve **HTTP 400** com uma mensagem de erro. Se tudo estiver certo, a rota devolve JSON com a operação e o resultado (`/api/soma?a=5&b=7` → `{"operacao": "soma", "resultado": 12}`).

Os testes em `test_app.py` usam o `test_client` do Flask e cobrem: soma de inteiros, decimais e negativos, parâmetro ausente e parâmetro inválido (400), além das demais operações e da divisão por zero.

---

## Evidências do pipeline (preencher durante a gravação)

| Execução | Commit | Resultado | O que aconteceu / aprendizado |
|---|---|---|---|
| 1 | (mensagem) | ✅ / ❌ | |
| 2 — bug proposital (`+` → `-` na soma) | | ❌ falhou no passo 5 (pytest) | |
| 3 — correção | | ✅ | |
