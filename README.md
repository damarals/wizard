# Wizard

Uma aplicação desktop para pesquisar e extrair metadados de artigos do Portal de Periódicos CAPES.

## Funcionalidades

- Pesquisa no Portal de Periódicos CAPES usando múltiplas consultas
- Configuração de parâmetros de pesquisa incluindo sintaxe de busca avançada
- Visualização e filtragem de resultados de pesquisa
- Exportação de metadados de artigos para CSV com campos configuráveis
- Processamento paralelo para buscas mais rápidas

## Instalação

### Windows

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

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.