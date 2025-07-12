#!/usr/bin/env python3
"""
Script para testar a sincronização de colaboradores
"""
import sys
import os
sys.path.append('/root/Relatorio_de_lucro-Auvo')

from App import create_app
from App.Controllers.Colaborador import ColaboradorController
from App.Models import Usuario

app = create_app()

with app.app_context():
    # Busca o primeiro usuário no banco
    usuario = Usuario.query.first()
    
    if not usuario:
        print("DEBUG: Nenhum usuário encontrado no banco")
        sys.exit(1)
    
    print(f"DEBUG: Usuário encontrado - ID: {usuario.id}, API Key: {usuario.chave_app}")
    
    # Testa a sincronização
    result = ColaboradorController.fetch_and_save_collaborators(usuario.id)
    
    print(f"DEBUG: Resultado da sincronização: {result}")
    
    # Verifica os colaboradores no banco
    colaboradores_result = ColaboradorController.get_collaborators_from_database()
    print(f"DEBUG: Colaboradores no banco: {colaboradores_result}")
