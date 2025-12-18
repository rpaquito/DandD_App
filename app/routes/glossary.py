"""Rotas do glossario de termos D&D."""

from flask import Blueprint, render_template, request, jsonify
from app.services.glossary_service import get_glossary_service

glossary_bp = Blueprint('glossary', __name__)


@glossary_bp.route('/')
def index():
    """Pagina principal do glossario."""
    service = get_glossary_service()
    grouped_terms = service.get_grouped_terms()
    categories = service.get_categories()

    return render_template(
        'glossary/index.html',
        grouped_terms=grouped_terms,
        categories=categories
    )


@glossary_bp.route('/termo/<term_id>')
def term_detail(term_id):
    """Detalhes de um termo especifico."""
    service = get_glossary_service()
    term = service.get_term(term_id)

    if not term:
        return jsonify({'erro': 'Termo nao encontrado'}), 404

    # Se for pedido AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(term)

    return render_template('glossary/term.html', term=term)


@glossary_bp.route('/tooltip/<term_id>')
def tooltip(term_id):
    """Dados para tooltip (AJAX)."""
    service = get_glossary_service()
    tooltip_data = service.get_term_for_tooltip(term_id)

    if not tooltip_data:
        return jsonify({'erro': 'Termo nao encontrado'}), 404

    return jsonify(tooltip_data)


@glossary_bp.route('/pesquisa')
def search():
    """Pesquisar termos."""
    query = request.args.get('q', '')
    service = get_glossary_service()

    if len(query) < 2:
        return jsonify({'resultados': {}, 'query': query})

    results = service.search_terms(query)

    # Se for pedido AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'resultados': results, 'query': query})

    categories = service.get_categories()
    return render_template(
        'glossary/search.html',
        results=results,
        query=query,
        categories=categories
    )


@glossary_bp.route('/categoria/<category>')
def by_category(category):
    """Termos de uma categoria especifica."""
    service = get_glossary_service()
    terms = service.get_terms_by_category(category)
    categories = service.get_categories()
    category_name = categories.get(category, category)

    return render_template(
        'glossary/category.html',
        terms=terms,
        category=category,
        category_name=category_name,
        categories=categories
    )
