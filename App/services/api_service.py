"""
APIService - Serviço centralizado para requisições à API Auvo
"""
import requests
import logging

logger = logging.getLogger(__name__)


class APIService:
    """Serviço para gerenciar requisições à API Auvo"""
    
    # URLs base da API Auvo
    BASE_URLS = {
        'products': 'https://api.auvo.com.br/v2/Product',
        'services': 'https://api.auvo.com.br/v2/Service', 
        'collaborators': 'https://api.auvo.com.br/v2/Person',
        'task_types': 'https://api.auvo.com.br/v2/TaskType',
        'tasks': 'https://api.auvo.com.br/v2/Tasks'
    }
    
    @staticmethod
    def make_request(url, headers, params=None, method='GET'):
        """
        Faz requisição HTTP padronizada
        
        Args:
            url (str): URL da requisição
            headers (dict): Headers da requisição
            params (dict, optional): Parâmetros da requisição
            method (str): Método HTTP (GET, POST, etc.)
            
        Returns:
            requests.Response: Resposta da requisição
            
        Raises:
            requests.exceptions.RequestException: Erro na requisição
        """
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=params)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {str(e)}")
            raise
    
    @staticmethod
    def fetch_paginated_data(endpoint_key, headers, params=None, page_size=500):
        """
        Busca dados paginados da API Auvo
        
        Args:
            endpoint_key (str): Chave do endpoint (products, services, etc.)
            headers (dict): Headers da requisição
            params (dict, optional): Parâmetros adicionais
            page_size (int): Tamanho da página
            
        Returns:
            tuple: (success: bool, data: list, message: str)
        """
        try:
            base_url = APIService.BASE_URLS.get(endpoint_key)
            if not base_url:
                return False, [], f"Endpoint não encontrado: {endpoint_key}"
            
            all_data = []
            page = 1
            
            # Parâmetros base para paginação
            request_params = {
                'pageSize': page_size,
                'page': page
            }
            
            # Adiciona parâmetros extras se fornecidos
            if params:
                request_params.update(params)
            
            while True:
                logger.debug(f"🔄 Buscando página {page} de {endpoint_key}")
                
                # Atualiza número da página
                request_params['page'] = page
                
                # Faz a requisição
                response = APIService.make_request(base_url, headers, request_params)
                data = response.json()
                
                # Extrai dados da resposta
                items = data.get('Data', [])
                if not items:
                    break
                
                all_data.extend(items)
                logger.debug(f"✅ Página {page}: {len(items)} itens")
                
                # Verifica se há mais páginas
                total_count = data.get('TotalCount', 0)
                if len(all_data) >= total_count:
                    break
                
                page += 1
            
            logger.info(f"✅ Total de {len(all_data)} itens obtidos de {endpoint_key}")
            return True, all_data, f"Dados obtidos com sucesso: {len(all_data)} itens"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição {endpoint_key}: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
        except Exception as e:
            error_msg = f"Erro inesperado em {endpoint_key}: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    @staticmethod
    def fetch_tasks_with_filter(headers, start_date=None, end_date=None, page_size=500):
        """
        Busca tarefas com filtros específicos
        
        Args:
            headers (dict): Headers da requisição
            start_date (str, optional): Data inicial (YYYY-MM-DD)
            end_date (str, optional): Data final (YYYY-MM-DD)
            page_size (int): Tamanho da página
            
        Returns:
            tuple: (success: bool, data: list, message: str)
        """
        try:
            params = {}
            
            # Adiciona filtros de data se fornecidos
            if start_date and end_date:
                # Formato específico para API de tarefas
                filter_params = {
                    "paramFilter": {
                        "startDate": start_date,
                        "endDate": end_date
                    }
                }
                params.update(filter_params)
            
            return APIService.fetch_paginated_data('tasks', headers, params, page_size)
            
        except Exception as e:
            error_msg = f"Erro ao buscar tarefas com filtro: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
