"""
Serviços de cálculos financeiros para o sistema de relatórios

Este módulo contém todas as funções auxiliares para calcular:
- Faturamento total, produto e serviço
- Lucro total, produto e serviço  
- Porcentagens de faturamento e lucro
"""

import logging

logger = logging.getLogger(__name__)


class CalculosService:
    """Serviço para cálculos financeiros"""
    
    @staticmethod
    def calcular_faturamento_total(faturamento_produto, faturamento_servico):
        """
        Calcula o faturamento total
        
        Args:
            faturamento_produto (float): Faturamento de produtos
            faturamento_servico (float): Faturamento de serviços
            
        Returns:
            float: Faturamento total
        """
        return faturamento_produto + faturamento_servico
    
    @staticmethod
    def calcular_lucro_produto(faturamento_produto, custo_produto):
        """
        Calcula o lucro de produtos
        
        Args:
            faturamento_produto (float): Faturamento de produtos
            custo_produto (float): Custo dos produtos
            
        Returns:
            float: Lucro de produtos
        """
        return faturamento_produto - custo_produto
    
    @staticmethod
    def calcular_lucro_servico(faturamento_servico):
        """
        Calcula o lucro de serviços (igual ao faturamento)
        
        Args:
            faturamento_servico (float): Faturamento de serviços
            
        Returns:
            float: Lucro de serviços
        """
        return faturamento_servico
    
    @staticmethod
    def calcular_lucro_total(lucro_produto, lucro_servico):
        """
        Calcula o lucro total
        
        Args:
            lucro_produto (float): Lucro de produtos
            lucro_servico (float): Lucro de serviços
            
        Returns:
            float: Lucro total
        """
        return lucro_produto + lucro_servico
    
    @staticmethod
    def calcular_porcentagem_faturamento_produto(faturamento_produto, faturamento_total):
        """
        Calcula a porcentagem do faturamento de produtos
        
        Args:
            faturamento_produto (float): Faturamento de produtos
            faturamento_total (float): Faturamento total
            
        Returns:
            float: Porcentagem do faturamento de produtos
        """
        if faturamento_total == 0:
            return 0.0
        return (faturamento_produto / faturamento_total) * 100
    
    @staticmethod
    def calcular_porcentagem_faturamento_servico(faturamento_servico, faturamento_total):
        """
        Calcula a porcentagem do faturamento de serviços
        
        Args:
            faturamento_servico (float): Faturamento de serviços
            faturamento_total (float): Faturamento total
            
        Returns:
            float: Porcentagem do faturamento de serviços
        """
        if faturamento_total == 0:
            return 0.0
        return (faturamento_servico / faturamento_total) * 100
    
    @staticmethod
    def calcular_porcentagem_lucro_produto(lucro_produto, lucro_total):
        """
        Calcula a porcentagem do lucro de produtos
        
        Args:
            lucro_produto (float): Lucro de produtos
            lucro_total (float): Lucro total
            
        Returns:
            float: Porcentagem do lucro de produtos
        """
        if lucro_total == 0:
            return 0.0
        return (lucro_produto / lucro_total) * 100
    
    @staticmethod
    def calcular_porcentagem_lucro_servico(lucro_servico, lucro_total):
        """
        Calcula a porcentagem do lucro de serviços
        
        Args:
            lucro_servico (float): Lucro de serviços
            lucro_total (float): Lucro total
            
        Returns:
            float: Porcentagem do lucro de serviços
        """
        if lucro_total == 0:
            return 0.0
        return (lucro_servico / lucro_total) * 100
    
    @staticmethod
    def calcular_porcentagem_lucro_faturamento(lucro_total, faturamento_total):
        """
        Calcula a porcentagem do lucro sobre o faturamento (margem de lucro)
        
        Args:
            lucro_total (float): Lucro total
            faturamento_total (float): Faturamento total
            
        Returns:
            float: Porcentagem do lucro sobre o faturamento
        """
        if faturamento_total == 0:
            return 0.0
        return (lucro_total / faturamento_total) * 100
    
    @staticmethod
    def calcular_todos_os_valores(faturamento_produto, faturamento_servico, custo_produto):
        """
        Calcula todos os valores financeiros de uma vez
        
        Args:
            faturamento_produto (float): Faturamento de produtos
            faturamento_servico (float): Faturamento de serviços
            custo_produto (float): Custo dos produtos
            
        Returns:
            dict: Dicionário com todos os valores calculados
        """
        
        # Cálculos básicos
        faturamento_total = CalculosService.calcular_faturamento_total(faturamento_produto, faturamento_servico)
        lucro_produto = CalculosService.calcular_lucro_produto(faturamento_produto, custo_produto)
        lucro_servico = CalculosService.calcular_lucro_servico(faturamento_servico)
        lucro_total = CalculosService.calcular_lucro_total(lucro_produto, lucro_servico)
        
        # Porcentagens
        porc_faturamento_produto = CalculosService.calcular_porcentagem_faturamento_produto(faturamento_produto, faturamento_total)
        porc_faturamento_servico = CalculosService.calcular_porcentagem_faturamento_servico(faturamento_servico, faturamento_total)
        porc_lucro_produto = CalculosService.calcular_porcentagem_lucro_produto(lucro_produto, lucro_total)
        porc_lucro_servico = CalculosService.calcular_porcentagem_lucro_servico(lucro_servico, lucro_total)
        porc_lucro_faturamento = CalculosService.calcular_porcentagem_lucro_faturamento(lucro_total, faturamento_total)
        
        resultado = {
            'valores': {
                'faturamento_total': faturamento_total,
                'faturamento_produto': faturamento_produto,
                'faturamento_servico': faturamento_servico,
                'custo_produto': custo_produto,
                'lucro_total': lucro_total,
                'lucro_produto': lucro_produto,
                'lucro_servico': lucro_servico
            },
            'porcentagens': {
                'faturamento_produto': porc_faturamento_produto,
                'faturamento_servico': porc_faturamento_servico,
                'lucro_produto': porc_lucro_produto,
                'lucro_servico': porc_lucro_servico,
                'lucro_faturamento': porc_lucro_faturamento
            }
        }
        
        logger.debug(f"📊 Cálculos realizados: {resultado}")
        
        return resultado
    
    @staticmethod
    def validar_valores(*valores):
        """
        Valida se todos os valores são números válidos
        
        Args:
            *valores: Valores a serem validados
            
        Returns:
            bool: True se todos os valores são válidos
        """
        for valor in valores:
            if not isinstance(valor, (int, float)) or valor < 0:
                return False
        return True
    
    @staticmethod
    def formatar_moeda(valor, simbolo='R$'):
        """
        Formata um valor como moeda brasileira
        
        Args:
            valor (float): Valor a ser formatado
            simbolo (str): Símbolo da moeda
            
        Returns:
            str: Valor formatado como moeda
        """
        return f"{simbolo} {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def formatar_porcentagem(valor, casas_decimais=2):
        """
        Formata um valor como porcentagem
        
        Args:
            valor (float): Valor da porcentagem
            casas_decimais (int): Número de casas decimais
            
        Returns:
            str: Valor formatado como porcentagem
        """
        return f"{valor:.{casas_decimais}f}%"
