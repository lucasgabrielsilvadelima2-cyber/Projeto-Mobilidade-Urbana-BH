# Guia de Contribuição

Obrigado por considerar contribuir com este projeto! Este guia ajudará você a começar.

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/bh-mobilidade-pipeline.git
cd bh-mobilidade-pipeline
```

### 2. Configure o Ambiente

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências de desenvolvimento
pip install -r requirements.txt
pip install -e .
```

### 3. Crie uma Branch

```bash
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

### 4. Desenvolva

- Escreva código limpo e documentado
- Siga PEP 8
- Adicione testes para novas funcionalidades
- Atualize a documentação

### 5. Teste

```bash
# Execute os testes
pytest

# Verifique a cobertura
pytest --cov=src --cov-report=html

# Verifique o estilo
flake8 src/ tests/
black --check src/ tests/
```

### 6. Commit

```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
```

**Convenções de Commit:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração
- `style:` Formatação
- `chore:` Manutenção

### 7. Push e Pull Request

```bash
git push origin feature/minha-feature
```

Abra um Pull Request no GitHub com:
- Descrição clara das mudanças
- Referências a issues relacionadas
- Screenshots (se aplicável)

## 📋 Padrões de Código

### Python

- **PEP 8**: Siga o guia de estilo Python
- **Type Hints**: Use type hints quando possível
- **Docstrings**: Documente funções e classes

```python
def exemplo_funcao(param1: str, param2: int) -> bool:
    """
    Descrição breve da função.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
    
    Returns:
        Descrição do retorno
    """
    pass
```

### Testes

- Use pytest
- Nomeie testes como `test_nome_descritivo`
- Organize em classes `TestNomeModulo`
- Cubra casos positivos e negativos

```python
class TestMinhaClasse:
    def test_comportamento_esperado(self):
        # Arrange
        obj = MinhaClasse()
        
        # Act
        result = obj.metodo()
        
        # Assert
        assert result == expected
```

## 🐛 Reportando Bugs

Abra uma issue com:

- **Título claro**: Descrição concisa do problema
- **Descrição**: Explicação detalhada
- **Passos para reproduzir**: Como replicar o bug
- **Comportamento esperado**: O que deveria acontecer
- **Comportamento atual**: O que está acontecendo
- **Ambiente**: OS, versão do Python, etc.

## 💡 Sugerindo Features

Abra uma issue com:

- **Título claro**: Descrição da feature
- **Motivação**: Por que é necessária
- **Implementação sugerida**: Como poderia ser feita
- **Alternativas**: Outras abordagens consideradas

## ✅ Checklist de PR

Antes de submeter um PR, verifique:

- [ ] Código segue PEP 8
- [ ] Testes adicionados e passando
- [ ] Documentação atualizada
- [ ] Commits descritivos
- [ ] Branch atualizada com main
- [ ] PR tem descrição clara

## 📝 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.

## ❓ Dúvidas?

Abra uma issue ou entre em contato com os mantenedores.

Obrigado por contribuir! 🎉
