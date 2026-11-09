# Backlog — Software Educacional de Transformações de Imagens

## Primeira versão

1. **Preparar a estrutura Python e a tela inicial em Streamlit.** Declarar NumPy, Pillow e Streamlit como dependências. Separar a interface das operações de imagem. Aceite: a aplicação abre no navegador e exibe a tela inicial.
2. **Carregar imagem de exemplo e aceitar PNG e JPEG.** Normalizar a orientação e os canais da imagem. Aceite: arquivos válidos aparecem na prévia e arquivos inválidos ou pequenos demais recebem uma mensagem clara.
3. **Dividir a imagem nos quatro quadrantes.** Guardar dimensões e referências de cada recorte. Aceite: a divisão respeita as posições do README e inclui todos os pixels mesmo quando largura ou altura são ímpares.
4. **Implementar Q1 — Rotação de 180°.** Girar em torno do centro e aplicar a matriz inserida pelo aluno. Aceite: a matriz diagonal com valores −1 restaura a orientação original.
5. **Implementar Q2 — Escala inversa.** Ampliar sem recortar, informar as dimensões e aplicar os fatores de correção. Aceite: a escala inversa recupera a largura e a altura esperadas, inclusive com fatores diferentes em X e Y.
6. **Implementar Q3 — Espelhamento horizontal.** Aplicar a reflexão e aceitar a correção direta ou a composição de rotação no eixo Z e reflexão vertical. Aceite: ambas as respostas equivalentes restauram a orientação.
7. **Implementar Q4 — Filtro RGB reversível.** Misturar os canais por matriz e aplicar a matriz de correção em ponto flutuante. Aceite: a inversa recupera os valores de referência dentro da tolerância, com arredondamento apenas para exibição.
8. **Montar a interface dos quatro desafios.** Exibir a grade 2×2, enunciados, campos numéricos e prévia de cada tentativa. Aceite: o aluno consegue corrigir um quadrante por vez, sem executar código digitado.
9. **Validar respostas e mostrar feedback.** Verificar formatos e valores, comparar matrizes e dimensões na geometria e usar tolerância para RGB. Aceite: respostas equivalentes são aceitas, erros de entrada recebem orientação e diferenças de interpolação na escala não invalidam uma solução correta.
10. **Guardar o progresso e recompor a imagem.** Usar o estado da sessão para registrar as correções e limpar o progresso ao trocar de imagem. Aceite: a reconstrução aparece depois das quatro correções e preserva dimensões e posições.
11. **Empacotar a aplicação com Docker.** Criar o Dockerfile e configurar o Streamlit para escutar na porta 8501. Aceite: os comandos do README constroem a imagem e abrem a aplicação no navegador.
12. **Testar o fluxo completo e revisar o README.** Cobrir entradas inválidas, imagens com dimensões ímpares, respostas certas e erradas e troca de imagem. Aceite: uma execução nova em Docker passa do carregamento à reconstrução e a documentação corresponde ao fluxo verificado.

## Opcional

13. **Persistir o histórico com SQLite se houver necessidade.** Definir quais dados de tentativas e resultados serão guardados. Aceite: o histórico pode ser consultado após reiniciar a aplicação.
