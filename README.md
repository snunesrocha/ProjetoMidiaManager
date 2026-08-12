# 📸 MidiaManager

(... conteúdo anterior ...)

---

## 🧩 Fluxo de Uso – Interface Atualizada

O MidiaManager organiza mídias sem duplicidade e permite vincular pessoas às imagens.  
A interface foi ajustada para ser mais leve e funcional:

---

### 1. Grid Inicial de Registros
- Ao abrir a aplicação, você verá apenas os **registros da base de dados** em formato de **grid**.
- Cada linha mostra:
  - Nome do arquivo
  - Pasta de origem
  - Hash da mídia
  - Pessoa vinculada (se existir)
- Ao lado, há um botão **Visualizar** para abrir a imagem sob demanda.

📷 *Exemplo: tabela com colunas [Arquivo | Pasta | Hash | Pessoa | Visualizar]*

---

### 2. Visualizar Mídia
- Clique em **Visualizar** para abrir a imagem correspondente.
- Isso evita carregar todas as imagens de uma vez, deixando a interface mais rápida.

📷 *Exemplo: miniatura da imagem exibida após clicar em "Visualizar".*

---

### 3. Vincular Pessoa a Imagem
- Na seção **🔗 Vincular Pessoa a Imagem**:
  1. Selecione uma mídia no campo de escolha.
  2. A imagem escolhida será exibida imediatamente.
  3. Digite o nome da pessoa.
  4. Clique em **Vincular** para associar.

📷 *Exemplo: selectbox com arquivos, imagem exibida abaixo e campo para nome da pessoa.*

---

### 4. Gerenciar Vínculos
Na seção **👤 Gerenciar vínculos de pessoas**:
- Selecione uma pessoa cadastrada.
- Todas as mídias já vinculadas a ela serão exibidas.
- Para cada mídia:
  - Botão **Desvincular** → remove a associação.
- Campo **Adicionar nova mídia** → permite vincular novas imagens à pessoa.

📷 *Exemplo: lista de imagens vinculadas a "Maria", cada uma com botão "Desvincular".*

---

### 5. Estrutura no Banco de Dados
- **Tabela media** → registros de imagens únicas.
- **Tabela people** → registros de pessoas.
- **Tabela people_media** → vínculos entre pessoas e mídias (uma pessoa pode ter várias