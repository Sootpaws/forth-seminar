memory = [0, 0, 0, 0]
stack = []
returns = []
execution_pointer = 0
input_buffer = []

var_state = 3
var_here = 2
var_latest = 1

def DOCOL(xt):
    global execution_pointer
    returns.append(execution_pointer)
    execution_pointer = xt

def EXECUTE(_):
    xt = stack.pop()
    memory[xt](xt)

def EXIT(_):
    global execution_pointer
    execution_pointer = returns.pop()

def CLEARRET(_):
    global returns
    returns = []

def LATEST(_):
    stack.append(var_latest)

def HERE(_):
    stack.append(var_here)

def STATE(_):
    stack.append(var_state)

def find(name):
    entry = memory[var_latest]
    while entry != 0:
        if memory[entry + 1] == name:
            break
        entry = memory[entry]
    return entry

def FIND(_):
    stack.append(find(stack.pop()))

def DUP(_):
    stack.append(stack[len(stack) - 1])

def DROP(_):
    stack.pop()

def SWAP(_):
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)

def PLUS(_):
    stack.append(stack.pop() + stack.pop())

def MINUS(_):
    a = stack.pop()
    stack.append(stack.pop() - a)

def LOAD(_):
    address = stack.pop()
    stack.append(memory[address])

def STORE(_):
    global memory
    address = stack.pop()
    value = stack.pop()
    memory += [0] * (address - len(memory) + 1)
    memory[address] = value

def WORD(_):
    global input_buffer
    while len(input_buffer) == 0:
        input_buffer += input("> ").split(" ")
    stack.append(input_buffer.pop(0))

def PARSEINT(_):
    stack.append(int(stack.pop()))

def TELL(_):
    print(stack.pop())

def LIT(_):
    global execution_pointer
    execution_pointer += 1
    stack.append(memory[execution_pointer])

def JUMP(_):
    global execution_pointer
    execution_pointer += 1
    execution_pointer += memory[execution_pointer]

def ZEROBRANCH(_):
    global execution_pointer
    execution_pointer += 1
    if stack.pop() == 0:
        execution_pointer += memory[execution_pointer]

def create(name, immidiate = False):
    global memory
    entry_start = len(memory)
    memory.append(memory[var_latest])
    memory[var_latest] = entry_start
    memory.append(name)
    if immidiate:
        memory.append(1)
    else:
        memory.append(0)

def def_builtin(name, func, immidiate = False):
    global memory
    create(name, immidiate)
    memory.append(func)

def def_word(name, body, immidiate = False):
    create(name, immidiate)
    memory.append(DOCOL)
    for word in body:
        if isinstance(word, str):
            xt = find(word) + 3
            if xt == 3:
                print("Word not defined: " + word)
                exit(1)
            memory.append(xt)
        else:
            memory.append(word)

def_builtin("LIT", LIT)
def_builtin("JUMP", JUMP)
def_builtin("0BRANCH", ZEROBRANCH)
def_builtin("DOCOL", DOCOL)
def_builtin("EXIT", EXIT)
def_builtin("CLEARRET", CLEARRET)
def_builtin("LATEST", LATEST)
def_builtin("HERE", HERE)
def_builtin("STATE", STATE)
def_builtin("DUP", DUP)
def_builtin("DROP", DROP)
def_builtin("SWAP", SWAP)
def_builtin("+", PLUS)
def_builtin("-", MINUS)
def_builtin("@", LOAD)
def_builtin("!", STORE)
def_builtin("WORD", WORD)
def_builtin("FIND", FIND)
def_builtin("EXECUTE", EXECUTE)
def_builtin("PARSEINT", PARSEINT)
def_builtin("TELL", TELL)

def_word(",", [
    "HERE", "@",
    "!",
    "HERE", "@",
    "LIT", 1, "+",
    "HERE", "!",
"EXIT"])

def_word("CREATE", [
    "HERE", "@",
    "LATEST", "DUP",
    "@", ",", "!",
    ",",
    "LIT", 0, ",",
    "LIT", DOCOL, ",",
"EXIT"])

def_word("[", [
    "CLEARRET", "LIT", 0, "STATE", "!",
    "WORD", "DUP", "FIND", "DUP", "0BRANCH", 8,
        "SWAP", "DROP", "LIT", 3, "+", "EXECUTE", "JUMP", -14,
        "DROP", "PARSEINT", "JUMP", -18
], immidiate = True)

def_word("]", [
    "CLEARRET", "LIT", 1, "STATE", "!",
    "WORD", "DUP", "FIND", "DUP", "0BRANCH", 19,
        "SWAP", "DROP", "DUP", "LIT", 3, "+", "SWAP",
                "LIT", 2, "+", "@", "0BRANCH", 3,
            "EXECUTE", "JUMP", -22,
            ",", "JUMP", -25,
        "DROP", "PARSEINT", "LIT", "LIT", ",", ",", "JUMP", -33
])

def_word(":", ["WORD", "CREATE", "]"])

def_word(";", ["LIT", "EXIT", ",", "["], immidiate = True)

def_word("IMMIDIATE", [
    "LIT", 1, "LATEST", "@", "LIT", 2, "+", "!", "EXIT"
], immidiate = True)

def_word("'", [
    "WORD", "FIND", "LIT", 3, "+",
    "STATE", "@", "0BRANCH", 4,
        "LIT", "LIT", ",", ",",
"EXIT"], immidiate = True)

memory[0] = find("[") + 3
memory[var_here] = len(memory)
while True:
    xt = memory[execution_pointer]
    memory[xt](xt)
    execution_pointer += 1

# : IF IMMIDIATE ' 0BRANCH , HERE @ 0 , ;
#
# : THEN IMMIDIATE DUP 1 + HERE @ SWAP - SWAP ! ;
#
# : ELSE IMMIDIATE
#     ' JUMP , HERE @ 0 , SWAP
#     DUP 1 + HERE @ SWAP - SWAP !
# ;
#
# : FIB DUP IF
#     1 - DUP IF
#         DUP FIB SWAP 1 - FIB +
#     ELSE
#         DROP 1
#     THEN
# THEN ;
