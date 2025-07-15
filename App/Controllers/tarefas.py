import requests
import json
from datetime import datetime, timedelta
from flask import jsonify
from ..Models import (
    Usuario, Tarefa, Produto, Servico, TipoTarefa, Colaborador,
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico
)
from .. import db
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TarefaController:
    """Controller para gerenciar tarefas da API da Auvo e cálculos financeiros"""
    
    @staticmethod
    def fetch_and_process_tasks(user_id, start_date=None, end_date=None):
        """
        Busca tarefas da API da Auvo, processa e salva dados financeiros
        
        Args:
            user_id (int): ID do usuário no banco de dados
            start_date (str, optional): Data inicial (YYYY-MM-DD). Default: ontem
            end_date (str, optional): Data final (YYYY-MM-DD). Default: hoje
            
        Returns:
            dict: Resultado da operação com todos os cálculos
        """
        
        logger.debug(f"🔄 Iniciando processamento de tarefas para usuário {user_id}")
        
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
            logger.error(f"❌ Usuário {user_id} não encontrado no banco de dados")
            return {
                'success': False,
                'message': 'Usuário não encontrado',
                'data': None
            }
        
        logger.debug(f"✅ Usuário encontrado: {usuario.chave_app}")
        
        # Verifica se o token ainda é válido (temporariamente desabilitado para debug)
        # from .auth_api import AuthController
        # token_validation = AuthController.validate_token(usuario.chave_app)
        
        # if not token_validation.get('valid'):
        #     logger.error(f"❌ Token inválido para usuário {user_id}")
        #     return {
        #         'success': False,
        #         'message': 'Token expirado. Faça login novamente.',
        #         'data': None
        #     }
        
        # Temporário: aceita token sempre válido durante login
        logger.debug(f"DEBUG: Tarefas - bypass da validação de token para user_id: {user_id}")
        token_validation = {'valid': True, 'access_token': usuario.token_bearer}
        
        # Define datas padrão se não fornecidas
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.debug(f"📅 Período: {start_date} até {end_date}")
        
        # Busca todas as tarefas do período
        tasks_result = TarefaController._fetch_all_tasks_from_api(usuario, start_date, end_date)
        
        if not tasks_result['success']:
            return tasks_result
        
        tasks_list = tasks_result['data']
        logger.debug(f"📊 Total de tarefas encontradas: {len(tasks_list)}")
        
        # Processa e salva as tarefas
        processing_result = TarefaController._process_and_save_tasks(tasks_list, usuario.id, start_date, end_date)
        
        return processing_result
    
    @staticmethod
    def _fetch_all_tasks_from_api(usuario, start_date, end_date):
        """
        Busca todas as tarefas da API com paginação
        
        Args:
            usuario: Objeto Usuario
            start_date (str): Data inicial
            end_date (str): Data final
            
        Returns:
            dict: Resultado com lista de tarefas
        """
        
        # Headers da requisição
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {usuario.token_bearer}'
        }
        
        # Parâmetros do filtro
        param_filter = {
            "startDate": start_date,
            "endDate": end_date,
            "status": 3  # Tarefas finalizadas automaticamente ou manualmente
        }
        
        all_tasks = []
        page = 1
        page_size = 100
        
        try:
            while True:
                # Monta a URL com parâmetros - Importante: Tasks com T maiúsculo
                url = f"https://api.auvo.com.br/v2/Tasks/?ParamFilter={json.dumps(param_filter)}&Page={page}&PageSize={page_size}"
                
                logger.debug(f"🌐 Buscando página {page}: {url}")
                
                # Faz a requisição para a API
                response = requests.get(url, headers=headers, timeout=30)
                
                logger.debug(f"📡 Status da resposta página {page}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.debug(f"📄 Resposta da API recebida com sucesso")
                        logger.debug(f"📋 Estrutura da resposta: {list(data.keys())}")
                        
                        # Verifica estrutura da resposta
                        if 'result' in data and 'entityList' in data['result']:
                            tasks_page = data['result']['entityList']
                            logger.debug(f"📊 Encontradas {len(tasks_page)} tarefas na página {page}")
                            
                            all_tasks.extend(tasks_page)
                            
                            # Verifica se há mais páginas
                            paged_data = data['result'].get('pagedSearchReturnData', {})
                            total_items = paged_data.get('totalItems', 0)
                            current_page = paged_data.get('page', page)
                            
                            logger.debug(f"📋 Paginação: página {current_page}, total de itens: {total_items}")
                            
                            # Se não há mais tarefas ou chegou ao final
                            if len(tasks_page) < page_size or len(all_tasks) >= total_items:
                                break
                            
                            page += 1
                        else:
                            logger.error(f"❌ Formato de resposta inválido da API. Estrutura: {list(data.keys())}")
                            return {
                                'success': False,
                                'message': 'Formato de resposta inválido da API',
                                'data': None
                            }
                            
                    except ValueError as e:
                        logger.error(f"❌ Erro ao processar resposta da API: {str(e)}")
                        return {
                            'success': False,
                            'message': 'Erro ao processar resposta da API',
                            'data': None
                        }
                        
                elif response.status_code == 401:
                    logger.error(f"❌ Token de autorização inválido ou expirado")
                    return {
                        'success': False,
                        'message': 'Token de autorização inválido ou expirado',
                        'data': None
                    }
                elif response.status_code == 400:
                    logger.error(f"❌ Erro na API: {response.status_code}")
                    logger.error(f"📄 Conteúdo da resposta: {response.text}")
                    return {
                        'success': False,
                        'message': f'Erro na requisição: {response.text}',
                        'data': None
                    }
                else:
                    logger.error(f"❌ Erro inesperado da API: {response.status_code}")
                    return {
                        'success': False,
                        'message': f'Erro inesperado: {response.status_code}',
                        'data': None
                    }
            
            logger.debug(f"✅ Total de tarefas coletadas: {len(all_tasks)}")
            
            return {
                'success': True,
                'message': f'Tarefas coletadas com sucesso',
                'data': all_tasks
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout na conexão com a API")
            return {
                'success': False,
                'message': 'Timeout na conexão com a API',
                'data': None
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 Erro de conexão com a API")
            return {
                'success': False,
                'message': 'Erro de conexão com a API',
                'data': None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"🚫 Erro na requisição para a API: {str(e)}")
            return {
                'success': False,
                'message': 'Erro na requisição para a API',
                'data': None
            }
    
    @staticmethod
    def _process_and_save_tasks(tasks_list, usuario_id, start_date, end_date):
        """
        Processa e salva as tarefas com todos os cálculos financeiros
        
        Args:
            tasks_list (list): Lista de tarefas da API
            usuario_id (int): ID do usuário
            start_date (str): Data inicial
            end_date (str): Data final
            
        Returns:
            dict: Resultado do processamento
        """
        
        logger.debug(f"💾 Processando {len(tasks_list)} tarefas para usuário {usuario_id}")
        
        # Contadores
        saved_tasks = 0
        updated_tasks = 0
        error_tasks = 0
        errors = []
        
        # Acumuladores para cálculos gerais
        faturamento_total_geral = 0.0
        faturamento_produto_geral = 0.0
        faturamento_servico_geral = 0.0
        custo_produto_geral = 0.0
        lucro_produto_geral = 0.0
        lucro_servico_geral = 0.0
        lucro_total_geral = 0.0
        
        try:
            for i, task_data in enumerate(tasks_list):
                try:
                    logger.debug(f"🔄 Processando tarefa {i+1}/{len(tasks_list)}")
                    
                    # Debug: Mostra a estrutura da primeira tarefa para análise
                    if i == 0:
                        logger.debug(f"🔍 Estrutura da primeira tarefa: {list(task_data.keys())}")
                        logger.debug(f"🔍 Dados completos da primeira tarefa: {task_data}")
                    
                    # Extrai dados da tarefa - tenta diferentes possíveis nomes para o ID
                    task_id = task_data.get('taskId') or task_data.get('id') or task_data.get('taskID') or task_data.get('ID')
                    user_to_id = task_data.get('idUserTo') or task_data.get('userToId') or task_data.get('userId')
                    customer_description = task_data.get('customerDescription', '') or task_data.get('customer', '') or task_data.get('customerName', '')
                    task_type_id = task_data.get('taskType') or task_data.get('taskTypeId') or task_data.get('typeId')
                    task_date_str = task_data.get('taskDate', '') or task_data.get('date', '') or task_data.get('dateTime', '')
                    
                    if not task_id:
                        logger.warning(f"⚠️ Tarefa sem ID ignorada. Chaves disponíveis: {list(task_data.keys())}")
                        error_tasks += 1
                        continue
                    
                    # Valida e corrige IDs de relacionamentos
                    # Verifica se tipo de tarefa existe no banco
                    if task_type_id is not None:
                        tipo_tarefa_existe = TipoTarefa.query.filter_by(
                            id=task_type_id,
                            usuario_id=usuario_id
                        ).first()
                        if not tipo_tarefa_existe:
                            # Se taskType é 0, cria um tipo padrão
                            if task_type_id == 0:
                                tipo_padrao = TipoTarefa.query.filter_by(
                                    id=0,
                                    usuario_id=usuario_id
                                ).first()
                                
                                if not tipo_padrao:
                                    # Cria tipo de tarefa padrão
                                    tipo_padrao = TipoTarefa(
                                        id=0,
                                        usuario_id=usuario_id,
                                        descricao="Tarefa Geral"
                                    )
                                    db.session.add(tipo_padrao)
                                    db.session.flush()  # Para obter o ID
                                    logger.debug(f"✅ Tipo de tarefa padrão criado: ID=0, Descrição='Tarefa Geral'")
                                
                                task_type_id = 0
                            else:
                                logger.warning(f"⚠️ Tipo de tarefa {task_type_id} não encontrado no banco. Usando tipo padrão.")
                                task_type_id = 0
                    else:
                        # Se task_type_id é None, usa tipo padrão
                        task_type_id = 0
                    
                    # Verifica se colaborador existe no banco
                    if user_to_id:
                        colaborador_existe = Colaborador.query.filter_by(
                            id=user_to_id,
                            usuario_id=usuario_id
                        ).first()
                        if not colaborador_existe:
                            logger.warning(f"⚠️ Colaborador {user_to_id} não encontrado no banco. Tarefa será ignorada.")
                            error_tasks += 1
                            errors.append(f"Tarefa {task_id}: colaborador {user_to_id} não encontrado")
                            continue
                    else:
                        logger.warning(f"⚠️ Tarefa {task_id} sem colaborador definido. Tarefa será ignorada.")
                        error_tasks += 1
                        errors.append(f"Tarefa {task_id}: sem colaborador definido")
                        continue
                    
                    # Parse da data
                    task_date = None
                    if task_date_str:
                        try:
                            task_date = datetime.fromisoformat(task_date_str.replace('Z', '+00:00'))
                        except ValueError:
                            logger.warning(f"⚠️ Data inválida na tarefa {task_id}: {task_date_str}")
                            task_date = datetime.now()
                    
                    # Processa produtos da tarefa
                    produtos = task_data.get('products', [])
                    faturamento_produto_tarefa = 0.0
                    custo_produto_tarefa = 0.0
                    
                    for produto_data in produtos:
                        produto_id = produto_data.get('productId')
                        quantidade = float(produto_data.get('quantity', 0))
                        valor_total_produto = float(produto_data.get('totalValue', 0))
                        
                        # Busca produto no banco para obter custo
                        produto_banco = Produto.query.filter_by(
                            id=produto_id,
                            usuario_id=usuario_id
                        ).first()
                        
                        if produto_banco:
                            custo_unitario = produto_banco.custo_unitario or 0.0
                            custo_total_produto = custo_unitario * quantidade
                            
                            faturamento_produto_tarefa += valor_total_produto
                            custo_produto_tarefa += custo_total_produto
                            
                            logger.debug(f"📦 Produto {produto_id}: Qtd={quantidade}, Faturamento={valor_total_produto}, Custo={custo_total_produto}")
                        else:
                            logger.warning(f"⚠️ Produto {produto_id} não encontrado no banco")
                    
                    # Processa serviços da tarefa
                    servicos = task_data.get('services', [])
                    faturamento_servico_tarefa = 0.0
                    
                    for servico_data in servicos:
                        valor_total_servico = float(servico_data.get('totalValue', 0))
                        faturamento_servico_tarefa += valor_total_servico
                        
                        logger.debug(f"🔧 Serviço: Faturamento={valor_total_servico}")
                    
                    # Cálculos da tarefa
                    faturamento_total_tarefa = faturamento_produto_tarefa + faturamento_servico_tarefa
                    lucro_produto_tarefa = faturamento_produto_tarefa - custo_produto_tarefa
                    lucro_servico_tarefa = faturamento_servico_tarefa  # Lucro serviço = faturamento serviço
                    lucro_total_tarefa = lucro_produto_tarefa + lucro_servico_tarefa
                    
                    # Verifica se a tarefa já existe
                    tarefa_existente = Tarefa.query.filter_by(
                        id=task_id,
                        usuario_id=usuario_id
                    ).first()
                    
                    # Monta JSON com detalhes completos
                    detalhes_json = {
                        'task_original': task_data,
                        'calculos': {
                            'faturamento_produto': faturamento_produto_tarefa,
                            'faturamento_servico': faturamento_servico_tarefa,
                            'faturamento_total': faturamento_total_tarefa,
                            'custo_produto': custo_produto_tarefa,
                            'lucro_produto': lucro_produto_tarefa,
                            'lucro_servico': lucro_servico_tarefa,
                            'lucro_total': lucro_total_tarefa
                        }
                    }
                    
                    if tarefa_existente:
                        # Atualiza tarefa existente
                        tarefa_existente.data = task_date
                        tarefa_existente.cliente = customer_description
                        tarefa_existente.tipo_tarefa_id = task_type_id
                        tarefa_existente.colaborador_id = user_to_id
                        tarefa_existente.valor_total = faturamento_total_tarefa
                        tarefa_existente.custo_total = custo_produto_tarefa
                        tarefa_existente.lucro_bruto = lucro_total_tarefa
                        tarefa_existente.detalhes_json = detalhes_json
                        
                        updated_tasks += 1
                        logger.debug(f"📝 Tarefa atualizada - ID: {task_id}")
                    else:
                        # Cria nova tarefa
                        nova_tarefa = Tarefa(
                            id=task_id,
                            usuario_id=usuario_id,
                            data=task_date,
                            cliente=customer_description,
                            tipo_tarefa_id=task_type_id,
                            colaborador_id=user_to_id,
                            valor_total=faturamento_total_tarefa,
                            custo_total=custo_produto_tarefa,
                            lucro_bruto=lucro_total_tarefa,
                            detalhes_json=detalhes_json
                        )
                        
                        db.session.add(nova_tarefa)
                        saved_tasks += 1
                        logger.debug(f"➕ Nova tarefa criada - ID: {task_id}")
                    
                    # Acumula valores gerais
                    faturamento_total_geral += faturamento_total_tarefa
                    faturamento_produto_geral += faturamento_produto_tarefa
                    faturamento_servico_geral += faturamento_servico_tarefa
                    custo_produto_geral += custo_produto_tarefa
                    lucro_produto_geral += lucro_produto_tarefa
                    lucro_servico_geral += lucro_servico_tarefa
                    lucro_total_geral += lucro_total_tarefa
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar tarefa {i+1}: {str(e)}")
                    error_tasks += 1
                    errors.append(f"Tarefa {i+1}: {str(e)}")
                    continue
            
            # Commit das tarefas
            db.session.commit()
            logger.debug(f"💾 Tarefas salvas - {saved_tasks} novas, {updated_tasks} atualizadas, {error_tasks} erros")
            
            # Calcula e salva dados financeiros gerais
            financial_result = TarefaController._calculate_and_save_financial_data(
                usuario_id, start_date, end_date,
                faturamento_total_geral, faturamento_produto_geral, faturamento_servico_geral,
                custo_produto_geral, lucro_produto_geral, lucro_servico_geral, lucro_total_geral
            )
            
            return {
                'success': True,
                'message': f'Processamento concluído com sucesso. {saved_tasks} tarefas salvas, {updated_tasks} atualizadas.',
                'data': {
                    'tasks_processed': len(tasks_list),
                    'tasks_saved': saved_tasks,
                    'tasks_updated': updated_tasks,
                    'tasks_errors': error_tasks,
                    'financial_data': financial_result,
                    'calculations': {
                        'faturamento_total': faturamento_total_geral,
                        'faturamento_produto': faturamento_produto_geral,
                        'faturamento_servico': faturamento_servico_geral,
                        'custo_produto': custo_produto_geral,
                        'lucro_produto': lucro_produto_geral,
                        'lucro_servico': lucro_servico_geral,
                        'lucro_total': lucro_total_geral
                    }
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Erro crítico ao processar tarefas: {str(e)}")
            return {
                'success': False,
                'message': f'Erro crítico: {str(e)}',
                'data': None
            }
    
    @staticmethod
    def _calculate_and_save_financial_data(usuario_id, start_date, end_date, 
                                         faturamento_total, faturamento_produto, faturamento_servico,
                                         custo_produto, lucro_produto, lucro_servico, lucro_total):
        """
        Calcula porcentagens e salva dados financeiros nos respectivos models
        """
        
        try:
            periodo_inicio = datetime.strptime(start_date, '%Y-%m-%d')
            periodo_fim = datetime.strptime(end_date, '%Y-%m-%d')
            agora = datetime.now()
            
            # Calcula porcentagens
            porc_faturamento_produto = (faturamento_produto / faturamento_total * 100) if faturamento_total > 0 else 0
            porc_faturamento_servico = (faturamento_servico / faturamento_total * 100) if faturamento_total > 0 else 0
            porc_lucro_produto = (lucro_produto / lucro_total * 100) if lucro_total > 0 else 0
            porc_lucro_servico = (lucro_servico / lucro_total * 100) if lucro_total > 0 else 0
            porc_lucro_faturamento = (lucro_total / faturamento_total * 100) if faturamento_total > 0 else 0
            
            logger.debug(f"📊 Calculando porcentagens:")
            logger.debug(f"   Faturamento Produto: {porc_faturamento_produto:.2f}%")
            logger.debug(f"   Faturamento Serviço: {porc_faturamento_servico:.2f}%")
            logger.debug(f"   Lucro Produto: {porc_lucro_produto:.2f}%")
            logger.debug(f"   Lucro Serviço: {porc_lucro_servico:.2f}%")
            logger.debug(f"   Lucro/Faturamento: {porc_lucro_faturamento:.2f}%")
            
            # Salva Faturamento Total
            faturamento_total_obj = FaturamentoTotal.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if faturamento_total_obj:
                faturamento_total_obj.valor_total = faturamento_total
                faturamento_total_obj.atualizado_em = agora
            else:
                faturamento_total_obj = FaturamentoTotal(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    valor_total=faturamento_total,
                    atualizado_em=agora
                )
                db.session.add(faturamento_total_obj)
            
            # Salva Faturamento Produto
            faturamento_produto_obj = FaturamentoProduto.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if faturamento_produto_obj:
                faturamento_produto_obj.valor_produtos = faturamento_produto
                faturamento_produto_obj.perc_relacao_total = porc_faturamento_produto
            else:
                faturamento_produto_obj = FaturamentoProduto(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    valor_produtos=faturamento_produto,
                    perc_relacao_total=porc_faturamento_produto
                )
                db.session.add(faturamento_produto_obj)
            
            # Salva Faturamento Serviço
            faturamento_servico_obj = FaturamentoServico.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if faturamento_servico_obj:
                faturamento_servico_obj.valor_servicos = faturamento_servico
                faturamento_servico_obj.perc_relacao_total = porc_faturamento_servico
            else:
                faturamento_servico_obj = FaturamentoServico(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    valor_servicos=faturamento_servico,
                    perc_relacao_total=porc_faturamento_servico
                )
                db.session.add(faturamento_servico_obj)
            
            # Salva Lucro Total
            lucro_total_obj = LucroTotal.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if lucro_total_obj:
                lucro_total_obj.lucro_total = lucro_total
                lucro_total_obj.margem_lucro = porc_lucro_faturamento
            else:
                lucro_total_obj = LucroTotal(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    lucro_total=lucro_total,
                    margem_lucro=porc_lucro_faturamento
                )
                db.session.add(lucro_total_obj)
            
            # Salva Lucro Produto
            lucro_produto_obj = LucroProduto.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if lucro_produto_obj:
                lucro_produto_obj.lucro_produtos = lucro_produto
                lucro_produto_obj.perc_relacao_lucro = porc_lucro_produto
            else:
                lucro_produto_obj = LucroProduto(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    lucro_produtos=lucro_produto,
                    perc_relacao_lucro=porc_lucro_produto
                )
                db.session.add(lucro_produto_obj)
            
            # Salva Lucro Serviço
            lucro_servico_obj = LucroServico.query.filter_by(
                usuario_id=usuario_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            if lucro_servico_obj:
                lucro_servico_obj.lucro_servicos = lucro_servico
                lucro_servico_obj.perc_relacao_lucro = porc_lucro_servico
            else:
                lucro_servico_obj = LucroServico(
                    usuario_id=usuario_id,
                    periodo_inicio=periodo_inicio,
                    periodo_fim=periodo_fim,
                    lucro_servicos=lucro_servico,
                    perc_relacao_lucro=porc_lucro_servico
                )
                db.session.add(lucro_servico_obj)
            
            # Commit dos dados financeiros
            db.session.commit()
            
            logger.debug(f"💰 Dados financeiros salvos com sucesso")
            
            return {
                'faturamento_total': faturamento_total,
                'faturamento_produto': faturamento_produto,
                'faturamento_servico': faturamento_servico,
                'lucro_total': lucro_total,
                'lucro_produto': lucro_produto,
                'lucro_servico': lucro_servico,
                'porcentagens': {
                    'faturamento_produto': porc_faturamento_produto,
                    'faturamento_servico': porc_faturamento_servico,
                    'lucro_produto': porc_lucro_produto,
                    'lucro_servico': porc_lucro_servico,
                    'lucro_faturamento': porc_lucro_faturamento
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados financeiros: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def get_financial_summary(user_id, start_date=None, end_date=None):
        """
        Busca resumo financeiro do usuário para um período
        
        Args:
            user_id (int): ID do usuário
            start_date (str, optional): Data inicial
            end_date (str, optional): Data final
            
        Returns:
            dict: Resumo financeiro completo
        """
        
        try:
            # Define datas padrão se não fornecidas
            if not start_date:
                start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            periodo_inicio = datetime.strptime(start_date, '%Y-%m-%d')
            periodo_fim = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Busca dados financeiros
            faturamento_total = FaturamentoTotal.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            faturamento_produto = FaturamentoProduto.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            faturamento_servico = FaturamentoServico.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            lucro_total = LucroTotal.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            lucro_produto = LucroProduto.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            lucro_servico = LucroServico.query.filter_by(
                usuario_id=user_id,
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim
            ).first()
            
            # Monta resumo
            summary = {
                'periodo': {
                    'inicio': start_date,
                    'fim': end_date
                },
                'faturamento': {
                    'total': faturamento_total.valor_total if faturamento_total else 0,
                    'produto': faturamento_produto.valor_produtos if faturamento_produto else 0,
                    'servico': faturamento_servico.valor_servicos if faturamento_servico else 0,
                    'porcentagem_produto': faturamento_produto.perc_relacao_total if faturamento_produto else 0,
                    'porcentagem_servico': faturamento_servico.perc_relacao_total if faturamento_servico else 0
                },
                'lucro': {
                    'total': lucro_total.lucro_total if lucro_total else 0,
                    'produto': lucro_produto.lucro_produtos if lucro_produto else 0,
                    'servico': lucro_servico.lucro_servicos if lucro_servico else 0,
                    'porcentagem_produto': lucro_produto.perc_relacao_lucro if lucro_produto else 0,
                    'porcentagem_servico': lucro_servico.perc_relacao_lucro if lucro_servico else 0,
                    'margem_lucro': lucro_total.margem_lucro if lucro_total else 0
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar resumo financeiro: {str(e)}")
            return None
    
    @staticmethod
    def sync_tasks_endpoint():
        """
        Endpoint para sincronização de tarefas via API REST
        
        Returns:
            dict: Resultado da sincronização
        """
        from flask import session, request
        
        user_id = session.get('user_id')
        
        if not user_id:
            return {
                'success': False,
                'message': 'Usuário não autenticado',
                'data': None
            }
        
        # Pega parâmetros opcionais da requisição
        start_date = request.json.get('start_date') if request.json else None
        end_date = request.json.get('end_date') if request.json else None
        
        result = TarefaController.fetch_and_process_tasks(user_id, start_date, end_date)
        return result

