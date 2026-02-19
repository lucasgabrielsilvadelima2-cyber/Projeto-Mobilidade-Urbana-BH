# 🔍 Análise Técnica: Problema com API PBH e Solução Correta

## ❌ Problema com a Abordagem Atual (PowerShell Fallback)

### Por Que PowerShell Fallback É Uma Má Solução?

#### 1. **Não é Portável**
```python
if sys.platform != 'win32':
    raise Exception("PowerShell fallback disponível apenas no Windows")
```
- ❌ Funciona apenas no Windows
- ❌ Não funciona em: Linux, macOS, containers Docker, ambientes cloud (AWS Lambda, Azure Functions, GCP)
- ❌ Impede deploy em produção em 99% dos cenários modernos

#### 2. **Dependência Externa**
- ❌ Requer PowerShell instalado (nem sempre disponível)
- ❌ Adiciona camada de complexidade (subprocess, parsing de output)
- ❌ Dificulta debug e tratamento de erros
- ❌ Performance inferior (overhead de spawn de processo)

#### 3. **Não Resolve o Problema Real**
- ❌ É um workaround, não uma solução
- ❌ Esconde o problema ao invés de entendê-lo
- ❌ Pode quebrar a qualquer momento se API mudar

#### 4. **Problemas de Segurança**
- ❌ Executa comandos shell arbitrários
- ❌ Risco de shell injection se URL não for validada
- ❌ Dificulta auditoria de segurança

---

## 🔍 O Problema Real: WAF e TLS Fingerprinting

### O Que Realmente Acontece?

APIs modernas usam múltiplas camadas de proteção anti-bot:

#### 1. **User-Agent Blocking (Simples)**
```python
# ❌ Bloqueado: User-Agent padrão do requests
requests.get(url)  # User-Agent: python-requests/2.31.0

# ✅ Pode funcionar: User-Agent de navegador
requests.get(url, headers={'User-Agent': 'Mozilla/5.0...'})
```

#### 2. **TLS/SSL Fingerprinting (Avançado)**
Mesmo com User-Agent correto, o servidor pode identificar a biblioteca Python por:
- **Ordem de ciphers no SSL handshake**
- **Extensões TLS suportadas**
- **Versão do protocolo TLS**
- **Características da biblioteca SSL (OpenSSL vs BoringSSL vs Schannel)**

```
Python requests → OpenSSL → Assinatura TLS única
PowerShell → Schannel (Windows) → Assinatura TLS diferente
Navegador Chrome → BoringSSL → Assinatura TLS "legítima"
```

#### 3. **Header Fingerprinting**
Ordem e formatação dos headers HTTP também identificam bibliotecas:
```
Python requests:
  User-Agent: ...
  Accept-Encoding: gzip, deflate
  Accept: */*
  Connection: keep-alive

Navegador real:
  Host: ...
  Connection: keep-alive
  User-Agent: ...
  Accept: text/html,application/xhtml+xml,...
  Accept-Encoding: gzip, deflate, br
  Accept-Language: pt-BR,pt;q=0.9
```

---

## ✅ Soluções Python Corretas (Por Ordem de Preferência)

### Solução 1: **curl_cffi** (Recomendada) ⭐

**Por que funciona?**
- Emula fingerprint TLS de navegadores reais (Chrome, Firefox, Safari)
- Usa libcurl com impersonation perfeita
- Biblioteca Python, sem dependências externas

```python
from curl_cffi import requests

# Emula Chrome 110 perfeitamente
response = requests.get(
    'https://temporeal.pbh.gov.br/v1/posicoes',
    impersonate="chrome110"
)
```

**Vantagens:**
- ✅ Funciona em qualquer plataforma (Windows, Linux, macOS, Docker)
- ✅ TLS fingerprint idêntico ao navegador real
- ✅ Performance excelente
- ✅ API compatível com requests
- ✅ Mantido ativamente

**Instalação:**
```bash
pip install curl-cffi
```

---

### Solução 2: **httpx** com HTTP/2

**Por que pode funcionar?**
- Suporta HTTP/2 (browsers modernos usam)
- Headers e comportamento mais próximo de navegador
- Biblioteca moderna e bem mantida

```python
import httpx

client = httpx.Client(http2=True)
response = client.get(
    'https://temporeal.pbh.gov.br/v1/posicoes',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://temporeal.pbh.gov.br/',
        'Origin': 'https://temporeal.pbh.gov.br',
    }
)
```

**Vantagens:**
- ✅ Portável
- ✅ API moderna (async/await support)
- ✅ HTTP/2 support
- ✅ Timeout robusto

---

### Solução 3: **cloudscraper**

**Por que funciona?**
- Desenvolvido especificamente para bypass de Cloudflare e WAFs similares
- Resolve challenges JavaScript automaticamente
- Mantém sessão com cookies

```python
import cloudscraper

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)
response = scraper.get('https://temporeal.pbh.gov.br/v1/posicoes')
```

**Vantagens:**
- ✅ Feito para bypass de WAF
- ✅ Resolve challenges automaticamente
- ✅ Portável

---

### Solução 4: **requests com SSL Context Customizado**

**Por que pode funcionar?**
- Customiza comportamento SSL/TLS
- Adiciona headers completos como navegador

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', TLSAdapter())

