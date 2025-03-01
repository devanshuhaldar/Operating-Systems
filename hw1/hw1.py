

# Now you can use the `cfg` variable in your reaching definitions analysis or any other CFG-related tasks.

class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.statements = []
        self.predecessors = []
        self.successors = []


class Statement:
    def __init__(self, variable, expression):
        self.variable = variable
        self.expression = expression
    def get_used_variables(self):
        # Extract variables used in the expression
        used_variables = set()
        if isinstance(self.expression, str):
            # Assuming the expression is a simple string, extract variables
            used_variables.update(var for var in self.expression.split() if var.isalpha())
        return used_variables
    def is_assignment(self):
        return isinstance(self.expression, AssignmentExpression)


class AssignmentExpression:
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value


def create_cfg():
    # Create basic blocks
    #entry_block = BasicBlock("Entry")
    block1 = BasicBlock("Block 1")
    block2 = BasicBlock("Block 2")
    block3 = BasicBlock("Block 3")
    block4 = BasicBlock("Block 4")
    block5 = BasicBlock("Block5")
    block6 = BasicBlock("Block6")
    #exit_block = BasicBlock("Exit")

    # Create statements
    stmt1 = Statement("a", AssignmentExpression("a", "1"))
    stmt2 = Statement("b", AssignmentExpression("b", "2"))
    stmt3 = Statement("c", AssignmentExpression("c", "a + b"))
    stmt4 = Statement("d", AssignmentExpression("d", "c - a"))
    stmt5 = Statement("d", AssignmentExpression("d", "b + d"))
    stmt6 = Statement("d", AssignmentExpression("d", "a + b"))
    stmt7 = Statement("e", AssignmentExpression("e", "e + 1"))
    stmt8 = Statement("b", AssignmentExpression("b", "a + b"))
    stmt9 = Statement("e", AssignmentExpression("e", "c - a"))
    stmt10 = Statement("a", AssignmentExpression("a", "b * d"))
    stmt11 = Statement("b", AssignmentExpression("b", "a - d"))

    # Connect basic blocks
    # entry_block.successors = [block1]
    block1.predecessors = []
    block1.successors = [block2]
    
    block2.predecessors = [block1, block5]
    block2.successors = [block3]

    block3.predecessors = [block2, block4]
    block3.successors = [block4, block5]

    block4.predecessors = [block3]
    block4.successors = [block3]

    block5.predecessors = [block3]
    block5.successors = [block2, block6]
     
    block6.predecessors = [block5]
    block6.successors = []
    # exit_block.predecessors = [block2]

    # Assign statements to basic blocks
    # entry_block.statements = []
    block1.statements = [stmt1, stmt2]
    block2.statements = [stmt3, stmt4]
    block3.statements = [stmt5]
    block4.statements = [stmt6, stmt7]
    block5.statements = [stmt8, stmt9]
    block6.statements = [stmt10, stmt11]
    # exit_block.statements = []

    # Return the CFG
    return [block1, block2, block3, block4, block5, block6]

def calculate_live_expression(cfg):
    # Initialize Live-In, Live-Out, Live-Gen, and Live-Kill sets for each basic block
    live_in = {block: set() for block in cfg}
    live_out = {block: set() for block in cfg}
    live_gen = {block: set() for block in cfg}
    live_kill = {block: set() for block in cfg}

    # Perform the live expression analysis using a worklist algorithm
    worklist = list(cfg)  # Initialize worklist with all basic blocks

    while worklist:
        current_block = worklist.pop(0)

        # Calculate Live-Out set for the current block
        live_out[current_block] = set().union(*[live_in[successor] for successor in current_block.successors])

        # Calculate Live-Gen and Live-Kill sets for the current block
        for stmt in reversed(current_block.statements):
            if stmt.is_assignment():
                live_gen[current_block] = live_gen[current_block].union(stmt.get_used_variables())
                live_kill[current_block] = live_kill[current_block].union({stmt.variable})
                break

        # Calculate Live-In set for the current block
        live_in[current_block] = set.union(live_gen[current_block], live_out[current_block].difference(live_kill[current_block]))

        # Update Live-Out set for predecessors of the current block
        for predecessor in current_block.predecessors:
            worklist.append(predecessor)

    # Return the calculated sets
    return live_in, live_out, live_gen, live_kill

