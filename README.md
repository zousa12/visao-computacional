# Software Educacional de Transformações de Imagens

Projeto acadêmico para praticar vetores, matrizes, transformações geométricas e processamento de imagens. O aluno recebe uma imagem dividida em quatro quadrantes alterados e tenta reconstruí-la digitando a fórmula ou a matriz de correção de cada parte.

## Como funciona

1. O aluno escolhe uma imagem de exemplo ou carrega um arquivo PNG ou JPEG.
2. O sistema divide a imagem em quatro quadrantes e aplica uma transformação diferente em cada um.
3. O aluno consulta as informações do desafio, digita sua resposta e visualiza o resultado.
4. O sistema compara cada tentativa com a referência do quadrante e indica o que ainda precisa ser corrigido. Ao concluir os quatro desafios, o aluno vê a imagem recomposta.

| Posição na tela | Esquerda | Direita |
| --- | --- | --- |
| Linha superior | 1. Frente Esquerdo | 2. Frente Direito |
| Linha inferior | 3. Trás Esquerdo | 4. Trás Direito |

## Os quatro desafios

| Quadrante | Alteração aplicada | Tarefa do aluno |
| --- | --- | --- |
| 1. Frente Esquerdo | Rotação de 180° em torno do centro do quadrante. | Inserir a matriz de rotação que recoloca a imagem na orientação original. |
| 2. Frente Direito | Ampliação por fatores conhecidos, mantendo o quadrante inteiro visível. | Calcular e inserir a escala inversa para recuperar a largura e a altura de referência. |
| 3. Trás Esquerdo | Espelhamento horizontal. | Corrigir o espelhamento com uma matriz de reflexão ou com uma composição que inclua uma rotação de 180° no eixo Z. |
| 4. Trás Direito | Mistura reversível dos canais de cor por uma matriz. | Inserir a matriz inversa para recuperar as cores originais. |

### 1. Rotação

Usando coordenadas relativas ao centro do quadrante, a rotação de 180° transforma o vetor `(x, y)` em `(-x, -y)`. Aplicar a mesma rotação novamente recupera a orientação inicial. A matriz de correção é `[[-1, 0], [0, -1]]`.

### 2. Escala

Se o quadrante for ampliado por um fator `sx` na horizontal e `sy` na vertical, a correção usa a matriz `[[1/sx, 0], [0, 1/sy]]`. Por exemplo, uma ampliação de 2 vezes em ambos os eixos é corrigida com os fatores `0,5` e `0,5`. O desafio mostra as dimensões original e ampliada para que o aluno calcule esses fatores.

### 3. Espelhamento

O espelhamento horizontal transforma `(x, y)` em `(-x, y)`. A mesma reflexão desfaz a alteração. Para praticar a composição de transformações, o aluno também pode girar 180° em torno de Z, obtendo `(-x, -y)` a partir de `(x, y)`, e depois refletir a coordenada vertical, obtendo `(-x, y)`. A rotação sozinha troca o sinal dos dois eixos.

### 4. Matriz de cores

Cada pixel é tratado como um vetor coluna RGB. Um exemplo de filtro reversível é a matriz `M = [[0.75, 0.25, 0], [0.25, 0.75, 0], [0, 0, 1]]`. Se o pixel alterado é `M · RGB`, o aluno deve aplicar `M⁻¹ = [[1.5, -0.5, 0], [-0.5, 1.5, 0], [0, 0, 1]]` ao vetor alterado. O sistema mantém os valores internos em ponto flutuante e arredonda apenas na visualização.

A escolha de um filtro reversível permite recuperar a imagem e praticar o cálculo da matriz inversa. Converter a imagem em preto e branco ou usar compressão com perda elimina informações necessárias para recuperar exatamente o original. Este desafio simula a ideia de desfazer um filtro matricial e trabalha como a intensidade dos canais afeta a cor.

## Implementação proposta

- **Python** para a lógica dos desafios e a validação das respostas.
- **NumPy** para operações com vetores, matrizes e canais de cor.
- **Pillow** para ler imagens, separar os quadrantes e montar a prévia.
- **Streamlit** para a interface no navegador, com campos numéricos para matrizes e fatores de escala. A aplicação converte esses valores em operações sem executar código digitado pelo aluno.
- **Docker** para empacotar e executar a aplicação.

A primeira versão pode guardar o progresso em memória durante a sessão. Se o projeto passar a exigir histórico entre sessões, SQLite pode armazenar tentativas e resultados.

## Critérios para a primeira versão

- Exibir os quatro quadrantes alterados e permitir testar cada correção separadamente.
- Mostrar o resultado de cada tentativa e aceitar fórmulas ou matrizes equivalentes.
- Validar as transformações geométricas com base na matriz resultante e nas dimensões esperadas. Isso permite distinguir erros de cálculo de pequenas diferenças na imagem causadas pelo redimensionamento.
- Comparar as cores recuperadas com a referência usando uma tolerância numérica e remontar a imagem quando os quatro desafios forem concluídos.

## Executar a aplicação

