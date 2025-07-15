#!/usr/bin/env python3
"""
Script para limpeza do banco de dados do sistema de relatórios de lucro Auvo

Este script permite limpar dados específicos ou todos os dados do banco,
mantendo a estrutura das tabelas intacta.

Uso:
    python clean_database.py [opções]

Opções:
    --all               Limpa todas as tabelas (exceto usuários)
    --users             Limpa apenas usuários
    --products          Limpa apenas produtos
    --services          Limpa apenas serviços
    --collaborators     Limpa apenas colaboradores
    --task-types        Limpa apenas tipos de tarefa
    --tasks             Limpa apenas tarefas
    --financial         Limpa apenas dados financeiros (faturamento e lucro)
    --sync-data         Limpa dados sincronizados (produtos, serviços, colaboradores, tipos, tarefas)
    --confirm           Confirma a operação sem prompt interativo
    --help              Mostra esta ajuda

Exemplos:
    python clean_database.py --sync-data --confirm
    python clean_database.py --financial
    python clean_database.py --all
"""

import sys
import os
import argparse
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from App import create_app, db
from App.Models import (
    Usuario, TipoTarefa, Colaborador, Produto, Servico, Tarefa,
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico
)


class DatabaseCleaner:
    """Classe para limpeza controlada do banco de dados"""
    
    def __init__(self, app):
        self.app = app
        
    def clean_users(self):
        """Limpa dados de usuários"""
        with self.app.app_context():
            try:
                count = Usuario.query.count()
                Usuario.query.delete()
                db.session.commit()
                print(f"✅ {count} usuários removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar usuários: {e}")
                return False
    
    def clean_products(self):
        """Limpa dados de produtos"""
        with self.app.app_context():
            try:
                count = Produto.query.count()
                Produto.query.delete()
                db.session.commit()
                print(f"✅ {count} produtos removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar produtos: {e}")
                return False
    
    def clean_services(self):
        """Limpa dados de serviços"""
        with self.app.app_context():
            try:
                count = Servico.query.count()
                Servico.query.delete()
                db.session.commit()
                print(f"✅ {count} serviços removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar serviços: {e}")
                return False
    
    def clean_collaborators(self):
        """Limpa dados de colaboradores"""
        with self.app.app_context():
            try:
                count = Colaborador.query.count()
                Colaborador.query.delete()
                db.session.commit()
                print(f"✅ {count} colaboradores removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar colaboradores: {e}")
                return False
    
    def clean_task_types(self):
        """Limpa dados de tipos de tarefa"""
        with self.app.app_context():
            try:
                count = TipoTarefa.query.count()
                TipoTarefa.query.delete()
                db.session.commit()
                print(f"✅ {count} tipos de tarefa removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar tipos de tarefa: {e}")
                return False
    
    def clean_tasks(self):
        """Limpa dados de tarefas"""
        with self.app.app_context():
            try:
                count = Tarefa.query.count()
                Tarefa.query.delete()
                db.session.commit()
                print(f"✅ {count} tarefas removidas")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar tarefas: {e}")
                return False
    
    def clean_financial_data(self):
        """Limpa todos os dados financeiros (faturamento e lucro)"""
        with self.app.app_context():
            try:
                # Conta registros antes da limpeza
                faturamento_total_count = FaturamentoTotal.query.count()
                faturamento_produto_count = FaturamentoProduto.query.count()
                faturamento_servico_count = FaturamentoServico.query.count()
                lucro_total_count = LucroTotal.query.count()
                lucro_produto_count = LucroProduto.query.count()
                lucro_servico_count = LucroServico.query.count()
                
                # Remove dados
                FaturamentoTotal.query.delete()
                FaturamentoProduto.query.delete()
                FaturamentoServico.query.delete()
                LucroTotal.query.delete()
                LucroProduto.query.delete()
                LucroServico.query.delete()
                
                db.session.commit()
                
                total = (faturamento_total_count + faturamento_produto_count + 
                        faturamento_servico_count + lucro_total_count + 
                        lucro_produto_count + lucro_servico_count)
                
                print(f"✅ Dados financeiros removidos:")
                print(f"   - {faturamento_total_count} registros de faturamento total")
                print(f"   - {faturamento_produto_count} registros de faturamento produto")
                print(f"   - {faturamento_servico_count} registros de faturamento serviço")
                print(f"   - {lucro_total_count} registros de lucro total")
                print(f"   - {lucro_produto_count} registros de lucro produto")
                print(f"   - {lucro_servico_count} registros de lucro serviço")
                print(f"   📊 Total: {total} registros removidos")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao limpar dados financeiros: {e}")
                return False
    
    def clean_sync_data(self):
        """Limpa dados sincronizados da API (produtos, serviços, colaboradores, tipos, tarefas)"""
        print("🔄 Limpando dados sincronizados...")
        success = True
        success &= self.clean_tasks()
        success &= self.clean_products()
        success &= self.clean_services()
        success &= self.clean_collaborators()
        success &= self.clean_task_types()
        success &= self.clean_financial_data()
        return success
    
    def clean_all(self):
        """Limpa todas as tabelas (exceto usuários por segurança)"""
        print("🧹 Limpando todas as tabelas (mantendo usuários)...")
        success = True
        success &= self.clean_tasks()
        success &= self.clean_financial_data()
        success &= self.clean_products()
        success &= self.clean_services()
        success &= self.clean_collaborators()
        success &= self.clean_task_types()
        return success
    
    def get_database_status(self):
        """Mostra o status atual do banco de dados"""
        with self.app.app_context():
            print("\n📊 STATUS ATUAL DO BANCO DE DADOS:")
            print("=" * 50)
            
            try:
                print(f"👥 Usuários: {Usuario.query.count()}")
                print(f"📦 Produtos: {Produto.query.count()}")
                print(f"🔧 Serviços: {Servico.query.count()}")
                print(f"👷 Colaboradores: {Colaborador.query.count()}")
                print(f"📋 Tipos de Tarefa: {TipoTarefa.query.count()}")
                print(f"📝 Tarefas: {Tarefa.query.count()}")
                print(f"💰 Faturamento Total: {FaturamentoTotal.query.count()}")
                print(f"📈 Faturamento Produto: {FaturamentoProduto.query.count()}")
                print(f"📈 Faturamento Serviço: {FaturamentoServico.query.count()}")
                print(f"💹 Lucro Total: {LucroTotal.query.count()}")
                print(f"📊 Lucro Produto: {LucroProduto.query.count()}")
                print(f"📊 Lucro Serviço: {LucroServico.query.count()}")
                print("=" * 50)
            except Exception as e:
                print(f"❌ Erro ao consultar status: {e}")


