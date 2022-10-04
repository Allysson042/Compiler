from ExpressionToken import ExpressionToken
from Parser.ParserException import ParserException
from Symbol import Symbol
from Token import Token
from utils.check_token import is_boolean, is_relation_op, is_number

temp_index = 0
while_index = 0
if_index = [0]
temp_list: list[ExpressionToken] = []


def write_to_file(string: str, end='\n'):
  with open('3-address-code.txt', 'a') as f:
    f.write(string+end)

# get the type operation related with the operator
def get_operator_type(operator: Token):
  # arithmetics and relation operations
  if operator.token == "ADD" or operator.token == "LESS" or operator.token == "MULT" or operator.token == "DIV":
    return "INT_TYPE" 
  else: # boolean operations (&& and ||) and (<= == !=) etc...
    return "BOOL_TYPE"

# check if the operands used in the curret operation have the proper types, otherwise throw erro
def check_operands_type(op1: ExpressionToken, op2: ExpressionToken, operator: Token):
  # an arithmetic operation with op1 or op2 being of type BOOL should throw error
  if operator.token == "ADD" or operator.token == "LESS" or operator.token == "MULT" or operator.token == "DIV":
    if isinstance(op1, ExpressionToken) and op1.type == "BOOL_TYPE":
      raise ParserException("Tipo booleano inválido neste tipo de operação", op1.line)
    if isinstance(op2, ExpressionToken) and op2.type == "BOOL_TYPE":
      raise ParserException("Tipo booleano inválido neste tipo de operação", op2.line)
    if is_boolean(op1) or is_boolean(op2):
      raise ParserException("Tipo booleano inválido neste tipo de operação", op1.line)

  # a relational operation with op1 or op2 being of type BOOL should throw error
  elif is_relation_op(operator):
    if isinstance(op1, ExpressionToken) and op1.type == "BOOL_TYPE": 
      raise ParserException("Tipo inteiro inválido neste tipo de operação", op1.line)
    if isinstance(op2, ExpressionToken) and op2.type == "BOOL_TYPE":
      raise ParserException("Tipo inteiro inválido neste tipo de operação", op2.line)
    if is_boolean(op1) or is_boolean(op2):
      raise ParserException("Tipo booleano inválido neste tipo de operação", op1.line)

  # a boolean operation with op1 or op2 being of type INT should throw error
  elif operator.token =="AND" or operator.token=="OR":
    if isinstance(op1, ExpressionToken) and op1.type == "INT_TYPE": 
      raise ParserException("Tipo inteiro inválido neste tipo de operação", op1.line)
    if isinstance(op2, ExpressionToken) and op2.type == "INT_TYPE":
      raise ParserException("Tipo inteiro inválido neste tipo de operação", op1.line)
    if is_number(op1) or is_number(op2):
      raise ParserException("Tipo inteiro inválido neste tipo de operação", op1.line)

def generate_temp_expressions(expression_tokens_list: list[Token], precedence_operator: str):
  global temp_index
  new_expressions_tokens_list = []

  # if the expression is of only one factor and it is a temp, don't do anything. Eg: temp5
  if len(expression_tokens_list)==1 and 'temp' in expression_tokens_list[0].lexeme and expression_tokens_list[0].token == None:
    return []

  # expression of only one factor. Eg.: z= 2;
  if (len(expression_tokens_list)==1):
    token = expression_tokens_list[0]
    write_to_file(f'temp{temp_index} = {token.lexeme}')
    
    if token.token == "IDENTIFIER":
      temp_list.append(ExpressionToken(token=token, type=token.type)) # add temp ExpressionToken to our temp_list
    
    elif (is_number(token)):
      temp_list.append(ExpressionToken(token=token, type="INT_TYPE")) # add temp ExpressionToken to our temp_list
    else:
      temp_list.append(ExpressionToken(token=token, type="BOOL_TYPE")) # add temp ExpressionToken to our temp_list
    temp_index += 1

    return []

  for index, token in enumerate(expression_tokens_list):
    # if the token with precedence has been found we need to save the expression using it in an temp 
    if token.token == precedence_operator:
      op1 = new_expressions_tokens_list[-1]
      op2 = expression_tokens_list[index+1]
      check_operands_type(op1, op2, token)

      # temp = <PREVIOUS_TOKEN> <OPERATOR> <NEXT_TOKEN>
      # eg.: calling generate_temp_expressions with 2+2*5 and the precedence_operator='*' 
      # we're going to write -> temp = 2*5
      write_to_file(f'temp{temp_index} = {op1.lexeme} {token.lexeme} {op2.lexeme}')

      # we used the previous token in this expression, so we need to delete it from new_expressions_tokens_list
      del new_expressions_tokens_list[-1]

      # we also use the next token to be read in this expression, so we need to delete it from the array we are iterating
      del expression_tokens_list[index+1]

      # we need to replace the expression we have just read as temp in our new_expressions_tokens_list 
      expression_token = Token(lexeme = f'temp{temp_index}', token=None, line=token.line) # creating temp Token
      type = get_operator_type(token)
      temp_token = ExpressionToken(expression_token, type) # converting our temp Token to ExpressionToken
      new_expressions_tokens_list.append(temp_token)
      temp_list.append(temp_token) # add temp ExpressionToken to our temp_list
      temp_index+=1
    else:
      new_expressions_tokens_list.append(token)
      
  
  return new_expressions_tokens_list

