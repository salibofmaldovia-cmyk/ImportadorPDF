<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Importador de Clientes</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
  <style>
    body { font-family: Arial; margin: 40px; }
    input, button { margin: 10px 0; width: 100%; padding: 8px; }
    label { font-weight: bold; }
  </style>
</head>
<body>
  <h1>📄 Importador de Clientes via PDF</h1>
  <input type="file" id="pdfInput" accept="application/pdf">
  <div id="formFields"></div>
  <button onclick="salvarCSV()">Salvar CSV</button>

  <script>
    const campos = ["NomeCliente", "Endereco", "RG", "CPF", "Bairro", "Cidade", "Estado", "CEP"];
    const dados = {};

    document.getElementById("pdfInput").addEventListener("change", async function () {
      const file = this.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = async function () {
        const typedarray = new Uint8Array(this.result);
        const pdf = await pdfjsLib.getDocument(typedarray).promise;
        const page = await pdf.getPage(1);
        const textContent = await page.getTextContent();
        const texto = textContent.items.map(item => item.str).join("\n");

        extrairDados(texto);
        renderizarCampos();
      };
      reader.readAsArrayBuffer(file);
    });

    function extrairDados(texto) {
      const nomeMatch = texto.match(/Nome empresarial\n(.+)/);
      dados["NomeCliente"] = nomeMatch ? nomeMatch[1].trim() : "Não encontrado";

      const cnpjMatch = texto.match(/\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/);
      dados["CPF"] = cnpjMatch ? cnpjMatch[0] : "Não encontrado";

      const rgMatch = texto.match(/\d{2}\.\d{3}\.\d{2}-\d/);
      dados["RG"] = rgMatch ? rgMatch[0] : "Não encontrado";

      const enderecoMatch = texto.match(/Endereço do estabelecimento\n(.+)\n(.+)/);
      if (enderecoMatch) {
        dados["Endereco"] = enderecoMatch[1].trim();
        const linha2 = enderecoMatch[2].trim();
        const match = linha2.match(/(.+?)\s*-\s*(.+?)\s+([A-Z]{2})\s+(\d{2}\.\d{3}-\d{3})/);
        if (match) {
          dados["Bairro"] = match[1].trim();
          dados["Cidade"] = match[2].trim();
          dados["Estado"] = match[3].trim();
          dados["CEP"] = match[4].trim();
        } else {
          dados["Bairro"] = dados["Cidade"] = dados["Estado"] = dados["CEP"] = "Não encontrado";
        }
      } else {
        campos.forEach(c => dados[c] = dados[c] || "Não encontrado");
      }
    }

    function renderizarCampos() {
      const container = document.getElementById("formFields");
      container.innerHTML = "";
      campos.forEach(campo => {
        const label = document.createElement("label");
        label.textContent = campo + ":";
        const input = document.createElement("input");
        input.value = dados[campo] || "";
        input.id = campo;
        container.appendChild(label);
        container.appendChild(input);
      });
    }

    function salvarCSV() {
      const linhas = [
        campos.join(","),
        campos.map(c => document.getElementById(c).value).join(",")
      ];
      const blob = new Blob([linhas.join("\n")], { type: "text/csv;charset=utf-8" });
      const nomeArquivo = document.getElementById("NomeCliente").value.replace(/[\\/*?:"<>|]/g, "_") + ".csv";
      saveAs(blob, nomeArquivo);
    }
  </script>
</body>
</html>
