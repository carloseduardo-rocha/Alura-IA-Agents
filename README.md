# 🤖 Agente de IA Inteligente - Imersão Alura

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)
![RAG](https://img.shields.io/badge/RAG-Advanced-FF6B00?style=for-the-badge)
![AI Agent](https://img.shields.io/badge/AI%20Agent-Autonomous-00C853?style=for-the-badge)

**Sistema inteligente de service desk com triagem automática e RAG**

[![GitHub](https://img.shields.io/badge/👁️_Ver_Código-181717?style=for-the-badge&logo=github&logoColor=white)](src/agente_ia.py)
[![Certificado](https://img.shields.io/badge/📜_Certificado_Alura-FF6B00?style=for-the-badge)](https://cursos.alura.com.br/immersion/certificate/1c584cf8-80ac-46eb-81b6-7b8259235cb7)

</div>

## 🎯 Sobre o Projeto

Desenvolvido durante a **Imersão IA: Agentes Autônomos Inteligentes** da Alura, este agente representa um sistema avançado de service desk que utiliza **triagem inteligente** e **RAG (Retrieval-Augmented Generation)** para atendimento automatizado com respostas contextuais e humanizadas.

## ⚡ Funcionalidades Principais

- **🤖 Triagem Automática Inteligente**: Classifica solicitações em 3 categorias automaticamente
- **🔍 Sistema RAG Avançado**: Busca em documentos PDF + geração contextualizada
- **💬 Respostas Humanizadas**: Comunicação natural com personalidade e emojis
- **🚨 Priorização por Urgência**: Define níveis de prioridade automaticamente
- **📚 Aprendizado Contínuo**: Melhora respostas com base no histórico

### 🎪 Fluxo de Decisão do Agente:


1. 📝 Usuário faz uma pergunta
2. 🎯 Agente classifica: AUTO_RESOLVER | PEDIR_INFO | ABRIR_CHAMADO
3. 🔍 Busca em base de conhecimento (RAG)
4. 💡 Gera resposta contextualizada e criativa
5. 📊 Retorna resultado com citações dos documentos



## 🛠️ Tecnologias Utilizadas

- **Python 3.9+** - Linguagem principal
- **Google Gemini API** - Modelos de linguagem avançados (gemini-1.5-flash)
- **RAG (Retrieval-Augmented Generation)** - Busca aumentada por recuperação
- **PyPDF2** - Processamento e análise de documentos PDF
- **Sistema de Triagem Automática** - Classificação inteligente baseada em contexto

## 📦 Estrutura do Projeto

```
Alura-IA-Agents/
├── src/
│   └── agente_ia.py
├── data/
├── .env.example
├── .gitignore
└── README.md
```

### 📋 Descrição dos Arquivos:
- **`src/agente_ia.py`** - Agente principal com sistema de triagem inteligente
- **`data/`** - Pasta para documentos PDF (base de conhecimento)
- **`.env.example`** - Modelo para variáveis de ambiente
- **`.gitignore`** - Proteção de arquivos sensíveis
- **`README.md`** - Esta documentação

### 🚀 Pré-requisitos
- Python 3.9+
- Conta no Google AI Studio (Gemini API)
- Git instalado

## 👨‍💻 Autor

<div align="center">

![Carlos Eduardo Rocha](https://avatars.githubusercontent.com/carloseduardo-rocha?s=100)

**Carlos Eduardo Rocha**  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/seu-perfil)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/carloseduardo-rocha)

</div>
<div align="center">
  
---
Desenvolvido com 💻 durante a Imersão IA da Alura

<div align="center">

**Certificado da Imersão IA**  
[![Alura](https://img.shields.io/badge/📜_Certificado_Alura-FF6B00?style=for-the-badge&logo=alura&logoColor=white)](https://cursos.alura.com.br/immersion/certificate/1c584cf8-80ac-46eb-81b6-7b8259235cb7)

</div>

"Transformando código em soluções inteligentes" 🚀

</div>