Com Python 3.12, execute na raiz do repositório pelo PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra [a aplicação local](http://localhost:8501). A versão atual permite visualizar a imagem de exemplo ou enviar um PNG ou JPEG de pelo menos 2 × 2 pixels. A prévia usa a orientação do arquivo e os canais RGB. O [quadro do projeto](https://github.com/users/zousa12/projects/2) acompanha as próximas etapas.

## Desafio Q1 disponível

O primeiro quadrante aparece girado em 180°. Preencha os quatro campos da matriz
2 x 2 e clique em **Aplicar matriz ao Q1** para visualizar a tentativa e receber
feedback. A matriz `[[-1, 0], [0, -1]]` recupera a orientação original. A validação
compara a transformação com tolerância absoluta de `1e-8`, inclusive quando a
imagem tem simetria. Matrizes singulares ou valores não finitos recebem uma
mensagem de erro. As tentativas sempre partem do quadrante alterado original.

As coordenadas são relativas ao centro, com X para a direita e Y para cima.
A prévia mantém as dimensões do quadrante: partes transformadas para fora do
quadro são recortadas e áreas sem pixels de origem aparecem em preto.

Para executar os testes de transformação, após instalar as dependências:

```sh
python -m unittest discover -v
```

## Desafio Q2 disponível

O quadrante **Frente Direito** é ampliado sem recortar, por 2 em X e 3 em Y.
A tela informa as dimensões originais e ampliadas em pixels e exibe a imagem
inteira, ajustada à largura disponível no navegador.

Preencha **Fator de correção em X** e **Fator de correção em Y**, depois clique
em **Aplicar escala ao Q2**. Para o desafio atual, use `0.5` em X e `0.333333`
em Y. A imagem de exemplo passa de 240 × 160 para 480 × 480 pixels e volta
a 240 × 160. Cada tentativa parte da imagem ampliada, preservando a referência.

A validação compara a escala inversa (tolerância absoluta de `1e-6`) e as
dimensões recuperadas, sem exigir igualdade de pixels após interpolação bicúbica.
As dimensões são arredondadas para pixels inteiros; com ampliação fracionária,
os fatores inversos são calculados pelas dimensões efetivas. Zero, negativos,
valores não finitos e resultados menores que 1 pixel são rejeitados. Para
controlar o uso de memória, cada redimensionamento é limitado a 16 milhões de
pixels e 16.384 pixels por lado; se a ampliação exceder esses limites, envie uma
imagem menor. Q1 continua disponível nesse caso.

### Aceite e encerramento da issue 5

1. Execute `python -m unittest discover -v` com as dependências instaladas ou
   construa a imagem Docker, que também executa todos os testes.
2. No navegador, confirme as dimensões do Q2 e aplique `0.5` em X e `0.333333`
   em Y. Verifique a prévia de 240 × 160 pixels e o feedback de sucesso.
3. Teste uma resposta incorreta e fatores zero ou negativos: devem gerar
   orientação, sem interromper a aplicação. Confira também a correção do Q1.
4. Revise o PR vinculado à issue 5 e confirme que a verificação Docker passou.
5. Faça o merge do PR na `main`. A referência `Closes #5` encerra a issue
   automaticamente. Confirme o estado **Closed** e, se necessário, atualize o
   item no quadro do projeto para **Done**.

## Desafio Q3 disponível

O quadrante **Trás Esquerdo** aparece espelhado horizontalmente na grade 2×2,
com as dimensões originais preservadas. Cada desafio tem seu próprio formulário,
prévia e feedback. As respostas são exclusivamente numéricas; nenhum código
digitado pelo aluno é executado.

Em **Reflexão direta**, informe `[[-1, 0], [0, 1]]`. Em **Composição de duas
matrizes**, informe a rotação de 180° em Z em A (`[[-1, 0], [0, -1]]`) e a
reflexão vertical em B (`[[1, 0], [0, -1]]`). Para vetores coluna, aplica-se
primeiro A e depois B, portanto a matriz final é `B × A`. Ambas as respostas
restauram todos os pixels do quadrante de referência. A rotação isolada não
corrige o espelhamento. Outras composições equivalentes também são aceitas.

Clique em **Aplicar correção ao Q3** para ver o resultado. Cada tentativa parte
do Q3 espelhado original; não modifica os outros quadrantes. A validação usa a
matriz resultante com tolerância absoluta de `1e-8`, inclusive para imagens
simétricas. Matrizes singulares, formatos inválidos, valores não finitos ou uma
composição numericamente inválida geram erro. A prévia usa o mesmo quadro e as
mesmas coordenadas centrais do Q1: X para a direita e Y para cima.

### Aceite e encerramento da issue 6

1. Execute `python -m unittest discover -v` com as dependências instaladas ou
   construa a imagem Docker, que executa todos os testes.
2. Confira a grade 2×2 e o espelhamento do Q3. Aplique a reflexão direta e,
   em seguida, a composição descrita acima: ambas devem receber sucesso.
3. Teste identidade, rotação isolada e matriz singular. As duas primeiras
   devem receber orientação e a última deve gerar um erro tratado.
4. Confirme que Q1 e Q2 continuam funcionando e que cada envio corrige apenas
   o quadrante correspondente, sem executar texto como código.
5. Revise o PR e os checks; faça merge na `main`. A referência `Closes #6`
   fecha a issue automaticamente. Confirme **Closed** e atualize o quadro
   para **Done**, se necessário.

## Executar com Docker

Com o Docker em execução, rode na raiz do repositório:

```sh
docker build -t software-educacional .
docker run --rm -p 127.0.0.1:8501:8501 software-educacional
```

Abra `http://localhost:8501` no navegador.