def calculate_reaching_definitions(cfg):
    # Initialize Kill, Gen, In, and Out sets for each basic block
    kill = {block: set() for block in cfg}
    gen = {block: set() for block in cfg}
    in_set = {block: set() for block in cfg}
    out_set = {block: set() for block in cfg}

    # Calculate Kill and Gen sets for each basic block
    for block in cfg:
        kill[block] = set()  # Initialize Kill set to an empty set

        for stmt in block.statements:
            if stmt.is_assignment():  # Check if statement is an assignment
                kill[block].add(stmt.variable)  # Add assigned variable to Kill set
                gen[block].add(stmt.variable)  # Add assigned variable to Gen set

    # Perform the reaching definitions analysis using a worklist algorithm
    worklist = list(cfg)  # Initialize worklist with all basic blocks

    while worklist:
        current_block = worklist.pop(0)

        # Calculate In set for the current block
        in_set[current_block] = set().union(*[out_set[predecessor] for predecessor in current_block.predecessors])

        # Calculate Out set for the current block
        out_set[current_block] = gen[current_block].union(in_set[current_block].difference(kill[current_block]))

        # Update In set for successors of the current block
        for successor in current_block.successors:
            if successor not in worklist:
                worklist.append(successor)

    # Return the calculated sets
    return kill, gen, in_set, out_set


def calculate_available_expressions(cfg):
    # Initialize Available-In, Available-Out, Available-Gen, and Available-Kill sets for each basic block
    available_in = {block: set() for block in cfg}
    available_out = {block: set() for block in cfg}
    available_gen = {block: set() for block in cfg}
    available_kill = {block: set() for block in cfg}

    # Perform the available expressions analysis using a worklist algorithm
    worklist = list(cfg)  # Initialize worklist with all basic blocks

    while worklist:
        current_block = worklist.pop(0)

        # Calculate Available-Out set for the current block
        available_out[current_block] = set().union(*[available_in[successor] for successor in current_block.successors])

        # Calculate Available-Gen and Available-Kill sets for the current block
        for stmt in current_block.statements:
            if stmt.is_assignment():
                expression = (stmt.variable, stmt.expression)
                available_gen[current_block] = available_gen[current_block].union({expression})
                available_kill[current_block] = available_kill[current_block].union(
                    {(var, expr) for var, expr in available_gen[current_block] if var == stmt.variable})

        # Calculate Available-In set for the current block
        available_in[current_block] = set.union(available_gen[current_block],
                                                available_out[current_block].difference(available_kill[current_block]))

        # Update Available-Out set for predecessors of the current block
        for predecessor in current_block.predecessors:
            worklist.append(predecessor)

    # Return the calculated sets
    return available_in, available_out, available_gen, available_kill



cfg = create_cfg()
# Call the function to calculate available expressions sets
available_in_set, available_out_set, available_gen_set, available_kill_set = calculate_available_expressions(cfg)

# Now you can inspect the results
# Now you can inspect the results
print("Available-In set:")
for block, expressions in available_in_set.items():
    print(f"{block.name}: {[f'({var}, {expr.value})' for var, expr in expressions]}")

print("\nAvailable-Out set:")
for block, expressions in available_out_set.items():
    print(f"{block.name}: {[f'({var}, {expr.value})' for var, expr in expressions]}")

print("\nAvailable-Gen set:")
for block, expressions in available_gen_set.items():
    print(f"{block.name}: {[f'({var}, {expr.value})' for var, expr in expressions]}")

print("\nAvailable-Kill set:")
for block, expressions in available_kill_set.items():
    print(f"{block.name}: {[f'({var}, {expr.value})' for var, expr in expressions]}")

# Example usage:

print("\n\n\n")
# Call the function to calculate reaching definitions sets
kill_set, gen_set, in_set, out_set = calculate_reaching_definitions(cfg)

# Now you can inspect the results
print("Kill set:")
for block, variables in kill_set.items():
    print(f"{block.name}: {variables}")

print("\nGen set:")
for block, variables in gen_set.items():
    print(f"{block.name}: {variables}")

print("\nIn set:")
for block, variables in in_set.items():
    print(f"{block.name}: {variables}")

print("\nOut set:")
for block, variables in out_set.items():
    print(f"{block.name}: {variables}")



# Call the function to calculate live expression sets
live_in_set, live_out_set, live_gen_set, live_kill_set = calculate_live_expression(cfg)
print("\n \n \n")
# Now you can inspect the results
print("Live-In set:")
for block, variables in live_in_set.items():
    print(f"{block.name}: {variables}")

print("\nLive-Out set:")
for block, variables in live_out_set.items():
    print(f"{block.name}: {variables}")

print("\nLive-Gen set:")
for block, variables in live_gen_set.items():
    print(f"{block.name}: {variables}")

print("\nLive-Kill set:")
for block, variables in live_kill_set.items():
    print(f"{block.name}: {variables}")
