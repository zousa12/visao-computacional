# Software Educacional de Transformações de Imagens

Aplicação educacional em Python e Streamlit para praticar matrizes e transformações.
O aluno escolhe uma imagem, corrige quatro quadrantes e visualiza a imagem recomposta
quando os quatro desafios são concluídos.

## Executar com Docker

Com o Docker em execução, abra um terminal na raiz deste repositório:

```sh
docker build -t software-educacional .
docker run --rm -p 127.0.0.1:8501:8501 software-educacional
```

Abra [http://localhost:8501](http://localhost:8501). O Streamlit escuta em
`0.0.0.0:8501` dentro do contêiner; a publicação acima permite o acesso local.
Encerre com `Ctrl+C`. Reconstrua a imagem depois de alterar o código.

A construção instala e verifica as dependências e executa os testes. Para uma
construção sem cache, acrescente `--no-cache` ao comando `docker build`.

## Executar com Python no Windows

Use Python 3.12. Na raiz do repositório, pelo PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra [http://localhost:8501](http://localhost:8501). O Docker usa Python 3.12.14;
as versões de NumPy, Pillow e Streamlit estão fixadas em `requirements.txt`.

## Como usar

1. Escolha **Imagem de exemplo** ou **Enviar PNG ou JPEG**. O arquivo precisa
   ter pelo menos 2 × 2 pixels. A leitura aplica a orientação EXIF e converte
   os canais para RGB. Arquivos inválidos ou pequenos demais recebem orientação.
2. Confira a grade 2×2 e as dimensões informadas. Cada painel reúne imagem
   alterada, enunciado, campos numéricos e botão de aplicação.
3. Preencha os valores e envie uma correção por vez. A última tentativa e seu
   feedback permanecem no painel; os demais desafios continuam disponíveis.
4. Depois dos quatro acertos, confira **Imagem recomposta** abaixo da grade.

| Posição | Esquerda | Direita |
| --- | --- | --- |
| Linha superior | Q1 — Frente Esquerdo | Q2 — Frente Direito |
| Linha inferior | Q3 — Trás Esquerdo | Q4 — Trás Direito |

Quando a largura é ímpar, a coluna extra fica à direita; quando a altura é
ímpar, a linha extra fica embaixo. Todos os pixels e as posições são preservados.
As imagens se ajustam ao espaço dos painéis; consulte as legendas para conhecer
as dimensões reais em pixels.

## Desafios e respostas de referência

| Desafio | Alteração | Correção de referência |
| --- | --- | --- |
| Q1 | Rotação de 180° em torno do centro. | Matriz `[[-1, 0], [0, -1]]`. |
| Q2 | Ampliação inteira, sem recortar, por 2 em X e 3 em Y. | Fator X `0.5` e fator Y `0.333333`. |
| Q3 | Espelhamento horizontal. | Reflexão `[[-1, 0], [0, 1]]`, ou a composição abaixo. |
| Q4 | Mistura reversível dos canais RGB. | Matriz inversa `[[1.5, -0.5, 0], [-0.5, 1.5, 0], [0, 0, 1]]`. |

### Coordenadas e composição

Q1 e Q3 usam coordenadas relativas ao centro: X para a direita e Y para cima.
As prévias geométricas mantêm o quadro do quadrante; regiões transformadas para
fora dele são recortadas e áreas sem pixels de origem aparecem em preto.

No Q3, escolha **Composição de duas matrizes** para aplicar primeiro a rotação
em Z `A = [[-1, 0], [0, -1]]` e depois a reflexão vertical
`B = [[1, 0], [0, -1]]`. Como os vetores são colunas, a matriz resultante é
`B × A`. Outras composições equivalentes também são aceitas. A rotação isolada
não desfaz o espelhamento horizontal.

### Escala inversa

Na imagem de exemplo, Q2 passa de 240 × 160 para 480 × 480 pixels. Os fatores
inversos recuperam 240 × 160 pixels. As dimensões são arredondadas para pixels
inteiros; ampliações fracionárias usam os fatores efetivos das dimensões geradas.
A interpolação bicúbica pode alterar ligeiramente os pixels: a resposta é validada
pelos fatores e pelas dimensões, sem exigir igualdade entre as imagens.

Cada redimensionamento é limitado a 16 milhões de pixels e 16.384 pixels por lado.
Zero, negativos, valores não finitos e resultados menores que 1 pixel recebem erro.
Se a ampliação do Q2 exceder os limites, envie uma imagem menor; os outros painéis
continuam disponíveis e a referência do Q2 permanece visível.

### Matriz de cores

O filtro do Q4 é `M = [[0.75, 0.25, 0], [0.25, 0.75, 0], [0, 0, 1]]`.
Cada pixel é um vetor coluna: `RGB alterado = M × RGB original`. As linhas da
matriz produzem R, G e B, nessa ordem. O aluno insere a matriz inversa de M.

Os cálculos usam `float64`, sem limitar ou arredondar os valores intermediários.
Apenas as prévias limitam os canais a 0–255 e arredondam para inteiros. Cada
correção parte dos dados filtrados originais, nunca dos pixels da prévia.
O filtro é reversível; a aplicação não tenta recuperar dados perdidos por
conversão em preto e branco ou compressão destrutiva.

## Validação e feedback

Todos os campos recebem números; nenhum código digitado pelo aluno é executado.

| Desafio | Aceite | Orientação para uma resposta incorreta |
| --- | --- | --- |
| Q1 | Transformação equivalente à inversa, tolerância absoluta `1e-8`. | Eixo ainda alterado e sinais a revisar. |
| Q2 | Fatores inversos, tolerância absoluta `1e-6`, e dimensões finais corretas. | Dimensões obtidas/esperadas, eixo incorreto ou coincidência por arredondamento. |
| Q3 | Reflexão ou composição equivalente, tolerância absoluta `1e-8`. | Eixo incorreto ou reflexão que falta após rotação isolada. |
| Q4 | Composição com o filtro (`1e-8`) e canais recuperados (`1e-6`). | Maior erro RGB ou coincidência de pixels em imagem uniforme. |

As comparações usam tolerância relativa zero. Formatos inválidos, números
complexos ou não finitos, matrizes singulares e operações fora dos limites
numéricos geram erros tratados no próprio painel. Corrija os campos e tente novamente.

## Progresso e recomposição

As tentativas, prévias, mensagens e correções aceitas ficam na sessão Streamlit.
A barra mostra de 0 a 4 quadrantes concluídos. Interagir com outros formulários ou
alternar o método do Q3 preserva o progresso da mesma imagem e sessão.

A recomposição aparece após quatro acertos e usa os resultados realmente
calculados, com as dimensões e posições originais. O Q2 mantém suas diferenças
de interpolação; ele não é substituído pela referência. Uma tentativa posterior
incorreta ou inválida atualiza a mensagem, preservando o último acerto salvo.

Trocar imagem, dimensões ou origem reinicia progresso e campos. Uploads também
consideram nome e conteúdo do arquivo. Upload inválido ou removido limpa o
progresso anterior. Cada sessão tem seu próprio estado em memória; fechar a
sessão ou reiniciar a aplicação pode descartá-lo. Histórico entre sessões é o
escopo opcional da [issue 13](https://github.com/zousa12/visao-computacional/issues/13).

## Testes e validação do fluxo completo

Depois de instalar as dependências:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
.\.venv\Scripts\python.exe -m unittest test_flow -v
```

Em Linux ou em outro ambiente com as dependências instaladas, use
`python -m unittest discover -v` e `python -m unittest test_flow -v`.
Os testes de interface precisam do Streamlit; sem ele, são marcados como ignorados.

Para repetir o fluxo em um contêiner novo, após construir a imagem:

```sh
docker run --rm software-educacional python -m unittest test_flow -v
```

| Cobertura | Cenários |
| --- | --- |
| Leitura de arquivos | PNG/JPEG, EXIF, RGB, tons de cinza, RGBA, formatos inválidos, truncamento e tamanho mínimo. |
| Transformações | Respostas corretas, incorretas, equivalentes, tolerâncias e valores extremos. |
| Fluxo completo | Upload pelo widget real da aplicação, correções de Q1–Q4, feedback, progresso e recomposição. |
| Troca de imagem | Novos pixels, nome de arquivo, origem, upload inválido/pequeno e remoção do arquivo. |
| Recomposição | Dimensões pares/ímpares, posições, preservação de pixels e resultado real da escala. |

O GitHub Actions constrói a imagem e executa a suíte completa durante a construção.
Depois executa `test_flow` em um contêiner novo, inicia outro contêiner com a
aplicação e verifica `http://127.0.0.1:8501/_stcore/health`. Os fluxos de interface
usam Streamlit AppTest; a verificação HTTP confirma a inicialização do serviço.

### Roteiro de aceite manual

1. Construa e execute a imagem Docker pelos comandos deste README.
2. Na imagem de exemplo, envie uma resposta errada e uma matriz singular; confira
   as mensagens e a possibilidade de corrigir os campos sem perder outros acertos.
3. Aplique as respostas da tabela: Q1, escala do Q2, composição do Q3 e inversa RGB.
   Confira que a recomposição aparece somente depois do quarto acerto.
4. Envie um PNG ou JPEG de dimensões ímpares e repita as correções. Confira as
   dimensões e as posições dos quadrantes na imagem final.
5. Troque o arquivo, envie um arquivo inválido/pequeno e remova o upload. Confira
   o reinício do progresso e a recuperação após enviar um arquivo válido.
6. Revise o PR e os checks. O merge na `main` com `Closes #12` encerra a issue 12;
   confirme o estado **Closed** e o item **Done** no quadro, se necessário.

## Organização do código

| Arquivo | Responsabilidade |
| --- | --- |
| `app.py` | Seleção e leitura da imagem, identificação do upload e entrada da interface. |
| `image_input.py` | Decodificação, normalização, exemplo e divisão em quadrantes. |
| `transformations.py` | Operações geométricas, RGB e tolerâncias numéricas. |
| `answer_validation.py` | Aceite e feedback contextual das respostas. |
| `challenge_ui.py` | Grade 2×2, formulários, prévias e barra de progresso. |
| `session_progress.py` | Tentativas, acertos, reinício do estado e recomposição. |
| `test_*.py` | Testes unitários e de interface. |

O [backlog](BACKLOG.md) descreve as etapas e o
[quadro do projeto](https://github.com/users/zousa12/projects/2) acompanha as tarefas.