response = session.get(
    'https://temporeal.pbh.gov.br/v1/posicoes',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://temporeal.pbh.gov.br/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
)
```

---

## 🎯 Recomendação Final

### Use **curl_cffi** como solução principal:

```python
from curl_cffi import requests

def fetch_api_data(url: str) -> str:
    """
    Faz requisição à API com fingerprint de navegador real.
    
    Funciona porque:
    - TLS fingerprint idêntico ao Chrome
    - Headers e comportamento de navegador real
    - Portável (funciona em qualquer plataforma)
    """
    try:
        response = requests.get(
            url,
            impersonate="chrome110",
            timeout=30
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Erro ao acessar API: {e}")
        raise
```

### Fallback Order (se necessário):
1. **curl_cffi** (Chrome impersonation)
2. **httpx** com HTTP/2
3. **cloudscraper**
4. **requests** com SSL customizado

### ❌ NUNCA use:
- PowerShell subprocess
- Selenium/Playwright para simples API calls
- Shell commands (curl, wget) via subprocess

---

## 📊 Comparação de Soluções

| Solução | Portabilidade | TLS Fingerprint | Performance | Manutenção | Recomendação |
|---------|--------------|-----------------|-------------|------------|--------------|
| **curl_cffi** | ✅ Todas plataformas | ✅ Perfeito | ✅ Excelente | ✅ Ativa | ⭐⭐⭐⭐⭐ |
| **httpx** | ✅ Todas plataformas | ⚠️ Bom | ✅ Excelente | ✅ Ativa | ⭐⭐⭐⭐ |
| **cloudscraper** | ✅ Todas plataformas | ✅ Muito bom | ⚠️ Médio | ✅ Ativa | ⭐⭐⭐⭐ |
| **requests + SSL** | ✅ Todas plataformas | ⚠️ Básico | ✅ Excelente | ➖ Manual | ⭐⭐⭐ |
| **PowerShell** | ❌ Só Windows | ✅ Bom | ❌ Ruim | ❌ Frágil | ❌❌❌ |

---

## 🔧 Implementação Correta

### Código Atualizado para `ingestion.py`:

```python
"""
Camada Bronze - Ingestão de Dados com fetch robusto.
"""

import logging
from typing import Optional
from curl_cffi import requests as cf_requests

logger = logging.getLogger(__name__)


class OnibusTempoRealIngester(BronzeDataIngester):
    """Ingestor de dados de ônibus em tempo real."""
    
    def _fetch_data(self) -> str:
        """
        Faz requisição à API com emulação de navegador real.
        
        Usa curl_cffi para emular fingerprint TLS do Chrome, 
        contornando proteções WAF de forma legítima e portável.
        
        Returns:
            Conteúdo da resposta como string
            
        Raises:
            Exception: Se falhar após todas tentativas
        """
        # Lista de impersonations para tentar (em ordem)
        impersonations = [
            "chrome110",
            "chrome107", 
            "safari15_5",
            "firefox109"
        ]
        
        last_error = None
        
        for impersonate in impersonations:
            try:
                logger.info(f"🔄 Tentando acessar API (emulando {impersonate})...")
                
                response = cf_requests.get(
                    self.api_url,
                    impersonate=impersonate,
                    timeout=30,
                    headers={
                        'Accept': '*/*',
                        'Accept-Language': 'pt-BR,pt;q=0.9',
                        'Referer': 'https://temporeal.pbh.gov.br/',
                    }
                )
                
                response.raise_for_status()
                logger.info(f"✅ Sucesso com {impersonate}")
                return response.text
                
            except Exception as e:
                logger.warning(f"⚠️ Falhou com {impersonate}: {e}")
                last_error = e
                continue
        
        # Se todas tentativas falharem
        logger.error(f"❌ Todas tentativas falharam. Último erro: {last_error}")
        raise Exception(f"Não foi possível acessar API após múltiplas tentativas: {last_error}")
    
    def extract(self) -> pd.DataFrame:
        """
        Extrai dados de posicionamento dos ônibus.
        
        Returns:
            DataFrame com os dados extraídos
        """
        lineage = DataLineage(
            source="PBH Tempo Real API",
            operation="extract_onibus_posicoes"
        )
        
        try:
            # Fetch dos dados usando método robusto
            text_content = self._fetch_data()
            lineage.add_metadata("method", "curl_cffi")
            
            # ... resto do código de parsing ...
```

---

## 📝 Conclusão

### O Problema Real Era:
**TLS/SSL Fingerprinting** - A API identifica e bloqueia requisições da biblioteca `requests` padrão por sua assinatura TLS única.

### A Solução Correta É:
**curl_cffi** - Emula perfeitamente o fingerprint TLS de navegadores reais, de forma portável e eficiente.

### Por Que Não PowerShell:
- ❌ Não portável (só Windows)
- ❌ Não escalável (containers, cloud)
- ❌ Performance ruim (subprocess overhead)
- ❌ Difícil manutenção
- ❌ Riscos de segurança

### Benefícios da Solução Correta:
- ✅ Funciona em qualquer plataforma
- ✅ Deploy em Docker/Kubernetes/Cloud
- ✅ Performance excelente
- ✅ Código limpo e mantível
- ✅ Sem dependências de sistema operacional

---

**Data da Análise:** 19 de fevereiro de 2026  
**Status:** Solução correta identificada e documentada  
**Próximo Passo:** Implementar curl_cffi no código de ingestão
