"""Servico para gestao do glossario de termos D&D."""

import json
import os
from functools import lru_cache
from flask import current_app


class GlossaryService:
    """Servico para operacoes com o glossario."""

    def __init__(self):
        self._glossary = None
        self._categories = None

    def _load_glossary(self):
        """Carrega o glossario do ficheiro JSON."""
        if self._glossary is not None:
            return

        glossary_file = os.path.join(
            current_app.root_path, 'data', 'glossary.json'
        )

        if os.path.exists(glossary_file):
            with open(glossary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._glossary = data.get('termos', {})
                self._categories = data.get('categorias', {})
        else:
            self._glossary = {}
            self._categories = {}

    def get_all_terms(self):
        """Obter todos os termos do glossario."""
        self._load_glossary()
        return self._glossary

    def get_term(self, term_id):
        """Obter um termo especifico por ID."""
        self._load_glossary()
        term = self._glossary.get(term_id)
        if term:
            term['id'] = term_id
        return term

    def get_categories(self):
        """Obter todas as categorias."""
        self._load_glossary()
        return self._categories

    def get_terms_by_category(self, category):
        """Obter termos de uma categoria especifica."""
        self._load_glossary()
        return {
            tid: term for tid, term in self._glossary.items()
            if term.get('categoria') == category
        }

    def search_terms(self, query):
        """Pesquisar termos por nome ou descricao."""
        self._load_glossary()
        query = query.lower()
        results = {}

        for tid, term in self._glossary.items():
            if (query in term.get('nome', '').lower() or
                query in term.get('abreviatura', '').lower() or
                query in term.get('descricao', '').lower()):
                results[tid] = term

        return results

    def get_term_for_tooltip(self, term_id):
        """Obter dados minimos para tooltip."""
        term = self.get_term(term_id)
        if not term:
            return None

        return {
            'id': term_id,
            'nome': term.get('nome', ''),
            'abreviatura': term.get('abreviatura', ''),
            'descricao': term.get('descricao', '')[:200] + ('...' if len(term.get('descricao', '')) > 200 else '')
        }

    def get_grouped_terms(self):
        """Obter termos agrupados por categoria."""
        self._load_glossary()
        grouped = {}

        for cat_id, cat_name in self._categories.items():
            terms = self.get_terms_by_category(cat_id)
            if terms:
                grouped[cat_id] = {
                    'nome': cat_name,
                    'termos': dict(sorted(terms.items(), key=lambda x: x[1].get('nome', '')))
                }

        return grouped


# Instancia global para cache
_glossary_service = None


def get_glossary_service():
    """Obter instancia do servico de glossario."""
    global _glossary_service
    if _glossary_service is None:
        _glossary_service = GlossaryService()
    return _glossary_service
