from functiondescriptionLexer import functiondescriptionLexer
from functiondescriptionParser import functiondescriptionParser
from AstVisitor import AstVisitor
from AstTransform import LoopUnrollingVisitor, ConstantVariableBindingVisitor, AssignmentBindingVisitor, EvaluationVisitor, VariableWidthSettingVisistor
from AstRead import collectAssignments
import AstNodes
from Functions import SelectorFunctionGenerator, UpdateFunctionGenerator
from FunctionPackageGenerator import FunctionPackageGenerator
import antlr4
import sys
import json
import os

class TypePrintVisitor:
	def visit(self, x):
		print(type(x))

def create_statement_list(file_name, arithmetic_variable_bindings, vector_variable_bindings, variable_width_bindings):
    lexer = functiondescriptionLexer(antlr4.FileStream(file_name))
    stream = antlr4.CommonTokenStream(lexer)
    parser = functiondescriptionParser(stream)
    tree = parser.function()

    visitor = AstVisitor()
    ast = visitor.visit(tree)

    #Unroll loops
    ast.acceptTopDown(LoopUnrollingVisitor())
    #Bind arithmetic variables
    ast.acceptTopDown(ConstantVariableBindingVisitor(arithmetic_variable_bindings, AstNodes.ArithmeticVariable))
    #Bind vector variables
    ast.acceptTopDown(ConstantVariableBindingVisitor(vector_variable_bindings, AstNodes.VectorVariable))
    ast.acceptTopDown(ConstantVariableBindingVisitor(vector_variable_bindings, AstNodes.IndexedVectorVariable))
    #Evaluate arithmetic terms in indexed variables and vector selects.
    ast.acceptTopDown(EvaluationVisitor())
    #Mark variables set by previous assignments
    ast.acceptTopDown(AssignmentBindingVisitor())

    ast.acceptTopDown(VariableWidthSettingVisistor(variable_width_bindings))
   
    #At this point, there should be only assignments or conditional assignment nodes in the tree.
    return collectAssignments(ast)

def create_selector_function_statement_list(data):
    selector_arithmetic_variables = {
        "selector_seed_size" : data["selector_seed_size"]
    }

    selector_vector_variables = {
        "v" : "in",
        "seed" : "in",
        "index" : "out"
    }

    #Create the ASTs for selector and update function
    selector_width = {
        "seed" : data["selector_seed_size"],
        "v" : data["value_size"],
        "offset" : data["offset_max_size"]
    }
    selector_width.update(data['selector_function_variables'])
    return create_statement_list(data['selector_function_file'], selector_arithmetic_variables, selector_vector_variables, selector_width)

def create_compute_function_statement_list(data):
    compute_arithmetic_variables = {
        "update_seed_size" : data["update_seed_size"]
    }

    compute_vector_variables = {
        "v" : "in",
        "seed" : "in"
    }

    #Create the ASTs for selector and update function
    compute_width = {
        "seed" : data["update_seed_size"],
        "v" : data["value_size"],
        "offset" : data["compute_out_size"]
    }
    compute_width.update(data['compute_function_variables'])
    return create_statement_list(data['compute_function_file'], compute_arithmetic_variables, compute_vector_variables, compute_width)

def create_cupdate_function_statement_list(data):
        update_arithmetic_variables = {
            "update_seed_size" : data["update_seed_size"]
        }

        update_vector_variables = {
            "v" : "in",
            "seed" : "in",
            "state" : "in"
        }

        update_width = {
            "seed" : data["update_seed_size"],
            "v" : data["compute_out_size"],
            "state" : data["state_size"],
            "outstate" : data["state_size"]
        }
        update_width.update(data['update_function_variables'])
        return create_statement_list(data['update_function_file'], update_arithmetic_variables, update_vector_variables, update_width)

def create_update_function_statement_list(data):
        update_arithmetic_variables = {
            "update_seed_size" : data["update_seed_size"]
        }

        update_vector_variables = {
            "v" : "in",
            "seed" : "in",
            "state" : "in"
        }

        update_width = {
            "seed" : data["update_seed_size"],
            "v" : data["value_size"],
            "state" : data["state_size"],
            "outstate" : data["state_size"]
        }
        update_width.update(data['update_function_variables'])
        return create_statement_list(data['update_function_file'], update_arithmetic_variables, update_vector_variables, update_width)
