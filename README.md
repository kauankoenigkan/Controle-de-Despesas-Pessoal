# App de controle de despesas pessoal

<p align="left">
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Framework-Flet-008080?style=for-the-badge&logo=flutter&logoColor=white" alt="Flet">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Build-PyInstaller-2C3E50?style=for-the-badge&logo=python&logoColor=white" alt="PyInstaller">
</p>

## 🚀 Tecnologias e Ferramentas

* **Linguagem Principal:** Python 3.10+
* **Interface Gráfica (GUI):** Flet (Flutter para Python)
* **Banco de Dados:** SQLite3
* **Manipulação e Exportação de Dados:** CSV / Pandas
* **Empacotamento Desktop:** PyInstaller
* **Compilação Mobile:** GitHub Actions (CI/CD)
* **IDE Recomendada:** VS Code

---

## 📌 Funcionalidades

* **Interface Moderna:** Telas limpas e responsivas construídas em Flet.
* **Persistência Local:** Salvamento rápido de informações utilizando banco de dados SQLite.
* **Exportação de Relatórios:** Gerador automático de arquivos `.csv` organizados para leitura no Microsoft Excel ou Google Planilhas.
* **Multiplataforma:** Arquitetura pronta para gerar executáveis de Windows (`.exe`) e Android (`.apk`).

---

## ⚡ Diferenciais Técnicos (Boas Práticas)

* **Arquitetura Modular:** Divisão clara de responsabilidades entre interface (`app.py`), persistência de dados (`database.py`) e exportação (`exportar.py`).
* **Tratamento de Encoding:** Relatórios gerados em `utf-8-sig` para evitar erros de acentuação no Excel.
* **Compilação Automática na Nuvem:** Workflow configurado no GitHub Actions para compilar arquivos `.apk` sem carregar a máquina local.
* **Build Otimizado:** Inclusão correta dos recursos visuais do Material Design no PyInstaller para garantir a integridade do `.exe`.

---

## 📂 Estrutura do Projeto

```text
KoenApp/
├── .github/
│   └── workflows/
│       └── build_apk.yml    # Automação de compilação do APK no GitHub
├── .gitignore               # Arquivos ignorados pelo controle de versão
├── LICENSE                  # Licença de uso do código
├── README.md                # Documentação do projeto
├── requirements.txt         # Dependências do projeto Python
├── app.py                   # Interface principal da aplicação (Flet)
├── database.py              # Operações de banco de dados (SQLite3)
└── exportar.py              # Módulo de exportação de dados em CSV
```

```bash

# 1. Clone o repositório
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)

# 2. Acesse a pasta do projeto
cd seu-repositorio

# 3. Instale as dependências
python -m pip install -r requirements.txt

# 4. Execute a aplicação
python app.py

python -m PyInstaller --noconfirm --onedir --windowed --add-data "database.py;." --add-data "exportar.py;." --collect-data flet app.py
```

👨‍💻 Autor
Desenvolvido por Kauan Koenigkan.
