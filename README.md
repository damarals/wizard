<div align="center">
    <img src=".github/banner.png" style="border-radius: 15px; max-width: 100%; height: auto; display: block; margin: 0 auto 16px;" alt="Wizard banner"/>
    <img src="https://img.shields.io/github/v/tag/damarals/wizard?color=success&label=" alt="Latest Tag" />
    <img src="https://github.com/damarals/wizard/actions/workflows/test.yaml/badge.svg" alt="Tests Status" />
    <a href="https://codecov.io/gh/damarals/wizard" >
      <img src="https://codecov.io/gh/damarals/wizard/graph/badge.svg?token=YJYmxxhTBx" alt="Code Coverage"/>
    </a>
    <img src="https://img.shields.io/github/last-commit/damarals/wizard/main?label=%C3%BAltimo%20commit&color=blue" alt="Last Commit" />
</div>
</br>
<div align="center">Uma aplicação desktop para <b>pesquisar e extrair metadados</b> de artigos do Portal de Periódicos CAPES</div>

## Introdução

O Wizard é uma aplicação desktop desenvolvida para facilitar a pesquisa e extração de metadados de artigos científicos do Portal de Periódicos CAPES. Ideal para pesquisadores, acadêmicos e estudantes que precisam realizar levantamentos bibliográficos de forma eficiente e organizada.

## Funcionalidades

- 🔍 **Pesquisa Avançada** usando múltiplas consultas e sintaxe complexa
- ⚡ **Processamento Paralelo** para buscas mais rápidas
- 📊 **Visualização de Resultados** com filtragem e ordenação
- 📤 **Exportação Configurável** para CSV com campos personalizáveis

## Instalação

### Windows e Linux

Baixe o instalador mais recente da página de [Releases](https://github.com/damarals/wizard/releases) e execute-o.

### Do Código Fonte

#### Usando Poetry (recomendado)

```bash
# Clone o repositório
git clone https://github.com/damarals/wizard.git
cd wizard

# Instale as dependências com Poetry
poetry install

# Execute a aplicação
poetry run wizard
```

#### Dev Container no VS Code

1. Abra o projeto no VS Code
2. Quando perguntado, escolha "Reabrir no Container"
3. No terminal integrado, execute:
   ```bash
   poetry install
   poetry run wizard
   ```

## Uso

1. **Adicionar Consultas de Pesquisa**
   - Clique em "Adicionar Consulta" para adicionar uma nova consulta
   - Digite um tema e termos de busca
   - Ative a sintaxe de busca avançada para consultas complexas

2. **Configurar Preferências**
   - Ajuste o número de workers concorrentes para processamento paralelo
   - Configure o atraso entre requisições para evitar sobrecarga do servidor
   - Limite o número de páginas a serem pesquisadas por consulta

3. **Executar Pesquisas**
   - Clique no botão de reprodução ao lado de cada consulta para iniciar a pesquisa
   - Monitore o progresso na barra de status
   - Visualize os resultados na tabela inferior

4. **Exportar Resultados**
   - Clique em "Exportar Artigos" para salvar os resultados em um arquivo CSV
   - Configure quais campos incluir na exportação através das configurações de exportação
   - Escolha um local para o arquivo exportado

## Desenvolvimento

### Configurar Ambiente de Desenvolvimento

```bash
# Instale as dependências de desenvolvimento
poetry install --with dev,test

# Execute os testes
poetry run pytest

# Com cobertura de código
poetry run pytest --cov=wizard --cov-report=xml
```

### Estrutura do Projeto

```
wizard/
├── src/               # Código fonte
│   └── wizard/        
│       ├── core/      # Funcionalidade principal (scraper, parser, exportador)
│       ├── ui/        # Componentes da interface do usuário
│       └── utils/     # Utilitários (logging, configuração)
├── tests/             # Suíte de testes
└── resources/         # Recursos (ícones, etc.)
```

### Fluxo de Desenvolvimento

1. Fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feat/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feat/nova-funcionalidade`)
5. Abra um Pull Request

## Contribuindo

Contribuições são sempre bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests. Se encontrar algum problema ou quiser sugerir uma melhoria, não hesite em contribuir.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.