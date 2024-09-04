#                                                                 #
#
#
#
#
#>                 ##### ##### ##### ##### #   #
#                  #     #   # #   #   #   #   #
#                  ####  #   # #####   #   #####
#                  #     #   # # #     #   #   #
#                  #     ##### #  #    #   #   #
#
#
#          ---------------------------------------------
#
#
#              Sootpaws
#
#
#
#

#
#
#                       What is Forth?
#
#
#>
#           - Programming language
#
#           - Procedural, concatenative, stack-based
#
#           - Very low level
#
#           - Suprisingly easy to make yourself!
#
#
#
#
#
#
#

#
#
#                       Some history
#
#
#>
#           - Created by Charles H. Moore in 1968
#
#           - Some standards, but lots of variation
#
#           - Made for mini- and microcomputers
#
#           - No longer used for practical applications
#
#
#
#
#
#
#

#
#
#                       An example:
#
#                    : DOUBLE DUP + ;
#>
#           - : starts a new fuction, or word
#
#           - DOUBLE is the word name
#
#           - DUP duplicates the top stack value
#
#           - + adds the top two stack values
#
#           - ; ends the word definition
#
#
#
#
#

#
#
#                       Machine state
#
#
#>      Our Forth will run on a simple virtual machine

memory = [0, 0, 0, 0] # Memory for our code to use and run from

stack = []            # The stack used for our data

returns = []          # Another stack for returning from words

execution_pointer = 0 # The next word in memory to run

input_buffer = []     # Queued user input

#
#
#

#
#
#                Primitives and higher-level words
#
#
#>
#           - Primitives: foundational words, part of
#               the language itself
#
#           - Most of the code for this Forth is primitives
#
#           - Higher-level: sequences of other words to run,
#               user-defined
#
#
#
#
#
#
#

#
#
#                         Words In Memory
#
#
#>      Remember the DOUBLE word from earlier?
#
#       This is what it looks like in memory!
#
#
#      --------------------------------------------
#       ... | [header] | (DOCOL) | &DUP | &+ | ...
#      ------------------------------|-----|-------
#                                    |     |
#                          -----------     ---------
#                          |                       |
#      --------------------V-----------------------V--------
#       ... | [header] | (DUP) | ... | [header] | (+) | ...
#      -----------------------------------------------------
#

#
#
#                         Words In Memory
#
#
#>      What about something like : QUAD DOUBLE DOUBLE ;?
#
#       How do we handle calling higher-level words?
#
#
#    ----------------------------------------------------
#     ... | [header] | (DOCOL) | &DOUBLE | &DOUBLE | ...
#    -------------------------------|---------|----------
#                                   |         |
#                         ---------------------
#                         |
#    ---------------------V----------------------
#     ... | [header] | (DOCOL) | &DUP | &+ | ...
#    ------------------------------|-----|-------
#                                  |     |

#
#
#                       What does DOCOL do?
#
#
#>
#           - Handles transferring control between
#               higher-level words
#
#           - Saves the current execution pointer to
#               the return stack
#
#           - Points execution to continue at the
#               following index
#
#
#
#
#
#

#
#
#                      DOCOL and EXECUTE:
#                  Calling higher-level words
#
#>      DOCOL is used to call higher-level words

def DOCOL(xt):
    global execution_pointer
    returns.append(execution_pointer)
    execution_pointer = xt

#       EXECUTE calls the word at the top stack value

def EXECUTE(_):
    xt = stack.pop()
    memory[xt](xt)

#
#

#
#
#                       Return stack
#
#
#>      EXIT is used at the end of a higher-level
#           word to return to where it was called from

def EXIT(_):
    global execution_pointer
    execution_pointer = returns.pop()

def CLEARRET(_):
    global returns
    returns = []

#
#
#
#

#
#
#                       Static variables
#
#
#>    Some global state tracked in fixed memory locations

var_state = 3  # ----------------  Compile-mode flag
               #                |
var_here = 2   # ---------      |  Next free memory address
               #         |      |
var_latest = 1 # --      |      |  Latest dictionary entry
               #  |      |      |
#                 V      V      V
#   memory: [0, latest, here, state]
#
#
#
#
#

#
#
#                        Static variables
#
#
#>      Getting the addresses of static variables

