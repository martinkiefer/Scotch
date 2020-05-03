from functiondescriptionVisitor import functiondescriptionVisitor
import functiondescriptionParser
import AstNodes

class AstVisitor(functiondescriptionVisitor):
    def getVisitedChildren(self, ctx, filter_type=None):
        if filter_type is None:
            return list(map(lambda x : self.visit(x), ctx.children))
        else:
            return list(map(lambda x : self.visit(x), filter(
                lambda x : isinstance(x,filter_type) ,ctx.children)))

    def visitFunc(self,ctx):
        return self.visit(ctx.children[0])

    def visitStatement_list(self,ctx):
        return AstNodes.StatementList(self.getVisitedChildren(ctx))

    def visitAssignmentr(self,ctx):
        return self.visit(ctx.children[0])

    def visitCassignment(self,ctx):
        return self.visit(ctx.children[0])

    def visitFor(self,ctx):
        return AstNodes.ForLoop(self.visit(ctx.children[7]),ctx.children[1].getText(),self.visit(ctx.children[3]),self.visit(ctx.children[5]))

    #def visitConditional(self,ctx):
    #    cond_part = self.visit(ctx.children[2])
    #    if_part = self.visit(ctx.children[5])
    #    else_part = None
    #    if len(ctx.children) > 7:
    #        else_part = self.visit(ctx.children[9])
    #    return AstNodes.Conditional(cond_part, if_part, else_part)       

    def visitBool_condition_eq(self,ctx):
        operator = ctx.children[1].getText()
        return AstNodes.BooleanExpression("=", self.visit(ctx.children[0]),self.visit(ctx.children[2]))

    def visitBool_condition_neq(self,ctx):
        operator = ctx.children[1].getText()
        return AstNodes.BooleanExpression("!=", self.visit(ctx.children[0]),self.visit(ctx.children[2]))

    def visitBool_condition_ge(self,ctx):
        operator = ctx.children[1].getText()
        return AstNodes.BooleanExpression(">", self.visit(ctx.children[0]),self.visit(ctx.children[2]))

    def visitBool_condition_le(self,ctx):
        operator = ctx.children[1].getText()
        return AstNodes.BooleanExpression("<", self.visit(ctx.children[0]),self.visit(ctx.children[2]))

    def visitVector_assignment(self,ctx):
        return AstNodes.Assignment(self.visit(ctx.children[0]), self.visit(ctx.children[2]), False)

    def visitArithmetic_assignment(self,ctx):
        return AstNodes.Assignment(self.visit(ctx.children[0]), self.visit(ctx.children[2]), True)

    def visitConditional_assignment_vv(self,ctx):
        return AstNodes.ConditionalAssignment(self.visit(ctx.children[2]), self.visit(ctx.children[0]), self.visit(ctx.children[4]), self.visit(ctx.children[6]), False, False)

    def visitConditional_assignment_va(self,ctx):
        return AstNodes.ConditionalAssignment(self.visit(ctx.children[2]), self.visit(ctx.children[0]), self.visit(ctx.children[4]), self.visit(ctx.children[6]), False, True)
 
    def visitConditional_assignment_av(self,ctx):
        return AstNodes.ConditionalAssignment(self.visit(ctx.children[2]), self.visit(ctx.children[0]), self.visit(ctx.children[4]), self.visit(ctx.children[6]), True, False)

    def visitConditional_assignment_aa(self,ctx):
        return AstNodes.ConditionalAssignment(self.visit(ctx.children[2]), self.visit(ctx.children[0]), self.visit(ctx.children[4]), self.visit(ctx.children[6]), True, True)

    def visitVector_term(self,ctx):
        return self.visit(ctx.children[0])

    def visitNumexp(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head
        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.BinaryArithmeticOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitNumterm(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        for i in range(1,len(ctx.children), 2):
            head = AstNodes.BinaryArithmeticOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitArithmetic_term_l1(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.BinaryArithmeticOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitArithmetic_term_l2(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.BinaryArithmeticOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitNeg_arithmetic_signed_atom(self,ctx):
        return AstNodes.UnaryArithmeticOperation("arith_neg", self.visit(ctx.children[1]))

    def visitNeg_nexp_signed_atom(self,ctx):
        return AstNodes.UnaryArithmeticOperation("arith_neg", self.visit(ctx.children[1]))

    def visitPos_arithmetic_signed_atom(self,ctx):        
        return self.visit(ctx.children[1])

    def visitPos_nexp_signed_atom(self,ctx):        
        return self.visit(ctx.children[1])

    def visitNexp_atom(self,ctx):        
        return self.visit(ctx.children[0])

    def visitPlain_arithmetic_signed_atom(self,ctx):
        return self.visit(ctx.children[0])      

    def visitParen_arith_atom(self,ctx):
        return self.visit(ctx.children[1])  

    def visitParen_arith_atom(self,ctx):
        return self.visit(ctx.children[1])  

    def visitUnsigned_vector_conversion(self,ctx):
        return AstNodes.Vector2ArithmeticConversion("unsigned", self.visit(ctx.children[2]))

    def visitSigned_vector_conversion(self,ctx):
        return AstNodes.Vector2ArithmeticConversion("signed", self.visit(ctx.children[2]))

    def visitArithmetic_literal(self,ctx):
        return AstNodes.ArithmeticLiteral(int(ctx.getText()))

    def visitNexp_literal(self,ctx):
        return AstNodes.ArithmeticLiteral(int(ctx.getText()))

    def visitArithmetic_variable(self,ctx):
        return AstNodes.ArithmeticVariable(ctx.getText())

    def visitNexp_variable(self,ctx):
        return AstNodes.ArithmeticVariable(ctx.getText())

    def visitVector_term_l1(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.VectorOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitVector_term_l2(self,ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.VectorOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitVector_term_l3(self, ctx):
        head = self.visit(ctx.children[0])
        if len(ctx.children) == 1:
            return head

        #We have at least one operator.
        for i in range(1,len(ctx.children), 2):
            head = AstNodes.VectorOperation(ctx.children[i].getText(), head, self.visit(ctx.children[i+1]))
        return head

    def visitParity_term(self, ctx):
        return AstNodes.ParityOperation("parity",self.visit(ctx.children[2]))

    def visitExpand_term(self, ctx):
        return AstNodes.ExpandOperation(self.visit(ctx.children[2]),self.visit(ctx.children[4]))

    def visitParen_term(self, ctx):
        return self.visit(ctx.children[1])

    def visitNexp_paren(self, ctx):
        return self.visit(ctx.children[1])

    def visitFull_vector(self, ctx):
        return self.visit(ctx.children[0])    

    def visitVector_range(self, ctx):
        #TODO: Needs logic for arbitrary expressions
        return AstNodes.VectorSelect(self.visit(ctx.children[2]),self.visit(ctx.children[4]),self.visit(ctx.children[0]))

    def visitVector_single(self, ctx):
        #TODO: Needs logic for arbitrary expressions
        return AstNodes.VectorSelect(self.visit(ctx.children[2]),self.visit(ctx.children[2]),self.visit(ctx.children[0]))

    def visitSimple_vector(self, ctx):
        return self.visit(ctx.children[0])  

    def visitVector_literal(self, ctx):
        return AstNodes.VectorLiteral("b2",ctx.getText()) 

    def visitPlain_vector_var(self, ctx):
        return AstNodes.VectorVariable(ctx.getText())

    def visitIndexed_vector_var(self, ctx):
        return AstNodes.IndexedVectorVariable(ctx.children[0].getText(), self.visit(ctx.children[2]))
