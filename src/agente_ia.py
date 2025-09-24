# -*- coding: utf-8 -*-
"""
Agente de IA - Imersão Alura + Google Gemini
Adaptado para VS Code com todas as funcionalidades originais
"""

import os
import re
import pathlib
from typing import List, Dict
from dotenv import load_dotenv
from google.generativeai import configure, GenerativeModel
import PyPDF2
from pathlib import Path

# Carrega variáveis de ambiente
load_dotenv()

class AgenteIACompleto:
    def __init__(self):
        # Configurações da API
        self.GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
        configure(api_key=self.GOOGLE_API_KEY)
        
        # Modelos
        self.llm = GenerativeModel('gemini-1.5-flash')
        self.llm_triagem = GenerativeModel('gemini-1.5-flash')
        
        # modelo pro (mais inteligente)
        # self.llm = GenerativeModel('gemini-1.5-pro')
        # self.llm_triagem = GenerativeModel('gemini-1.5-pro')

        # Configurações do sistema
        self.TRIAGEM_PROMPT = (
            "Você é um triador de Service Desk para políticas internas da empresa Carraro Desenvolvimento. "
            "Dada a mensagem do usuário, retorne SOMENTE um JSON com:\n"
            "{\n"
            '  "decisao": "AUTO_RESOLVER" | "PEDIR_INFO" | "ABRIR_CHAMADO",\n'
            '  "urgencia": "BAIXA" | "MEDIA" | "ALTA",\n'
            '  "campos_faltantes": ["..."]\n'
            "}\n"
            "Regras:\n"
            '- **AUTO_RESOLVER**: Perguntas claras sobre regras ou procedimentos descritos nas políticas.\n'
            '- **PEDIR_INFO**: Mensagens vagas ou que faltam informações para identificar o tema ou contexto.\n'
            '- **ABRIR_CHAMADO**: Pedidos de exceção, liberação, aprovação ou acesso especial.'
        )
        
        self.KEYWORDS_ABRIR_TICKET = ["aprovação", "exceção", "liberação", "abrir ticket", "abrir chamado", "acesso especial"]
        
        # Inicializa documentos
        self.docs = []
        self.carregar_documentos()
    
    def carregar_documentos(self):
        """Carrega documentos PDF da pasta data/"""
        data_path = Path("data")
        if data_path.exists():
            for pdf_file in data_path.glob("*.pdf"):
                try:
                    with open(pdf_file, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num, page in enumerate(pdf_reader.pages):
                            self.docs.append({
                                'content': page.extract_text(),
                                'source': pdf_file.name,
                                'page': page_num
                            })
                    print(f"✅ Carregado: {pdf_file.name}")
                except Exception as e:
                    print(f"❌ Erro ao carregar {pdf_file.name}: {e}")
        else:
            print("ℹ️  Pasta 'data' não encontrada. O agente funcionará sem documentos PDF.")
            data_path.mkdir(exist_ok=True)
    
    def triagem(self, mensagem: str) -> Dict:
        """Faz a triagem da mensagem do usuário"""
        try:
            prompt = f"""
            {self.TRIAGEM_PROMPT}
            
            Mensagem do usuário: "{mensagem}"
            
            Retorne APENAS o JSON, sem nenhum texto adicional.
            """
            response = self.llm_triagem.generate_content(prompt)
            
            # Limpa a resposta e tenta extrair o JSON
            texto = response.text.strip()
            
            # Tenta encontrar o JSON na resposta
            if "AUTO_RESOLVER" in texto:
                return {"decisao": "AUTO_RESOLVER", "urgencia": "MEDIA", "campos_faltantes": []}
            elif "ABRIR_CHAMADO" in texto:
                return {"decisao": "ABRIR_CHAMADO", "urgencia": "ALTA", "campos_faltantes": []}
            elif "PEDIR_INFO" in texto:
                return {"decisao": "PEDIR_INFO", "urgencia": "BAIXA", "campos_faltantes": ["mais detalhes"]}
            else:
                # Se não identificar, faz uma análise simples
                pergunta_lower = mensagem.lower()
                if any(palavra in pergunta_lower for palavra in ["reembolsar", "internet", "casa", "home office", "política", "regra", "como funciona", "procedimento"]):
                    return {"decisao": "AUTO_RESOLVER", "urgencia": "MEDIA", "campos_faltantes": []}
                elif any(palavra in pergunta_lower for palavra in ["aprovação", "exceção", "liberação", "acesso especial"]):
                    return {"decisao": "ABRIR_CHAMADO", "urgencia": "ALTA", "campos_faltantes": []}
                else:
                    return {"decisao": "PEDIR_INFO", "urgencia": "BAIXA", "campos_faltantes": ["mais detalhes"]}
                    
        except Exception as e:
            print(f"❌ Erro na triagem: {e}")
            # Fallback baseado nas palavras-chave
            pergunta_lower = mensagem.lower()
            if any(palavra in pergunta_lower for palavra in ["reembolsar", "internet", "casa", "home office", "política", "regra"]):
                return {"decisao": "AUTO_RESOLVER", "urgencia": "MEDIA", "campos_faltantes": []}
            elif any(palavra in pergunta_lower for palavra in ["aprovação", "exceção", "liberação", "acesso especial"]):
                return {"decisao": "ABRIR_CHAMADO", "urgencia": "ALTA", "campos_faltantes": []}
            else:
                return {"decisao": "PEDIR_INFO", "urgencia": "BAIXA", "campos_faltantes": ["mais detalhes"]}

    def buscar_em_documentos(self, pergunta: str) -> List[Dict]:
        """Busca a pergunta nos documentos carregados"""
        resultados = []
        for doc in self.docs:
            if pergunta.lower() in doc['content'].lower():
                resultados.append({
                    'documento': doc['source'],
                    'pagina': doc['page'] + 1,
                    'trecho': self.extrair_trecho(doc['content'], pergunta)
                })
        return resultados[:3]  # Retorna no máximo 3 resultados
    
    def extrair_trecho(self, texto: str, query: str, janela: int = 240) -> str:
        """Extrai um trecho relevante do texto"""
        txt = re.sub(r"\s+", " ", texto or "").strip()
        termos = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) >= 4]
        pos = -1
        for t in termos:
            pos = txt.lower().find(t)
            if pos != -1: 
                break
        if pos == -1: 
            pos = 0
        ini, fim = max(0, pos - janela//2), min(len(txt), pos + janela//2)
        return txt[ini:fim]
    
    def perguntar_politica_RAG(self, pergunta: str) -> Dict:
        """Faz uma pergunta usando RAG nos documentos - VERSÃO CRIATIVA"""
        docs_relacionados = self.buscar_em_documentos(pergunta)
        
        if not docs_relacionados:
            # Se não encontrou nos documentos, usa o Gemini diretamente
            try:
                prompt_criativo = f"""
                🎯 **Você é um assistente super simpático e criativo do service desk da Carraro!** 
                
                **Seu estilo:**
                - 😊 Super amigável e acolhedor
                - 💡 Prático e útil 
                - 🎨 Com personalidade (pode usar emojis!)
                - 📚 Respostas claras mas com toque humano
                
                **Pergunta do usuário:** {pergunta}
                
                **Dê uma resposta completa, criativa e que realmente ajude a pessoa!** 
                Se não souber algo, seja honesto mas mantenha o estilo simpático! ✨
                """
                resposta = self.llm.generate_content(prompt_criativo)
                return {
                    "answer": resposta.text,
                    "citacoes": [],
                    "contexto_encontrado": False
                }
            except Exception as e:
                return {
                    "answer": "🤖 Opa, tive um probleminha técnico aqui! Pode tentar de novo?",
                    "citacoes": [],
                    "contexto_encontrado": False
                }
        
        # Se encontrou documentos, usa no contexto
        contexto = "\n".join([f"📄 **Documento:** {doc['documento']}, Página {doc['pagina']}:\n{doc['trecho']}" 
                             for doc in docs_relacionados])
        
        prompt_contexto = f"""
        🎯 **Você é um especialista super simpático da Carraro!** 
        
        **Seu estilo:**
        - 😊 Amigável e acolhedor
        - 💡 Prático e direto ao ponto
        - 🎨 Com toque pessoal (emoji quando fizer sentido!)
        - 📚 Baseado nos documentos oficiais
        
        **Documentos relevantes:**
        {contexto}
        
        **Pergunta do usuário:** {pergunta}
        
        **Responda de forma:** 
        - ✅ Clara e objetiva
        - 🤝 Acolhedora e útil
        - 🎯 Baseada nos documentos quando possível
        - 💬 Com naturalidade humana
        
        Se a informação não estiver nos documentos, seja honesto mas mantenha o estilo simpático! 😊
        """
        
        try:
            resposta = self.llm.generate_content(prompt_contexto)
            return {
                "answer": resposta.text,
                "citacoes": docs_relacionados,
                "contexto_encontrado": True
            }
        except Exception as e:
            return {
                "answer": "⚠️ Opa, tive um instante de bug! Pode reformular a pergunta?",
                "citacoes": docs_relacionados,
                "contexto_encontrado": True
            }
    
    def executar_fluxo_completo(self, pergunta: str) -> Dict:
        """Executa o fluxo completo do agente - VERSÃO CRIATIVA"""
        print(f"🔍 Analisando pergunta: {pergunta}")
        
        # 1. Triagem
        triagem_result = self.triagem(pergunta)
        print(f"🎯 Triagem: {triagem_result['decisao']} (Urgência: {triagem_result['urgencia']})")
        
        # 2. Decisão baseada na triagem
        if triagem_result['decisao'] == "AUTO_RESOLVER":
            resposta_rag = self.perguntar_politica_RAG(pergunta)
            
            if resposta_rag['contexto_encontrado']:
                return {
                    "pergunta": pergunta,
                    "triagem": triagem_result,
                    "resposta": resposta_rag['answer'],
                    "citacoes": resposta_rag['citacoes'],
                    "acao_final": "AUTO_RESOLVER"
                }
            else:
                # Fallback: verifica keywords para abrir chamado
                if any(k in pergunta.lower() for k in self.KEYWORDS_ABRIR_TICKET):
                    return {
                        "pergunta": pergunta,
                        "triagem": {**triagem_result, "decisao": "ABRIR_CHAMADO"},
                        "resposta": f"🚨 Entendi que você precisa de algo especial! Vou abrir um chamado com urgência {triagem_result['urgencia']} para nosso time. Em breve eles entrarão em contato! 📋✨",
                        "citacoes": [],
                        "acao_final": "ABRIR_CHAMADO"
                    }
                else:
                    campos = triagem_result.get('campos_faltantes', ['mais detalhes'])
                    return {
                        "pergunta": pergunta,
                        "triagem": {**triagem_result, "decisao": "PEDIR_INFO"},
                        "resposta": f"🤔 Hmm, preciso de mais detalhes para te ajudar melhor! Pode me contar mais sobre: {', '.join(campos)}? Assim consigo te direcionar perfeitamente! 💪",
                        "citacoes": [],
                        "acao_final": "PEDIR_INFO"
                    }
        
        elif triagem_result['decisao'] == "ABRIR_CHAMADO":
            return {
                "pergunta": pergunta,
                "triagem": triagem_result,
                "resposta": f"🚨 Entendido! Vou abrir um chamado com urgência {triagem_result['urgencia']} para você. Nosso time já foi acionado e em breve entrará em contato! 📋✨",
                "citacoes": [],
                "acao_final": "ABRIR_CHAMADO"
            }
        
        else:  # PEDIR_INFO
            campos = triagem_result.get('campos_faltantes', ['mais detalhes'])
            return {
                "pergunta": pergunta,
                "triagem": triagem_result,
                "resposta": f"🤔 Hmm, preciso de mais detalhes para te ajudar melhor! Pode me contar mais sobre: {', '.join(campos)}? Assim consigo te direcionar perfeitamente! 💪",
                "citacoes": [],
                "acao_final": "PEDIR_INFO"
            }

# Interface principal para teste
def main():
    print("=" * 60)
    print("🤖 AGENTE DE IA - IMERSÃO ALURA (SERVICE DESK)")
    print("=" * 60)
    
    agente = AgenteIACompleto()
    print(f"✅ Agente carregado! Documentos: {len(agente.docs)}")
    print("💡 Dica: Experimente perguntar sobre políticas, reembolsos ou aprovações!")
    
    while True:
        print("\n" + "-" * 50)
        pergunta = input("💬 Digite sua pergunta (ou 'sair' para encerrar): ").strip()
        
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("\n👋 Até mais! Foi um prazer ajudar! 😊")
            break
        
        if not pergunta:
            print("⚠️  Por favor, digite uma pergunta!")
            continue
        
        # Executa o fluxo completo
        resultado = agente.executar_fluxo_completo(pergunta)
        
        # Exibe resultados
        print(f"\n🎯 **DECISÃO:** {resultado['triagem']['decisao']}")
        print(f"⚠️  **URGÊNCIA:** {resultado['triagem']['urgencia']}")
        print(f"📋 **AÇÃO FINAL:** {resultado['acao_final']}")
        print(f"\n🤖 **RESPOSTA:** {resultado['resposta']}")
        
        if resultado['citacoes']:
            print("\n📚 **CITAÇÕES ENCONTRADAS:**")
            for citacao in resultado['citacoes']:
                print(f"   📄 **Documento:** {citacao['documento']}, **Página:** {citacao['pagina']}")
                print(f"   📖 **Trecho:** {citacao['trecho'][:100]}...")

if __name__ == "__main__":
    main()