def generate_function_parameters(expression_tokens_list: list[Token], index: int, parameters_type_list: list[str]):
  global temp_index, temp_list
  
  temp_params: list[str] = []

  params: list[Token] = [] 
  params_index = 0
 
  # if there are parameters
  if not expression_tokens_list[index+2].token == "CLOSE_PARENTHESES":
    # iterate through tokens 
    for token_expression_param in expression_tokens_list[index+2:]:
      # end of parameters list
      if token_expression_param.token == "CLOSE_PARENTHESES":
        break
      
      # another parameter expression found, so we execute the first parameters expression and then keep going
      if (token_expression_param.token == "COMMA"):
        parseExpression(params)
        temp_params.append(f'param temp{temp_index-1}')
        if (parameters_type_list[params_index] != temp_list[-1].type):
          raise ParserException(f"Tipo de parâmetro inválido. Esperado {parameters_type_list[params_index]}", line=temp_list[-1].line)
        params = []
        params_index += 1
        continue
      
      params.append(token_expression_param)

    # execute the parameter
    parseExpression(params)
    temp_params.append(f'param temp{temp_index-1}')
    if (parameters_type_list[params_index] != temp_list[-1].type):
      raise ParserException(f"Tipo de parâmetro inválido. Esperado {parameters_type_list[params_index]}", line=temp_list[-1].line)

  return temp_params

def generate_function_call(expression_tokens_list: list[Token]):
  global temp_index, temp_list

  for index, token in enumerate(expression_tokens_list):
    if (token.token == "IDENTIFIER"):
      is_last_token = index == len(expression_tokens_list)-1
      # function found
      if (not is_last_token and expression_tokens_list[index+1].token == "OPEN_PARENTHESES"):      
        # if we have parameters then call parse expressions for each one
        temp_params = generate_function_parameters(expression_tokens_list, index, token.parameters_type)

        # execute function and replace its call for temp
        for temp_param in temp_params: # for i in temp_params write_to_file param temp_i (used to call the function)
          write_to_file(temp_param)
        write_to_file(f"temp{temp_index} = call {token.lexeme}, {len(temp_params)}")
        
        expression_token = Token(lexeme = f'temp{temp_index}', token=None, line=token.line) # creating temp Token
        temp_token = ExpressionToken(expression_token, token.type) # converting our temp Token to ExpressionToken
        expression_tokens_list[index] = temp_token
        temp_list.append(temp_token) # add temp ExpressionToken to our temp_list
        temp_index += 1 

        # delete everything between the ( ) and the ( ) as well
        for token in expression_tokens_list[index+1:]:
          if token.token == "CLOSE_PARENTHESES":
            del expression_tokens_list[index+1]
            break

          del expression_tokens_list[index+1]

