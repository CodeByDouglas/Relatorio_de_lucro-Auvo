import requests
from datetime import datetime
from flask import jsonify
from ..Models import Usuario, Produto
from .. import db


class ProdutoController:
    """Controller para gerenciar produtos da API da Auvo"""
    
    @staticmethod
    def fetch_and_save_products(user_id):
        """
        Busca produtos da API da Auvo e salva no banco de dados
        
        Args:
            user_id (int): ID do usuário no banco de dados
            
        Returns:
            dict: Resultado da operação
        """
        
        # Validação básica
        if not user_id:
            return {
                'success': False,
                'message': 'ID do usuário é obrigatório',
                'data': None
            }
        
        # Busca o usuário no banco
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return {
                'success': False,
                'message': 'Usuário não encontrado',
                'data': None
            }
        
        # Verifica se o token ainda é válido
        from .auth_api import AuthController
        token_validation = AuthController.validate_token(usuario.chave_app)
        
        if not token_validation.get('valid'):
            return {
                'success': False,
                'message': 'Token expirado. Faça login novamente.',
                'data': None
            }
        
        # URL da API de produtos
        url = "https://api.auvo.com.br/v2/products/?pageSize=9999999"
        
        # Headers da requisição
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {usuario.token_bearer}'
        }
        
        try:
            # Faz a requisição para a API
            response = requests.get(url, headers=headers, timeout=30)
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verifica se a estrutura da resposta está correta
                    if 'result' in data and 'entityList' in data['result']:
                        products_list = data['result']['entityList']
                        
                        # Salva os produtos no banco
                        save_result = ProdutoController._save_products_to_database(products_list)
                        
                        return {
                            'success': True,
                            'message': f'Produtos sincronizados com sucesso. {save_result["saved"]} produtos salvos, {save_result["updated"]} atualizados.',
                            'data': {
                                'total_products': len(products_list),
                                'saved': save_result['saved'],
                                'updated': save_result['updated'],
                                'errors': save_result['errors']
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Formato de resposta inválido da API',
                            'data': None
                        }
                        
                except ValueError as e:
                    return {
                        'success': False,
                        'message': 'Erro ao processar resposta da API',
                        'data': None
                    }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Token de autorização inválido ou expirado',
                    'data': None
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Acesso negado. Verifique suas permissões',
                    'data': None
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro na API: {response.status_code}',
                    'data': None
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Timeout na conexão com a API',
                'data': None
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': 'Erro de conexão com a API',
                'data': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': 'Erro na requisição para a API',
                'data': None
            }
    
    @staticmethod
    def _save_products_to_database(products_list):
        """
        Salva ou atualiza produtos no banco de dados
        
        Args:
            products_list (list): Lista de produtos da API
            
        Returns:
            dict: Estatísticas da operação
        """
        saved_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        try:
            for product_data in products_list:
                try:
                    # Extrai os dados necessários
                    product_id = product_data.get('productId')
                    name = product_data.get('name', '').strip()
                    unitary_cost_str = product_data.get('unitaryCost', '0,00')
                    
                    # Validação básica
                    if not product_id:
                        error_count += 1
                        errors.append(f"Produto sem productId: {product_data}")
                        continue
                    
                    if not name:
                        name = f"Produto {product_id}"
                    
                    # Converte o custo unitário de string para float
                    # Remove vírgulas e converte para float (formato brasileiro: "6,00" -> 6.0)
                    try:
                        unitary_cost = float(unitary_cost_str.replace(',', '.')) if unitary_cost_str else 0.0
                    except (ValueError, AttributeError):
                        unitary_cost = 0.0
                    
                    # Busca produto existente
                    produto_existente = Produto.query.filter_by(id=product_id).first()
                    
                    if produto_existente:
                        # Atualiza produto existente
                        produto_existente.nome = name
                        produto_existente.custo_unitario = unitary_cost
                        updated_count += 1
                    else:
                        # Cria novo produto
                        novo_produto = Produto(
                            id=product_id,
                            nome=name,
                            custo_unitario=unitary_cost,
                            preco_unitario=None  # Pode ser definido posteriormente
                        )
                        db.session.add(novo_produto)
                        saved_count += 1
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Erro ao processar produto {product_data.get('productId', 'unknown')}: {str(e)}")
                    continue
            
            # Commit das alterações
            db.session.commit()
            
            return {
                'saved': saved_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'saved': 0,
                'updated': 0,
                'errors': len(products_list),
                'error_details': [f"Erro geral no banco de dados: {str(e)}"]
            }
    
    @staticmethod
    def get_products_from_database(limit=None):
        """
        Recupera produtos do banco de dados
        
        Args:
            limit (int, optional): Limite de produtos a retornar
            
        Returns:
            dict: Lista de produtos
        """
        try:
            query = Produto.query
            
            if limit:
                query = query.limit(limit)
            
            produtos = query.all()
            
            products_list = []
            for produto in produtos:
                products_list.append({
                    'id': produto.id,
                    'nome': produto.nome,
                    'custo_unitario': produto.custo_unitario,
                    'preco_unitario': produto.preco_unitario
                })
            
            return {
                'success': True,
                'message': f'{len(products_list)} produtos encontrados',
                'data': products_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar produtos no banco',
                'data': None
            }
    
    @staticmethod
    def update_product_cost(product_id, custo_unitario, preco_unitario=None):
        """
        Atualiza custos de um produto
        
        Args:
            product_id (str): ID do produto (UUID)
            custo_unitario (float): Custo unitário do produto
            preco_unitario (float, optional): Preço unitário do produto
            
        Returns:
            dict: Resultado da operação
        """
        try:
            produto = Produto.query.filter_by(id=product_id).first()
            
            if not produto:
                return {
                    'success': False,
                    'message': 'Produto não encontrado',
                    'data': None
                }
            
            # Atualiza os valores
            produto.custo_unitario = custo_unitario
            if preco_unitario is not None:
                produto.preco_unitario = preco_unitario
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Produto atualizado com sucesso',
                'data': {
                    'id': produto.id,
                    'nome': produto.nome,
                    'custo_unitario': produto.custo_unitario,
                    'preco_unitario': produto.preco_unitario
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Erro ao atualizar produto',
                'data': None
            }
    
    @staticmethod
    def get_product_by_id(product_id):
        """
        Busca um produto específico por ID
        
        Args:
            product_id (str): ID do produto (UUID)
            
        Returns:
            dict: Dados do produto
        """
        try:
            produto = Produto.query.filter_by(id=product_id).first()
            
            if not produto:
                return {
                    'success': False,
                    'message': 'Produto não encontrado',
                    'data': None
                }
            
            return {
                'success': True,
                'message': 'Produto encontrado',
                'data': {
                    'id': produto.id,
                    'nome': produto.nome,
                    'custo_unitario': produto.custo_unitario,
                    'preco_unitario': produto.preco_unitario
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar produto',
                'data': None
            }