def confirm_action(message):
    """Solicita confirmação do usuário"""
    response = input(f"\n⚠️  {message} (s/N): ").lower().strip()
    return response in ['s', 'sim', 'y', 'yes']


def main():
    parser = argparse.ArgumentParser(
        description="Script para limpeza do banco de dados",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Limpa todas as tabelas (exceto usuários)')
    parser.add_argument('--users', action='store_true', 
                       help='Limpa apenas usuários')
    parser.add_argument('--products', action='store_true', 
                       help='Limpa apenas produtos')
    parser.add_argument('--services', action='store_true', 
                       help='Limpa apenas serviços')
    parser.add_argument('--collaborators', action='store_true', 
                       help='Limpa apenas colaboradores')
    parser.add_argument('--task-types', action='store_true', 
                       help='Limpa apenas tipos de tarefa')
    parser.add_argument('--tasks', action='store_true', 
                       help='Limpa apenas tarefas')
    parser.add_argument('--financial', action='store_true', 
                       help='Limpa apenas dados financeiros')
    parser.add_argument('--sync-data', action='store_true', 
                       help='Limpa dados sincronizados (produtos, serviços, colaboradores, tipos, tarefas)')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirma a operação sem prompt')
    parser.add_argument('--status', action='store_true', 
                       help='Mostra apenas o status do banco')
    
    args = parser.parse_args()
    
    # Cria a aplicação Flask
    app = create_app()
    cleaner = DatabaseCleaner(app)
    
    # Se apenas status foi solicitado
    if args.status:
        cleaner.get_database_status()
        return
    
    # Mostra status inicial
    cleaner.get_database_status()
    
    # Se nenhuma opção foi especificada, mostra ajuda
    if not any([args.all, args.users, args.products, args.services, 
                args.collaborators, args.task_types, args.tasks, 
                args.financial, args.sync_data]):
        parser.print_help()
        return
    
    print(f"\n🗓️  Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Confirmação de segurança
    if not args.confirm:
        if not confirm_action("Tem certeza que deseja prosseguir com a limpeza?"):
            print("❌ Operação cancelada pelo usuário")
            return
    
    # Executa as limpezas solicitadas
    print("\n🧹 INICIANDO LIMPEZA DO BANCO DE DADOS")
    print("=" * 50)
    
    success = True
    
    if args.all:
        success &= cleaner.clean_all()
    
    if args.users:
        if not args.confirm and not confirm_action("ATENÇÃO: Limpar usuários irá remover todas as credenciais. Continuar?"):
            print("❌ Limpeza de usuários cancelada")
        else:
            success &= cleaner.clean_users()
    
    if args.products:
        success &= cleaner.clean_products()
    
    if args.services:
        success &= cleaner.clean_services()
    
    if args.collaborators:
        success &= cleaner.clean_collaborators()
    
    if args.task_types:
        success &= cleaner.clean_task_types()
    
    if args.tasks:
        success &= cleaner.clean_tasks()
    
    if args.financial:
        success &= cleaner.clean_financial_data()
    
    if args.sync_data:
        success &= cleaner.clean_sync_data()
    
    print("\n" + "=" * 50)
    
    if success:
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
    else:
        print("⚠️  LIMPEZA CONCLUÍDA COM ALGUNS ERROS")
    
    # Mostra status final
    cleaner.get_database_status()
    
    print(f"\n🏁 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