def LATEST(_):
    stack.append(var_latest)

def HERE(_):
    stack.append(var_here)

def STATE(_):
    stack.append(var_state)

#
#
#
#

#
#
#                       The dictionary
#
#
#>
#           - How do we find words by name?
#
#           - Search through them using a linked list
#
#           - Each entry has the word body, name, and
#               a link to the previous word
#
#           ---------------  -------------------  ---------
#                         |  |                 |  |
#           --------------|--V-----------------|--V--------
#            ... | body | prev | name | body | prev | ...
#           -----------------------------------------------
#
#

#
#
#                       The dictionary
#
#
#>      We need to be able to find dictionary entries by name

def find(name):
    entry = memory[var_latest]
    while entry != 0:
        if memory[entry + 1] == name:
            break
        entry = memory[entry]
    return entry

#
#       This will return zero if the entry wasn't found,
#       since the first entry has zero for the value of
#       the link pointer
#

#
#
#                       The dictionary
#
#
#>      We want to be able to call this as a primitive

def FIND(_):
    stack.append(find(stack.pop()))

#
#
#
#
#
#
#
#
#
#

#
#
#                  Stack manipulation primitives
#
#
#>

def DUP(_):  # x -> x x
    stack.append(stack[len(stack) - 1])

def DROP(_): # x ->
    stack.pop()

def SWAP(_): # x y -> y x
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)

#

#
#
#                      Performing arithmatic
#
#
#>

def PLUS(_):  # x y -> x + y
    stack.append(stack.pop() + stack.pop())

def MINUS(_): # x y -> x - y
    a = stack.pop()
    stack.append(stack.pop() - a)

#
#
#
#
#
#

#
#
#                  Reading and writing memory
#
#
#>

def LOAD(_):  # a -> Read the value in memory at $a
    address = stack.pop()
    stack.append(memory[address])

def STORE(_): # x a -> Write x into memory at $a
    global memory
    address = stack.pop()
    value = stack.pop()
    # This adds more space to memory if needed
    memory += [0] * (address - len(memory) + 1)
    memory[address] = value

#

#
#
#                     User input and I/O
#
#
#>

def WORD(_):     # Read a word of input from the user
    global input_buffer
    while len(input_buffer) == 0:
        input_buffer += input("> ").split(" ")
    stack.append(input_buffer.pop(0))

def PARSEINT(_): # Parse a string into a number
    stack.append(int(stack.pop()))

def TELL(_):     # Print something to the user
    print(stack.pop())

#

#
#
#                        Literal values
#
#
#>

def LIT(_): # Instead of running the next "word" in memory,
            # push it to the stack
    global execution_pointer
    execution_pointer += 1
    stack.append(memory[execution_pointer])

#            run   run  skip!  run
#           -----------------------
#            ... | LIT |  x  | ...
#           --------------|--------
#                         V
#                       stack
#

#
#
#                         Flow control
#
#
#>

def JUMP(_):       # Similar to LIT, but jumps forward
                   # (or backward) by the following value
    global execution_pointer
    execution_pointer += 1
    execution_pointer += memory[execution_pointer]

def ZEROBRANCH(_): # Similar to JUMP, but only jumps if the
                   # top value in the stack is zero
    global execution_pointer
    execution_pointer += 1
    if stack.pop() == 0:
        execution_pointer += memory[execution_pointer]


#
#
#                   Dictionary manipulation
#
#       This will be used to create dictionary headers for
#>          primitives and pre-made higher-level words

def create(name, immidiate = False):
    global memory
    entry_start = len(memory)         # New LATEST
    memory.append(memory[var_latest]) # Link to previous
    memory[var_latest] = entry_start  # Update latest
    memory.append(name)               # Name
    # Immidiate flag
    if immidiate:
        memory.append(1)
    else:
        memory.append(0)

#

#
#
#                   Dictionary manipulation
#
#
#>      Create a dictionary entry for a primitive

def def_builtin(name, func, immidiate = False):
    global memory
    create(name, immidiate)     # Create the header
    memory.append(func)         # Add the codeword

#
#
#
#
#
#
#
#

#
#
#                   Dictionary manipulation
#
#
#>      Create a higher-level word

