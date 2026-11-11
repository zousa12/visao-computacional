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

## Executar com Docker

Com o Docker em execução, rode na raiz do repositório:

```sh
docker build -t software-educacional .
docker run --rm -p 127.0.0.1:8501:8501 software-educacional
```

Abra `http://localhost:8501` no navegador.
