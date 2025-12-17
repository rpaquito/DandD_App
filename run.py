#!/usr/bin/env python3
"""Ponto de entrada da aplicação Companheiro de Mestre de Dungeon."""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  Companheiro de Mestre de Dungeon")
    print("  Acede a: http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, host='127.0.0.1', port=5001)
