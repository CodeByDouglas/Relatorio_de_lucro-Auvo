"""
Script de migração para adicionar usuario_id aos models existentes

Este script deve ser executado para atualizar o banco de dados existente
com as novas colunas usuario_id nos models que não as possuíam.
"""

from flask import Flask
from App import create_app, db
from App.Models import *
import sqlite3
import os


def migrate_database():
    """
    Migra o banco de dados adicionando as colunas usuario_id necessárias
    """
    app = create_app()
    
    with app.app_context():
        # Conecta diretamente ao SQLite para fazer as alterações
        db_path = os.path.join(app.instance_path, 'database.db')
        
        if not os.path.exists(db_path):
            print("❌ Banco de dados não encontrado. Criando novo banco...")
            db.create_all()
            print("✅ Novo banco de dados criado com sucesso!")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print("🔄 Iniciando migração do banco de dados...")
            
            # Lista de tabelas para verificar/adicionar usuario_id
            tables_to_migrate = [
                'tipo_tarefa',
                'colaborador', 
                'produto',
                'servico',
                'tarefa'
            ]
            
            for table in tables_to_migrate:
                # Verifica se a coluna usuario_id já existe
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'usuario_id' not in columns:
                    print(f"➕ Adicionando usuario_id à tabela {table}...")
                    
                    # Adiciona a coluna usuario_id
                    cursor.execute(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN usuario_id INTEGER 
                        REFERENCES usuario(id)
                    """)
                    
                    # Define um valor padrão (assumindo que existe pelo menos um usuário com id=1)
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET usuario_id = 1 
                        WHERE usuario_id IS NULL
                    """)
                    
                    print(f"✅ Coluna usuario_id adicionada à tabela {table}")
                else:
                    print(f"ℹ️  Tabela {table} já possui a coluna usuario_id")
            
            # Remove a constraint UNIQUE da descrição em tipo_tarefa se existir
            print("🔄 Verificando constraints da tabela tipo_tarefa...")
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tipo_tarefa'")
            table_sql = cursor.fetchone()
            
            if table_sql and 'UNIQUE' in table_sql[0] and 'descricao' in table_sql[0]:
                print("🔄 Removendo constraint UNIQUE da coluna descricao...")
                
                # Backup dos dados
                cursor.execute("CREATE TEMPORARY TABLE tipo_tarefa_backup AS SELECT * FROM tipo_tarefa")
                
                # Remove a tabela original
                cursor.execute("DROP TABLE tipo_tarefa")
                
                # Recria a tabela sem a constraint UNIQUE
                cursor.execute("""
                    CREATE TABLE tipo_tarefa (
                        id INTEGER PRIMARY KEY,
                        usuario_id INTEGER REFERENCES usuario(id),
                        descricao VARCHAR NOT NULL
                    )
                """)
                
                # Restaura os dados
                cursor.execute("INSERT INTO tipo_tarefa SELECT * FROM tipo_tarefa_backup")
                cursor.execute("DROP TABLE tipo_tarefa_backup")
                
                print("✅ Constraint UNIQUE removida da coluna descricao")
            
            conn.commit()
            print("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro durante a migração: {str(e)}")
            raise
        finally:
            conn.close()


if __name__ == "__main__":
    migrate_database()