def def_word(name, body, immidiate = False):
    create(name, immidiate)         # Header
    memory.append(DOCOL)            # Codeword
    for word in body:               # Body
        if isinstance(word, str):
            xt = find(word) + 3
            if xt == 3:
                print("Word not defined: " + word)
                exit(1)
            memory.append(xt)
        else:
            memory.append(word)


#
#
#                   Primitive dictionary entries
#
#
#>      Create dictionary entries for all the primitives

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


#
#
#                   Primitive dictionary entries
#
#
#>      The rest of them

def_builtin("+", PLUS)
def_builtin("-", MINUS)
def_builtin("@", LOAD)
def_builtin("!", STORE)
def_builtin("WORD", WORD)
def_builtin("FIND", FIND)
def_builtin("EXECUTE", EXECUTE)
def_builtin("PARSEINT", PARSEINT)
def_builtin("TELL", TELL)

#
#
#

#
#
#                     High-level words
#
#
#>      , is used to append a value to the end of memory

def_word(",", [
    "HERE", "@",    # Get the next free memory address
    "!",            # Store the thing there
    "HERE", "@",    # Get the next free address again
    "LIT", 1, "+",  # Increment it
    "HERE", "!",    # Update the global variable
"EXIT"])

#
#
#
#
#
#

#
#
#                     High-level words
#
#
#>      CREATE creates a dictionary header

def_word("CREATE", [
    "HERE", "@",        # This is where the header will go
    "LATEST", "DUP",    # Write the link pointer and
    "@", ",", "!",      #     update LATEST
    ",",                # Append name field
    "LIT", 0, ",",      # Immidiate flag
    "LIT", DOCOL, ",",  # Codeword
"EXIT"])

#
#
#
#

#
#
#                     High-level words
#
#
#>      This is the code for execute mode

def_word("[", [
    "CLEARRET", "LIT", 0, "STATE", "!",
    "WORD", "DUP", "FIND", "DUP", "0BRANCH", 8,
        "SWAP", "DROP", "LIT", 3, "+", "EXECUTE", "JUMP", -14,
        "DROP", "PARSEINT", "JUMP", -18
], immidiate = True)

#
#     Repeatedly read a word and try to find it in the dictionary
#         If found, execute it
#         Else, parse it as a number and leave it on the stack
#
#

#
#
#                     High-level words
#
#       Compile mode: similar to execute mode, but appends
#>          to memory instead of executing (unless immidiate)

def_word("]", [
    "CLEARRET", "LIT", 1, "STATE", "!",
    "WORD", "DUP", "FIND", "DUP", "0BRANCH", 19,
        "SWAP", "DROP", "DUP", "LIT", 3, "+", "SWAP",
                "LIT", 2, "+", "@", "0BRANCH", 3,
            "EXECUTE", "JUMP", -22,
            ",", "JUMP", -25,
        "DROP", "PARSEINT", "LIT", "LIT", ",", ",", "JUMP", -33
])

#
#
#

#
#
#                     High-level words
#
#
#>      Defining new high-level words

# Start a word definition
def_word(":", ["WORD", "CREATE", "]"])

# End a word definition
def_word(";", ["LIT", "EXIT", ",", "["], immidiate = True)

# Mark the most recent word defintion as immidiate
def_word("IMMIDIATE", [
    "LIT", 1, "LATEST", "@", "LIT", 2, "+", "!", "EXIT"
], immidiate = True)

#
#

#
#
#                     High-level words
#
#
#>      The last high-level word we need to define here

# Get the codeword of a word
def_word("'", [
    "WORD", "FIND", "LIT", 3, "+",      # Get the codeword
    "STATE", "@", "0BRANCH", 4,         # Compiling?
        "LIT", "LIT", ",", ",",         # Make it a literal
"EXIT"], immidiate = True)    # Runs immidiately in compile mode

#
#
#
#
#
#

#
#
#                  Final setup and main loop
#
#
#>      This is it! We now have a working Forth!

# Make the first instruction a call to the [ word
memory[0] = find("[") + 3

# Point HERE to the first word of unallocated memory
memory[var_here] = len(memory)

# Run
while True:
    xt = memory[execution_pointer]
    memory[xt](xt)
    execution_pointer += 1

#



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

#>
