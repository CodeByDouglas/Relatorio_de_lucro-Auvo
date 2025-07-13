"""
Testes unitários para o CalculosService
"""
import unittest
from unittest.mock import Mock
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.services.calculos import CalculosService


class TestCalculosService(unittest.TestCase):
    """Testes para o serviço de cálculos financeiros"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.service = CalculosService()
        
        # Dados de teste
        self.faturamento_produto = 1000.0
        self.faturamento_servico = 500.0
        self.custo_produto = 300.0
    
    def test_calcular_faturamento_total(self):
        """Testa o cálculo do faturamento total"""
        resultado = self.service.calcular_faturamento_total(
            self.faturamento_produto, 
            self.faturamento_servico
        )
        
        self.assertEqual(resultado, 1500.0)
        
        # Testa com valores zero
        resultado_zero = self.service.calcular_faturamento_total(0, 0)
        self.assertEqual(resultado_zero, 0.0)
    
    def test_calcular_lucro_produto(self):
        """Testa o cálculo do lucro de produtos"""
        resultado = self.service.calcular_lucro_produto(
            self.faturamento_produto, 
            self.custo_produto
        )
        
        self.assertEqual(resultado, 700.0)
        
        # Testa com custo maior que faturamento (prejuízo)
        resultado_prejuizo = self.service.calcular_lucro_produto(100, 200)
        self.assertEqual(resultado_prejuizo, -100.0)
    
    def test_calcular_lucro_servico(self):
        """Testa o cálculo do lucro de serviços"""
        resultado = self.service.calcular_lucro_servico(self.faturamento_servico)
        
        # Lucro de serviço é igual ao faturamento
        self.assertEqual(resultado, 500.0)
        
        # Testa com zero
        resultado_zero = self.service.calcular_lucro_servico(0)
        self.assertEqual(resultado_zero, 0.0)
    
    def test_calcular_lucro_total(self):
        """Testa o cálculo do lucro total"""
        lucro_produto = 700.0
        lucro_servico = 500.0
        
        resultado = self.service.calcular_lucro_total(lucro_produto, lucro_servico)
        
        self.assertEqual(resultado, 1200.0)
    
    def test_calcular_porcentagem_faturamento_produto(self):
        """Testa o cálculo da porcentagem de faturamento de produtos"""
        faturamento_total = 1500.0
        
        resultado = self.service.calcular_porcentagem_faturamento_produto(
            self.faturamento_produto, 
            faturamento_total
        )
        
        self.assertAlmostEqual(resultado, 66.67, places=2)
        
        # Testa divisão por zero
        resultado_zero = self.service.calcular_porcentagem_faturamento_produto(100, 0)
        self.assertEqual(resultado_zero, 0.0)
    
    def test_calcular_porcentagem_faturamento_servico(self):
        """Testa o cálculo da porcentagem de faturamento de serviços"""
        faturamento_total = 1500.0
        
        resultado = self.service.calcular_porcentagem_faturamento_servico(
            self.faturamento_servico, 
            faturamento_total
        )
        
        self.assertAlmostEqual(resultado, 33.33, places=2)
    
    def test_calcular_porcentagem_lucro_produto(self):
        """Testa o cálculo da porcentagem de lucro de produtos"""
        lucro_produto = 700.0
        lucro_total = 1200.0
        
        resultado = self.service.calcular_porcentagem_lucro_produto(
            lucro_produto, 
            lucro_total
        )
        
        self.assertAlmostEqual(resultado, 58.33, places=2)
        
        # Testa divisão por zero
        resultado_zero = self.service.calcular_porcentagem_lucro_produto(100, 0)
        self.assertEqual(resultado_zero, 0.0)
    
    def test_calcular_porcentagem_lucro_servico(self):
        """Testa o cálculo da porcentagem de lucro de serviços"""
        lucro_servico = 500.0
        lucro_total = 1200.0
        
        resultado = self.service.calcular_porcentagem_lucro_servico(
            lucro_servico, 
            lucro_total
        )
        
        self.assertAlmostEqual(resultado, 41.67, places=2)
    
    def test_calcular_porcentagem_lucro_faturamento(self):
        """Testa o cálculo da margem de lucro"""
        lucro_total = 1200.0
        faturamento_total = 1500.0
        
        resultado = self.service.calcular_porcentagem_lucro_faturamento(
            lucro_total, 
            faturamento_total
        )
        
        self.assertEqual(resultado, 80.0)
        
        # Testa divisão por zero
        resultado_zero = self.service.calcular_porcentagem_lucro_faturamento(100, 0)
        self.assertEqual(resultado_zero, 0.0)
    
    def test_calcular_todos_os_valores(self):
        """Testa o cálculo de todos os valores de uma vez"""
        resultado = self.service.calcular_todos_os_valores(
            self.faturamento_produto,
            self.faturamento_servico,
            self.custo_produto
        )
        
        # Verifica estrutura do resultado
        self.assertIn('valores', resultado)
        self.assertIn('porcentagens', resultado)
        
        # Verifica valores calculados
        valores = resultado['valores']
        self.assertEqual(valores['faturamento_total'], 1500.0)
        self.assertEqual(valores['faturamento_produto'], 1000.0)
        self.assertEqual(valores['faturamento_servico'], 500.0)
        self.assertEqual(valores['custo_produto'], 300.0)
        self.assertEqual(valores['lucro_total'], 1200.0)
        self.assertEqual(valores['lucro_produto'], 700.0)
        self.assertEqual(valores['lucro_servico'], 500.0)
        
        # Verifica porcentagens
        porcentagens = resultado['porcentagens']
        self.assertAlmostEqual(porcentagens['faturamento_produto'], 66.67, places=2)
        self.assertAlmostEqual(porcentagens['faturamento_servico'], 33.33, places=2)
        self.assertAlmostEqual(porcentagens['lucro_produto'], 58.33, places=2)
        self.assertAlmostEqual(porcentagens['lucro_servico'], 41.67, places=2)
        self.assertEqual(porcentagens['lucro_faturamento'], 80.0)
    
    def test_validar_valores(self):
        """Testa a validação de valores"""
        # Valores válidos
        self.assertTrue(self.service.validar_valores(10.0, 20.5, 0))
        
        # Valores inválidos
        self.assertFalse(self.service.validar_valores(-10.0))  # Negativo
        self.assertFalse(self.service.validar_valores('string'))  # String
        self.assertFalse(self.service.validar_valores(None))  # None
    
    def test_formatar_moeda(self):
        """Testa a formatação de valores como moeda"""
        valor = 1234.56
        
        resultado = self.service.formatar_moeda(valor)
        self.assertEqual(resultado, "R$ 1.234,56")
        
        # Testa com símbolo customizado
        resultado_custom = self.service.formatar_moeda(valor, simbolo="US$")
        self.assertEqual(resultado_custom, "US$ 1.234,56")
    
    def test_formatar_porcentagem(self):
        """Testa a formatação de porcentagens"""
        valor = 66.6666
        
        resultado = self.service.formatar_porcentagem(valor)
        self.assertEqual(resultado, "66.67%")
        
        # Testa com casas decimais customizadas
        resultado_custom = self.service.formatar_porcentagem(valor, casas_decimais=1)
        self.assertEqual(resultado_custom, "66.7%")


if __name__ == '__main__':
    unittest.main()
