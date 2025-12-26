"""
Migração: Adicionar campo xp_total à tabela session_players

Este script adiciona o campo xp_total à tabela session_players para rastrear
XP acumulado dos jogadores.

Como executar:
    python migrations/001_add_xp_total.py
"""

import sqlite3
import os

# Caminho para a base de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'app.db')


def migrate():
    """Executa a migração."""
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de dados não encontrada: {DB_PATH}")
        print("   Execute a aplicação primeiro para criar a base de dados.")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(session_players)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'xp_total' in columns:
            print("✓ Campo xp_total já existe na tabela session_players")
            conn.close()
            return True

        # Adicionar a coluna
        print("Adicionando campo xp_total à tabela session_players...")
        cursor.execute("""
            ALTER TABLE session_players
            ADD COLUMN xp_total INTEGER DEFAULT 0
        """)

        conn.commit()
        print("✓ Campo xp_total adicionado com sucesso!")

        # Verificar
        cursor.execute("PRAGMA table_info(session_players)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"  Colunas da tabela: {', '.join(columns)}")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False


def rollback():
    """Reverte a migração (remove o campo xp_total)."""
    print("⚠️  AVISO: SQLite não suporta DROP COLUMN diretamente.")
    print("   Para reverter, seria necessário recriar a tabela.")
    print("   Não recomendado a menos que seja absolutamente necessário.")
    return False


if __name__ == '__main__':
    print("=" * 60)
    print("MIGRAÇÃO 001: Adicionar campo xp_total")
    print("=" * 60)
    print()

    success = migrate()

    print()
    if success:
        print("✓ Migração concluída com sucesso!")
    else:
        print("❌ Migração falhou.")

    print()
    print("=" * 60)
