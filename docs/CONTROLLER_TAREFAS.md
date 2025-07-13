# Controller de Tarefas - Documentação Completa

## Visão Geral

O `TarefaController` é o controller mais complexo do sistema, responsável por:

1. **Buscar tarefas** da API Auvo com paginação automática
2. **Processar produtos e serviços** de cada tarefa
3. **Calcular dados financeiros** individuais e gerais
4. **Armazenar tarefas** individuais no banco
5. **Armazenar dados financeiros** nos respectivos models
6. **Aplicar isolamento por usuário** em todas as operações

## Funcionalidades Principais

### 1. **Busca de Tarefas com Paginação**

```python
TarefaController.fetch_and_process_tasks(user_id, start_date, end_date)
```

**Características:**

- ✅ Paginação automática (100 tarefas por página)
- ✅ Datas padrão: ontem até hoje
- ✅ Status fixo: 3 (finalizadas automaticamente ou manualmente)
- ✅ Validação de token e usuário
- ✅ Tratamento de erros completo

**Parâmetros da API:**

```json
{
  "paramFilter": {
    "startDate": "2025-07-11",
    "endDate": "2025-07-12",
    "status": 3
  },
  "page": 1,
  "pageSize": 100
}
```

### 2. **Processamento de Tarefas**

Para cada tarefa da API, o controller:

#### **Extrai Dados Essenciais:**

- `taskId` → ID da tarefa
- `idUserTo` → ID do colaborador
- `customerDescription` → Nome do cliente
- `taskType` → ID do tipo de tarefa
- `taskDate` → Data da tarefa

#### **Processa Produtos:**

- Busca produtos no banco local por `productId` e `usuario_id`
- Calcula: `custo_total = custo_unitario * quantidade`
- Acumula: `faturamento_produto += totalValue`

#### **Processa Serviços:**

- Acumula: `faturamento_servico += totalValue`
- Lucro serviço = faturamento serviço (sem custo)

### 3. **Cálculos Financeiros**

#### **Por Tarefa:**

```python
faturamento_total_tarefa = faturamento_produto + faturamento_servico
lucro_produto_tarefa = faturamento_produto - custo_produto
lucro_servico_tarefa = faturamento_servico
lucro_total_tarefa = lucro_produto + lucro_servico
```

#### **Gerais (Acumulados):**

- Soma todos os valores das tarefas do período
- Calcula todas as porcentagens necessárias
- Armazena nos models específicos

### 4. **Cálculos de Porcentagens**

```python
# Porcentagens de Faturamento
porc_faturamento_produto = (faturamento_produto / faturamento_total) * 100
porc_faturamento_servico = (faturamento_servico / faturamento_total) * 100

# Porcentagens de Lucro
porc_lucro_produto = (lucro_produto / lucro_total) * 100
porc_lucro_servico = (lucro_servico / lucro_total) * 100

# Margem de Lucro
porc_lucro_faturamento = (lucro_total / faturamento_total) * 100
```

### 5. **Armazenamento no Banco**

#### **Tabela `tarefa`:**

- Dados individuais de cada tarefa
- JSON completo com detalhes e cálculos
- Isolamento por `usuario_id`

#### **Tabelas Financeiras:**

- `faturamento_total` - Faturamento geral do período
- `faturamento_produto` - Faturamento e % de produtos
- `faturamento_servico` - Faturamento e % de serviços
- `lucro_total` - Lucro geral e margem
- `lucro_produto` - Lucro e % de produtos
- `lucro_servico` - Lucro e % de serviços

## Estrutura do Controller

### **Métodos Principais:**

1. **`fetch_and_process_tasks()`**

   - Método principal de entrada
   - Coordena todo o processo

2. **`_fetch_all_tasks_from_api()`**

   - Busca com paginação automática
   - Trata erros de API

3. **`_process_and_save_tasks()`**

   - Processa cada tarefa individualmente
   - Calcula valores financeiros
   - Salva no banco

