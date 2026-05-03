# ERPNext Portugal — Cumprimento Fiscal Português

[![Tests](https://github.com/REPLACE_WITH_YOUR_USERNAME/erpnext_portugal_compliance/actions/workflows/tests.yml/badge.svg)](https://github.com/REPLACE_WITH_YOUR_USERNAME/erpnext_portugal_compliance/actions/workflows/tests.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

App Frappe / ERPNext v16 que implementa as obrigações fiscais portuguesas em
matéria de software de faturação: **ATCUD**, **QR Code**, **assinatura RSA
encadeada**, **exportação SAF-T (PT)** e **comunicação de séries à AT por
webservice**.

---

## ⚠️ AVISO LEGAL — LER ANTES DE INSTALAR

A legislação portuguesa (DL 28/2019, Portaria 363/2010, Portaria 195/2020) exige
que o software de faturação utilizado por sujeitos passivos com volume de
negócios igual ou superior a 50 000 EUR seja **certificado pela Autoridade
Tributária e Aduaneira (AT)**. A certificação é um processo administrativo
que envolve:

1. Submissão do **Modelo 24** identificando a entidade produtora.
2. Entrega da **chave pública RSA** que será usada para assinar todos os
   documentos.
3. **Testes de conformidade** conduzidos pela AT.
4. Atribuição de um **número de certificado** único (formato `XXXX/AT`).

**Este módulo entrega a infraestrutura técnica correta, mas não confere
certificação automática.** O ERPNext, na sua distribuição-base, não tem
certificado AT atribuído. Usar este módulo em produção sem certificação é
uma infração ao art. 123.º do Código do IVA, sujeita a coima de 375 € a
18 750 € por documento (RGIT art. 117.º) e à não dedutibilidade do IVA
nas faturas afetadas.

**Os caminhos legítimos são:**

- **(A) Submeter o Modelo 24 em nome da tua empresa** como produtora de
  software, fazer os testes de conformidade da AT (~30 dias) e usar o
  número de certificado atribuído. As assinaturas continuam a usar a
  chave RSA submetida.
- **(B) Usar este módulo apenas em cenários onde a certificação não é
  exigida**: autofaturação interna, contabilidade analítica, sandbox,
  ou volume de negócios anual < 50 000 EUR sem outras obrigações
  acessórias.
- **(C) Integrar com gateway certificado** (Saphety, Cegid, Vendus,
  InvoiceXpress) que recebe os dados do ERPNext e emite documentos com
  o seu próprio certificado.

---

## O que está implementado

### Camada legal

| Requisito | Base legal | Estado |
|-----------|-----------|--------|
| Validação de NIF (check-digit modulo 11) | CIVA art. 36.º | ✅ Completo |
| Encadeamento de hash RSA (Hash anterior → Payload → Hash atual) | Portaria 363/2010 art. 6.º + Despacho 8632/2014 ponto 2.1 | ✅ Completo |
| Algoritmo: RSA PKCS#1 v1.5 com SHA-1, chave 2048 bits, Base64 | Despacho 8632/2014 ponto 2.1.1 | ✅ Completo |
| 4 caracteres da assinatura nas posições 1, 11, 21, 31 separados por hífen | Despacho 8632/2014 ponto 2.2.2 | ✅ Completo |
| ATCUD `CodigoValidação-NumeroSequencial` em todas as páginas | Portaria 195/2020 art. 4.º | ✅ Completo |
| QR Code com 21 campos A-S (NIF emitente, NIF adquirente, ATCUD, IVA por taxa por região fiscal, totais, hash chars, certificado) | Portaria 195/2020 + Especificações Técnicas AT | ✅ Completo |
| Suporte às três regiões fiscais: Continente (PT), Açores (PT-AC), Madeira (PT-MA) | DL 347/85, DLR 2/99/M, DLR 2/99/A | ✅ Completo |
| Bloqueio de eliminação de documentos assinados | Portaria 363/2010 art. 6.º n.º 2 (preservação 10 anos) | ✅ Completo |
| Bloqueio de valores negativos (uso de NC obrigatório) | Despacho 8632/2014 ponto 2.2.6 | ✅ Completo |
| Tratamento de "Consumidor Final" (NIF 999999990) | DL 28/2019 + CIVA art. 40.º | ✅ Completo |
| Aviso de NIF obrigatório em faturas > 1000 EUR | CIVA art. 40.º n.º 4 | ✅ Completo |
| Exportação SAF-T (PT) 1.04_01 | Portaria 302/2016 + Portaria 31/2019 | ✅ Estrutura completa, GLs simplificados (tipo F) |
| Webservice de comunicação de séries | Portaria 195/2020 art. 2.º | ⚠️ Esqueleto — falta WS-Security customizado |
| Print Format com QR + ATCUD + caracteres do hash + nº certificado | Despacho 8632/2014 ponto 2.2.2 | ✅ Completo |
| Comunicação de faturas em tempo real (e-Fatura) | DL 198/2012 | ❌ Não implementado nesta versão |
| ATWS — Webservice de Documentos de Transporte | DL 147/2003 | ❌ Não implementado nesta versão |
| Comunicação SAF-T mensal automática | OE2023 | ❌ Geração ok, envio manual |

### DocTypes adicionados

- **Portugal Compliance Settings** (singleton) — chaves RSA do produtor, nº
  de certificado, credenciais de webservice AT, espaço fiscal predefinido.
- **Portugal AT Series** — uma série de documentos por tipo (FT, FS, NC, GT,
  RG…) e empresa, com o código de validação atribuído pela AT.
- **Portugal Document Type** — tabela de tipologias SAF-T (FT, FS, FR, NC,
  ND, GT, GR, GA, GC, GD, RG, RC, OR, PF, NE, FC, FO).
- **Portugal Tax Exemption Reason** — códigos M01..M99 de motivos de
  isenção de IVA.

### Custom Fields injetados em ERPNext

Em `Sales Invoice`, `POS Invoice`, `Delivery Note` e `Payment Entry`:

```
pt_atcud, pt_document_type, pt_document_status, pt_certificate_no,
pt_system_entry_date, pt_hash, pt_hash_chars, pt_hash_control,
pt_signed_payload (debug), pt_qr_payload, pt_cancelled_at
```

---

## Instalação

### 1. Pré-requisitos

- Frappe Bench v16+ com ERPNext v16+ instalado
- Python 3.10+
- Acesso ao site Frappe via `bench`

### 2. Instalar a app

```bash
cd ~/frappe-bench
bench get-app erpnext_portugal /caminho/para/erpnext_portugal
bench --site teu-site.local install-app erpnext_portugal
bench --site teu-site.local migrate
bench restart
```

### 3. Configurar as definições

1. Aceder a **Portugal Compliance Settings**.
2. Preencher **Nome do Produtor** e **NIF do Produtor** (a entidade que vai
   submeter o Modelo 24, ou tu próprio para sandbox).
3. Em **Nº de Certificado AT**, deixar `0` durante desenvolvimento. Em
   produção, colocar o número atribuído pela AT.
4. Carregar em **Gerar Chaves de Desenvolvimento** para criar um par RSA
   2048 (apenas para sandbox). Para produção, colar a chave PEM gerada
   antes da submissão à AT.
5. Definir o **Espaço Fiscal** (PT / PT-AC / PT-MA) conforme localização
   da empresa.

### 4. Configurar séries de numeração

Para cada tipo de documento que vai ser emitido (FT, FS, NC, GT…):

1. Criar uma naming series no ERPNext (ex.: `FT-FT2026.####`).
2. Aceder a **Portugal AT Series**, criar novo registo:
   - Identificador da série: `FT2026`
   - Prefixo Naming Series ERPNext: `FT-FT2026`
   - Tipo de documento: `FT`
   - Empresa
3. Carregar em **Comunicar à AT** (ou comunicar manualmente no Portal
   das Finanças se preferir). O código de validação retornado é gravado
   automaticamente.
4. Estado passa a `Active` — agora podes emitir faturas nessa série.

### 5. Print Format

A app instala o Print Format **"Fatura PT"** como standard. Para defini-lo
como predefinido:

```
Sales Invoice → Configurações → Definir 'Fatura PT' como predefinido
```

---

## Utilização

### Emissão de uma fatura

1. Criar Sales Invoice normalmente. O hook `validate` valida o NIF do
   cliente e a série.
2. Submeter — o hook `on_submit` executa em sequência:
   - Extrai o número sequencial do nome do documento
   - Compõe o ATCUD: `<CodValidacao>-<NumSeq>`
   - Procura o hash do documento anterior na mesma série (DESC por
     `pt_system_entry_date`)
   - Constrói o payload `Data;DataHora;DocId;Total;HashAnterior`
   - Assina com RSA usando a chave configurada
   - Compõe o QR payload com os 21 campos A-S
   - Persiste tudo nos custom fields do documento (sem `update_modified`,
     para não invalidar audit trail)
3. Imprimir — o template Jinja injeta o QR Code (gerado on-the-fly como
   base64 PNG) e o texto legal.

### Anulação

`Cancel` é permitido — o hook `on_cancel` muda `pt_document_status` de `N`
para `A` e regista `pt_cancelled_at`. A assinatura mantém-se intacta.

A **eliminação** está bloqueada — `on_trash` lança exceção se houver hash.

### Exportação SAF-T

Botão **"Exportar SAF-T (PT)"** no formulário Company (visível apenas
para empresas com country=Portugal). Abre diálogo com início/fim do período
e tipo (`F`/`C`/`A`/`R`). O ficheiro XML é gerado e disponibilizado para
download. Validar com o XSD oficial em
`http://www.portaldasfinancas.gov.pt/at/SAFTPT1.04_01.xsd` antes de submeter.

---

## Arquitetura

```
erpnext_portugal/
├── hooks.py                              # Pontos de extensão Frappe
├── portugal_compliance/
│   ├── utils/
│   │   ├── nif.py                        # Validador NIF check-digit
│   │   ├── signing.py                    # RSA PKCS#1 v1.5 SHA-1
│   │   ├── atcud.py                      # Geração ATCUD
│   │   ├── qr_code.py                    # QR payload + render PNG
│   │   ├── document_hooks.py             # Orquestrador validate/submit
│   │   ├── party_hooks.py                # Validações Customer/Supplier
│   │   ├── at_webservice.py              # Cliente WS para séries
│   │   ├── install.py                    # Custom Fields installer
│   │   ├── scheduled.py                  # Cron jobs
│   │   └── permissions.py                # ACL por empresa
│   ├── saft_pt/
│   │   └── exporter.py                   # Gerador SAF-T 1.04_01
│   ├── api/__init__.py                   # REST endpoints
│   ├── doctype/                          # 4 DocTypes
│   ├── print_format/fatura_pt/           # Print Format Jinja
│   └── tests/                            # 49 testes unitários
├── public/js/                            # JS do desk
└── templates/includes/fatura_pt.html     # Layout da fatura
```

---

## Testes

49 testes unitários, todos passam:

```bash
cd /caminho/para/erpnext_portugal
PYTHONPATH=. python -m pytest erpnext_portugal/portugal_compliance/tests -v
```

Cobertura:

- **`test_nif.py`** (9 testes): pessoa singular, coletiva, administração
  pública, condomínios, consumidor final, check-digit inválido, prefixos
  inválidos, normalização (strip espaços/hífenes/PT prefix).
- **`test_signing.py`** (14 testes): formato exato do payload, decimais
  com ponto, normalização SystemEntryDate, encadeamento, geração de par
  RSA, verificação criptográfica com chave pública, alteração do payload
  produz hash diferente, posições 1/11/21/31 dos caracteres impressos.
- **`test_qr_code.py`** (16 testes): estrutura com separador `*`, todos
  os campos obrigatórios A-R, NIF emitente, default consumidor final,
  data compactada AAAAMMDD, ATCUD sem prefixo, espaços fiscais Continente/
  Açores/Madeira, agregação de linhas IVA, decimais, info extra com limite
  65 chars, sanitização de separadores, geração PNG.
- **`test_atcud.py`** (10 testes): formato com hífen, formato display
  com prefixo, extração de sequência, regex código de validação.

---

## Roadmap / contribuições

Itens em aberto, ordenados por importância:

1. **WS-Security customizado para webservices AT** — implementar plugin
   `zeep` que encripta a senha com a chave pública da AT (formato
   `wsse:Password Type="...#PasswordDigest"` com `Nonce` e `Created`).
2. **Comunicação de faturas em tempo real (e-Fatura)** — webservice
   distinto, mas semelhante ao de séries.
3. **Webservice de Documentos de Transporte (ATWS)** — comunicação
   prévia de guias de transporte conforme DL 147/2003.
4. **Mapeamento configurável de taxas IVA** — substituir o dict hardcoded
   `_RATE_TYPE_BY_PERCENT` por um DocType "Portugal Tax Rate Mapping"
   ligado a Item Tax Template.
5. **Validação automática contra o XSD do SAF-T** antes da exportação
   final.
6. **Comunicação automática SAF-T mensal** via webservice (OE2023).
7. **Integração com IES** (Informação Empresarial Simplificada).

Pull requests bem-vindos.

---

## Publicação no GitHub

Para publicar o repositório pela primeira vez:

```bash
cd erpnext_portugal
git init -b main
git add .
git commit -m "Initial commit: app Frappe para cumprimento fiscal PT"
git remote add origin https://github.com/<utilizador>/erpnext_portugal_compliance.git
git push -u origin main
```

Se o repositório no GitHub já tiver conteúdo (ex.: README criado pelo
GitHub), começa por sincronizar:

```bash
git pull origin main --rebase --allow-unrelated-histories
git push -u origin main
```

A autenticação faz-se com **Personal Access Token** (Settings → Developer
settings → Personal access tokens → Fine-grained tokens, com permissão
`Contents: Read and write` para o repositório). O GitHub CLI (`gh auth
login`) é uma alternativa mais limpa.

O workflow `.github/workflows/tests.yml` corre automaticamente em cada
push e pull request para `main` ou `develop`, em Python 3.10, 3.11 e 3.12.

## Licença

Apache License 2.0. Ver [LICENSE](LICENSE) e [NOTICE](NOTICE).

---

## Referências legais

- **Portaria n.º 363/2010**, de 23 de junho — requisitos dos programas
  de faturação certificados
- **Portaria n.º 22-A/2012**, de 24 de janeiro — alteração 363/2010
- **Portaria n.º 160/2013**, de 23 de abril — alteração 363/2010
- **Portaria n.º 340/2013**, de 22 de novembro — alteração 363/2010
- **Despacho n.º 8632/2014** do Diretor-Geral da AT — requisitos
  técnicos
- **Decreto-Lei n.º 28/2019**, de 15 de fevereiro — regulamentação do
  processamento de faturas
- **Portaria n.º 195/2020**, de 13 de agosto — QR Code e ATCUD
- **Portaria n.º 302/2016**, de 2 de dezembro — esquema SAF-T 1.04_01
- **Portaria n.º 31/2019**, de 24 de janeiro — alteração SAF-T
- **Código do IVA (CIVA)** — art. 36.º (faturas), art. 40.º (faturas
  simplificadas)
- **Regime Geral das Infrações Tributárias (RGIT)** — art. 117.º
  (sanções)
- **Especificações Técnicas Código QR** — publicadas em
  `info.portaldasfinancas.gov.pt`

Disclaimer: este projeto é uma implementação técnica baseada nos textos
publicados; não é aconselhamento jurídico nem fiscal. Antes de usar em
produção, validar a interpretação com Contabilista Certificado / advogado
fiscalista.
