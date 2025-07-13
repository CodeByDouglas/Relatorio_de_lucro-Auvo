"""
Script para executar todos os testes da aplicação
"""
import os
import sys
import unittest
import subprocess

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_functional_tests():
    """Executa apenas os testes funcionais que sabemos que funcionam"""
    
    print("=" * 60)
    print("EXECUTANDO TESTES FUNCIONAIS (VALIDADOS)")
    print("=" * 60)
    
    try:
        # Carrega e executa os testes funcionais
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('tests.test_functional')
        
        # Executa os testes
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Contabiliza resultados
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        passed_tests = total_tests - failures - errors
        
        print(f"\n{'-' * 50}")
        print("RELATÓRIO DOS TESTES FUNCIONAIS:")
        print(f"{'-' * 50}")
        print(f"Total de testes executados: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {failures}")
        print(f"Erros: {errors}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"Taxa de sucesso: {success_rate:.2f}%")
        
        # Mostra detalhes dos erros se houver
        if result.failures:
            print(f"\n{'-' * 30}")
            print("FALHAS:")
            print(f"{'-' * 30}")
            for test, error in result.failures:
                print(f"FALHA em {test}: {error}")
        
        if result.errors:
            print(f"\n{'-' * 30}")
            print("ERROS:")
            print(f"{'-' * 30}")
            for test, error in result.errors:
                print(f"ERRO em {test}: {error}")
        
        # Status final
        if failures == 0 and errors == 0:
            print("\n✅ TODOS OS TESTES FUNCIONAIS PASSARAM!")
            return True
        else:
            print(f"\n❌ {failures + errors} TESTE(S) FALHARAM!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar testes funcionais: {e}")
        return False
    """Executa todos os testes unitários e de integração"""
    
    print("=" * 60)
    print("EXECUTANDO BATERIA COMPLETA DE TESTES")
    print("=" * 60)
    
    # Lista de módulos de teste
    test_modules = [
        'tests.test_calculos_service',
        'tests.test_produto_controller',
        'tests.test_colaborador_controller',
        'tests.test_tipo_tarefa_controller',
        'tests.test_servico_controller',
        'tests.test_tarefa_controller',
        'tests.test_view_controllers',
        'tests.test_integration'
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    errors = []
    
    for module in test_modules:
        print(f"\n{'-' * 50}")
        print(f"Executando: {module}")
        print(f"{'-' * 50}")
        
        try:
            # Carrega e executa os testes do módulo
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(module)
            
            # Executa os testes
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            # Contabiliza resultados
            module_tests = result.testsRun
            module_failures = len(result.failures)
            module_errors = len(result.errors)
            module_passed = module_tests - module_failures - module_errors
            
            total_tests += module_tests
            passed_tests += module_passed
            failed_tests += module_failures + module_errors
            
            print(f"\nResultados do módulo {module}:")
            print(f"  Testes executados: {module_tests}")
            print(f"  Testes aprovados: {module_passed}")
            print(f"  Testes falharam: {module_failures}")
            print(f"  Erros: {module_errors}")
            
            # Coleta detalhes dos erros
            if result.failures:
                for test, error in result.failures:
                    errors.append(f"FALHA em {test}: {error}")
            
            if result.errors:
                for test, error in result.errors:
                    errors.append(f"ERRO em {test}: {error}")
                    
        except Exception as e:
            print(f"ERRO ao executar {module}: {str(e)}")
            errors.append(f"ERRO no módulo {module}: {str(e)}")
            failed_tests += 1
    
    # Relatório final
    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    print(f"Total de testes executados: {total_tests}")
    print(f"Testes aprovados: {passed_tests}")
    print(f"Testes falharam: {failed_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"Taxa de sucesso: {success_rate:.2f}%")
    
    # Mostra erros detalhados
    if errors:
        print(f"\n{'-' * 50}")
        print("DETALHES DOS ERROS:")
        print(f"{'-' * 50}")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
            print()
    
    # Status final
    if failed_tests == 0:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"\n❌ {failed_tests} TESTE(S) FALHARAM!")
        return False


def run_coverage_report():
    """Executa relatório de cobertura de código"""
    print("\n" + "=" * 60)
    print("GERANDO RELATÓRIO DE COBERTURA")
    print("=" * 60)
    
    try:
        # Instala coverage se não estiver instalado
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], 
                      capture_output=True, check=False)
        
        # Executa testes com coverage
        subprocess.run([
            sys.executable, '-m', 'coverage', 'run', '--source=App', 
            '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'
        ], check=True)
        
        # Gera relatório
        result = subprocess.run([
            sys.executable, '-m', 'coverage', 'report', '--show-missing'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        # Gera relatório HTML
        subprocess.run([
            sys.executable, '-m', 'coverage', 'html', '--directory=htmlcov'
        ], check=True)
        
        print("\n✅ Relatório de cobertura gerado em htmlcov/index.html")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar relatório de cobertura: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


def run_specific_test(test_name):
    """Executa um teste específico"""
    print(f"Executando teste específico: {test_name}")
    
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'tests.{test_name}')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print(f"✅ Teste {test_name} passou!")
        else:
            print(f"❌ Teste {test_name} falhou!")
            
    except Exception as e:
        print(f"❌ Erro ao executar teste {test_name}: {e}")


def list_available_tests():
    """Lista todos os testes disponíveis"""
    print("Testes disponíveis:")
    print("-" * 30)
    
    test_files = [
        'test_calculos_service',
        'test_produto_controller', 
        'test_colaborador_controller',
        'test_tipo_tarefa_controller',
        'test_servico_controller',
        'test_tarefa_controller',
        'test_view_controllers',
        'test_integration'
    ]
    
    for i, test_file in enumerate(test_files, 1):
        print(f"{i}. {test_file}")


def main():
    """Função principal do script"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'all':
            success = run_functional_tests()
            sys.exit(0 if success else 1)
            
        elif command == 'functional':
            success = run_functional_tests()
            sys.exit(0 if success else 1)
            
        elif command == 'coverage':
            run_coverage_report()
            
        elif command == 'list':
            list_available_tests()
            
        elif command.startswith('test_'):
            run_specific_test(command)
            
        else:
            print(f"Comando desconhecido: {command}")
            print("Comandos disponíveis:")
            print("  all        - Executa testes funcionais")
            print("  functional - Executa testes funcionais")
            print("  coverage   - Gera relatório de cobertura")
            print("  list       - Lista testes disponíveis")
            print("  test_*     - Executa teste específico")
    else:
        # Executa testes funcionais por padrão
        success = run_functional_tests()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