4. **`_calculate_and_save_financial_data()`**

   - Calcula porcentagens
   - Salva dados financeiros nos models

5. **`get_financial_summary()`**

   - Busca resumo financeiro de um período
   - Retorna dados formatados

6. **`sync_tasks_endpoint()`**
   - Endpoint para API REST
   - Integração com sistema de sessões

## Serviço de Cálculos

### **CalculosService** (`App/services/calculos.py`)

Centraliza todas as fórmulas de cálculo:

```python
# Cálculos básicos
calcular_faturamento_total()
calcular_lucro_produto()
calcular_lucro_servico()
calcular_lucro_total()

# Porcentagens
calcular_porcentagem_faturamento_produto()
calcular_porcentagem_faturamento_servico()
calcular_porcentagem_lucro_produto()
calcular_porcentagem_lucro_servico()
calcular_porcentagem_lucro_faturamento()

# Utilidades
calcular_todos_os_valores()  # Faz todos os cálculos de uma vez
validar_valores()            # Valida se valores são válidos
formatar_moeda()            # Formata valores como moeda
formatar_porcentagem()      # Formata porcentagens
```

## Isolamento por Usuário

**Todas as operações consideram `usuario_id`:**

- ✅ Busca de produtos no banco local
- ✅ Verificação de tarefas existentes
- ✅ Salvamento de tarefas individuais
- ✅ Armazenamento de dados financeiros
- ✅ Consultas de resumo financeiro

## Tratamento de Erros

### **Validações:**

- ✅ ID do usuário obrigatório
- ✅ Usuário deve existir no banco
- ✅ Token deve ser válido
- ✅ Produtos devem existir no banco local

### **Erros de API:**

- ✅ Timeout de conexão
- ✅ Erro de autorização (401)
- ✅ Erro de requisição (400)
- ✅ Erro de conexão
- ✅ Resposta malformada

### **Logs Detalhados:**

- 🔄 Iniciando operações
- ✅ Sucessos
- ❌ Erros com detalhes
- 📊 Estatísticas de processamento
- 💰 Dados financeiros calculados

## Uso e Integração

### **Endpoint REST:**

```python
POST /api/tasks/sync
{
  "start_date": "2025-07-11",  # Opcional
  "end_date": "2025-07-12"     # Opcional
}
```

### **Resposta de Sucesso:**

```json
{
  "success": true,
  "message": "Processamento concluído com sucesso. X tarefas salvas, Y atualizadas.",
  "data": {
    "tasks_processed": 150,
    "tasks_saved": 120,
    "tasks_updated": 30,
    "tasks_errors": 0,
    "financial_data": {
      "faturamento_total": 50000.0,
      "faturamento_produto": 30000.0,
      "faturamento_servico": 20000.0,
      "lucro_total": 25000.0,
      "porcentagens": {
        "faturamento_produto": 60.0,
        "faturamento_servico": 40.0,
        "lucro_produto": 50.0,
        "lucro_servico": 50.0,
        "lucro_faturamento": 50.0
      }
    }
  }
}
```

## Fluxo Completo

1. **Login** → Dashboard
2. **Sincronização automática** com período padrão (ontem-hoje)
3. **Processamento** de todas as tarefas do período
4. **Cálculos** financeiros individuais e gerais
5. **Armazenamento** em banco com isolamento por usuário
6. **Exibição** no dashboard com dados calculados

## Performance e Otimização

- ✅ **Paginação automática** para grandes volumes
- ✅ **Commits em lote** para melhor performance
- ✅ **Logs estruturados** para debugging
- ✅ **Validação prévia** para evitar processamento desnecessário
- ✅ **Rollback automático** em caso de erro crítico

## Status: ✅ IMPLEMENTADO E TESTADO

O controller de tarefas está completamente implementado e pronto para uso no dashboard do sistema.