def parseExpression(expression_tokens_list: list[Token]):
  global temp_index
  # check if there are functions calls and execute function calls first
  generate_function_call(expression_tokens_list)

  precedence_operator_order = ['MULT',
  'DIV',
  'ADD',
  'LESS',
  'LESS_THAN_OP',
  'LESS_OR_EQ_OP',
  'GREATER_THAN_OP',
  'GREATER_OR_EQ_OP',
  'EQUALS_OP',
  'NOT_EQUAL_OP',
  'AND',
  'OR']

  open_parentheses_index= -1
  close_parentheses_index= -1

  # seting index for the first open parentheses 
  for index, token in enumerate(expression_tokens_list):
    if token.token == 'OPEN_PARENTHESES':
      open_parentheses_index = index
      break

  # seting index for the last close parentheses    
  for index, token in enumerate(expression_tokens_list):
    if token.token == 'CLOSE_PARENTHESES':
      close_parentheses_index = index

  # if the we have open parentheses recursively then call parseExpression with the expression 
  # inside the ( ) 
  if open_parentheses_index > -1:
    parseExpression(expression_tokens_list[open_parentheses_index+1:close_parentheses_index:])
    

  # if exist a parentheses, then we have called parseExpression recursively right up 
  # so we replace the expression from inside ( ) for temp
  if close_parentheses_index > -1:
    expression_token = Token(lexeme = f'temp{temp_index-1}', token=None, line=token.line) # creating temp Token
    temp_token = ExpressionToken(expression_token, temp_list[-1].type) # converting our temp Token to ExpressionToken
    expression_tokens_list = expression_tokens_list[:open_parentheses_index:] + [temp_token] + expression_tokens_list[close_parentheses_index+1::]
    

  # iterates the operators in the precedence order and generates temps expressions
  for precedence in precedence_operator_order:
    expression_tokens_list = generate_temp_expressions(expression_tokens_list, precedence)


def parse_command(command_str: str):
  global temp_index
  write_to_file(command_str.replace("#", "temp"+str(temp_index-1)))

def check_expression_type(type: str):
  global temp_list

  last_temp = temp_list[-1]
  if last_temp.type != type:
    raise ParserException(f"Tipo de atribuição inválida. Esperado {type}", last_temp.line)

def check_expression_bool_type():
  global temp_list

  last_temp = temp_list[-1]
  if last_temp.type != "BOOL_TYPE":
    raise ParserException(f"Expressão inválida. Esperado tipo booleano", last_temp.line)

def parse_var_attribution(var_symbol: Symbol):
  global temp_list, temp_index
  
  check_expression_type(var_symbol.type)

  parse_command(f"{var_symbol.lexeme} = temp{temp_index-1}")

def parse_while_command(scope_id: str): 
  global temp_list

  check_expression_bool_type()

  write_to_file(f"{scope_id}: if !temp{temp_index-1} goto F{scope_id}") 
def add_while_final_labels(scope_id: str):
  write_to_file(f"goto {scope_id}")
  write_to_file(f"F{scope_id}: ", end="")

def parse_continue_command(scope_id: str):
  write_to_file(f"goto {scope_id}")
def parse_break_command(scope_id: str):
  write_to_file(f"goto F{scope_id}")


def parse_if_command(scope_id: str):
  global if_index
  if_index.append(if_index[-1]+1)

  check_expression_bool_type()

  write_to_file(f"if temp{temp_index-1} goto A{scope_id}-{if_index[-1]}")
  write_to_file(f"if !temp{temp_index-1} goto B{scope_id}-{if_index[-1]}")
  
  write_to_file(f"A{scope_id}-{if_index[-1]}: ", end ='')
  
def parse_else_command(scope_id: str):
  global if_index
  write_to_file(f"goto B{scope_id}-{if_index[-1]+1}")
  write_to_file(f"B{scope_id}-{if_index[-1]}: ", end ='')

def add_final_conditional_command(scope_id: str, else_declared: bool):
  global if_index
  if (else_declared):
    write_to_file(f"B{scope_id}-{if_index[-1]+1}: ", end ='')
  else:
    write_to_file(f"B{scope_id}-{if_index[-1]}: ", end ='')
  
  if_index.pop()

def parse_return_command(function_type: str):
  check_expression_type(function_type)
  
  parse_command(f"return temp{temp_index-1}")

def parse_subroutine(subroutine_identifier: str):
  write_to_file(f"{subroutine_identifier}: ", end="")

def reset():
  global temp_index, temp_list
  temp_index = 0
  temp_list = []


 