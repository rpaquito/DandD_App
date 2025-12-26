"""
Migração: Combat Enhancements - Combat Log, Spell Slots, Action Economy

Este script adiciona:
1. Tabela combat_logs para histórico de ações
2. Campos action_economy_json e spell_slots_json à tabela session_combats

Como executar:
    python migrations/002_add_combat_enhancements.py
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

        print("\n=== 1. Criar tabela combat_logs ===")

        # Verificar se tabela já existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='combat_logs'")
        if cursor.fetchone():
            print("✓ Tabela combat_logs já existe")
        else:
            cursor.execute("""
                CREATE TABLE combat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    combat_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ronda INTEGER DEFAULT 1,
                    turno INTEGER DEFAULT 1,
                    actor_id VARCHAR(100) NOT NULL,
                    actor_nome VARCHAR(200) NOT NULL,
                    action_type VARCHAR(50) NOT NULL,
                    details_json TEXT,
                    target_id VARCHAR(100),
                    target_nome VARCHAR(200),
                    message TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
                )
            """)
            print("✓ Tabela combat_logs criada com sucesso!")

        print("\n=== 2. Adicionar campos a session_combats ===")

        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(session_combats)")
        columns = [column[1] for column in cursor.fetchall()]

        # Adicionar action_economy_json
        if 'action_economy_json' not in columns:
            print("Adicionando campo action_economy_json...")
            cursor.execute("""
                ALTER TABLE session_combats
                ADD COLUMN action_economy_json TEXT
            """)
            print("✓ Campo action_economy_json adicionado")
        else:
            print("✓ Campo action_economy_json já existe")

        # Adicionar spell_slots_json
        if 'spell_slots_json' not in columns:
            print("Adicionando campo spell_slots_json...")
            cursor.execute("""
                ALTER TABLE session_combats
                ADD COLUMN spell_slots_json TEXT
            """)
            print("✓ Campo spell_slots_json adicionado")
        else:
            print("✓ Campo spell_slots_json já existe")

        conn.commit()

        # Verificar resultado final
        print("\n=== Verificação Final ===")
        cursor.execute("PRAGMA table_info(session_combats)")
        combat_columns = [column[1] for column in cursor.fetchall()]
        print(f"Colunas de session_combats: {', '.join(combat_columns)}")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='combat_logs'")
        if cursor.fetchone():
            print("✓ Tabela combat_logs confirmada")

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False


def rollback():
    """Reverte a migração."""
    print("⚠️  AVISO: Rollback de combat enhancements")
    print("   Isto irá APAGAR todos os combat logs!")

    response = input("Tens a certeza? (yes/no): ")
    if response.lower() != 'yes':
        print("Rollback cancelado")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Apagar tabela combat_logs
        cursor.execute("DROP TABLE IF EXISTS combat_logs")
        print("✓ Tabela combat_logs apagada")

        # Nota: SQLite não suporta DROP COLUMN facilmente
        print("⚠️  Campos action_economy_json e spell_slots_json não foram removidos")
        print("   (SQLite não suporta DROP COLUMN sem recriar tabela)")

        conn.commit()
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ Erro ao executar rollback: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("MIGRAÇÃO 002: Combat Enhancements")
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
