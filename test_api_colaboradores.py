#!/usr/bin/env python3
"""
Script para testar a API de colaboradores diretamente
"""
import requests
import json

# Dados do usuário (obtidos do banco)
api_key = "h4ADLfG3Ui0QxHdbHyT5J0F5m8D9NZ"
bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6WyJzaWx2YS5hZG1pbmlzdHJhZG9yIiwic2lsdmEuYWRtaW5pc3RyYWRvciJdLCJqdGkiOiIyZThhMTk0M2NkMDY0MWE1OWNiZDE0YTRkZjBmNDI5NCIsImFwaUtleSI6Img0QURMZkczVWkwUXhIZGJIeVQ1SjBGNW04RDlOWiIsImFwaVRva2VuIjoicHFjRExmRzNVZ0NYYlluMGxTb3BITGpvQ0IwYm4iLCJuYmYiOjE3NTIzNTMxODUsImV4cCI6MTc1MjM2ODgyNSwiaWF0IjoxNzUyMzUzMTg1LCJpc3MiOiJBdXZvX0FwaV9QdWJsaWNhIiwiYXVkIjoiVXN1YXJpb19BcGkifQ.RZKk75hqgZjraShL7hEVd4bJlhaU4DrZBjkC7H99Gwk"

# URL da API de colaboradores
url = "https://api.auvo.com.br/v2/users/?pageSize=999"

# Headers da requisição
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {bearer_token}'
}

print(f"Testando API de colaboradores...")
print(f"URL: {url}")
print(f"Headers: {headers}")

try:
    # Faz a requisição para a API
    response = requests.get(url, headers=headers, timeout=30)
    
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Resposta JSON recebida com sucesso")
            print(f"Chaves na resposta: {list(data.keys())}")
            
            if 'result' in data:
                result = data['result']
                print(f"Chaves em 'result': {list(result.keys())}")
                
                if 'entityList' in result:
                    entity_list = result['entityList']
                    print(f"Número de entidades: {len(entity_list)}")
                    
                    # Mostra os primeiros 3 colaboradores
                    for i, entity in enumerate(entity_list[:3]):
                        print(f"Colaborador {i+1}:")
                        print(f"  userId: {entity.get('userId')}")
                        print(f"  name: {entity.get('name')}")
                        print(f"  Todas as chaves: {list(entity.keys())}")
                else:
                    print("Chave 'entityList' não encontrada em 'result'")
            else:
                print("Chave 'result' não encontrada na resposta")
                
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            print(f"Resposta raw: {response.text[:500]}...")
    else:
        print(f"Erro HTTP {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Erro na requisição: {e}")
