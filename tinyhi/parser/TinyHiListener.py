# Generated from TinyHi.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TinyHiParser import TinyHiParser
else:
    from TinyHiParser import TinyHiParser

# This class defines a complete listener for a parse tree produced by TinyHiParser.
class TinyHiListener(ParseTreeListener):

    # Enter a parse tree produced by TinyHiParser#program.
    def enterProgram(self, ctx:TinyHiParser.ProgramContext):
        pass

    # Exit a parse tree produced by TinyHiParser#program.
    def exitProgram(self, ctx:TinyHiParser.ProgramContext):
        pass


    # Enter a parse tree produced by TinyHiParser#statements.
    def enterStatements(self, ctx:TinyHiParser.StatementsContext):
        pass

    # Exit a parse tree produced by TinyHiParser#statements.
    def exitStatements(self, ctx:TinyHiParser.StatementsContext):
        pass


    # Enter a parse tree produced by TinyHiParser#statement.
    def enterStatement(self, ctx:TinyHiParser.StatementContext):
        pass

    # Exit a parse tree produced by TinyHiParser#statement.
    def exitStatement(self, ctx:TinyHiParser.StatementContext):
        pass


    # Enter a parse tree produced by TinyHiParser#assignStat.
    def enterAssignStat(self, ctx:TinyHiParser.AssignStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#assignStat.
    def exitAssignStat(self, ctx:TinyHiParser.AssignStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#ifStat.
    def enterIfStat(self, ctx:TinyHiParser.IfStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#ifStat.
    def exitIfStat(self, ctx:TinyHiParser.IfStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#whileStat.
    def enterWhileStat(self, ctx:TinyHiParser.WhileStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#whileStat.
    def exitWhileStat(self, ctx:TinyHiParser.WhileStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#untilStat.
    def enterUntilStat(self, ctx:TinyHiParser.UntilStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#untilStat.
    def exitUntilStat(self, ctx:TinyHiParser.UntilStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#blockStat.
    def enterBlockStat(self, ctx:TinyHiParser.BlockStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#blockStat.
    def exitBlockStat(self, ctx:TinyHiParser.BlockStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#exprStat.
    def enterExprStat(self, ctx:TinyHiParser.ExprStatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#exprStat.
    def exitExprStat(self, ctx:TinyHiParser.ExprStatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#block.
    def enterBlock(self, ctx:TinyHiParser.BlockContext):
        pass

    # Exit a parse tree produced by TinyHiParser#block.
    def exitBlock(self, ctx:TinyHiParser.BlockContext):
        pass


    # Enter a parse tree produced by TinyHiParser#ifstat.
    def enterIfstat(self, ctx:TinyHiParser.IfstatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#ifstat.
    def exitIfstat(self, ctx:TinyHiParser.IfstatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#whilestat.
    def enterWhilestat(self, ctx:TinyHiParser.WhilestatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#whilestat.
    def exitWhilestat(self, ctx:TinyHiParser.WhilestatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#untilstat.
    def enterUntilstat(self, ctx:TinyHiParser.UntilstatContext):
        pass

    # Exit a parse tree produced by TinyHiParser#untilstat.
    def exitUntilstat(self, ctx:TinyHiParser.UntilstatContext):
        pass


    # Enter a parse tree produced by TinyHiParser#strExpr.
    def enterStrExpr(self, ctx:TinyHiParser.StrExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#strExpr.
    def exitStrExpr(self, ctx:TinyHiParser.StrExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#indexExpr.
    def enterIndexExpr(self, ctx:TinyHiParser.IndexExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#indexExpr.
    def exitIndexExpr(self, ctx:TinyHiParser.IndexExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#varExpr.
    def enterVarExpr(self, ctx:TinyHiParser.VarExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#varExpr.
    def exitVarExpr(self, ctx:TinyHiParser.VarExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#lenExpr.
    def enterLenExpr(self, ctx:TinyHiParser.LenExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#lenExpr.
    def exitLenExpr(self, ctx:TinyHiParser.LenExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#addSubExpr.
    def enterAddSubExpr(self, ctx:TinyHiParser.AddSubExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#addSubExpr.
    def exitAddSubExpr(self, ctx:TinyHiParser.AddSubExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#negExpr.
    def enterNegExpr(self, ctx:TinyHiParser.NegExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#negExpr.
    def exitNegExpr(self, ctx:TinyHiParser.NegExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#callExpr.
    def enterCallExpr(self, ctx:TinyHiParser.CallExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#callExpr.
    def exitCallExpr(self, ctx:TinyHiParser.CallExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#mulDivExpr.
    def enterMulDivExpr(self, ctx:TinyHiParser.MulDivExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#mulDivExpr.
    def exitMulDivExpr(self, ctx:TinyHiParser.MulDivExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#parenExpr.
    def enterParenExpr(self, ctx:TinyHiParser.ParenExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#parenExpr.
    def exitParenExpr(self, ctx:TinyHiParser.ParenExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#numExpr.
    def enterNumExpr(self, ctx:TinyHiParser.NumExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#numExpr.
    def exitNumExpr(self, ctx:TinyHiParser.NumExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#concatExpr.
    def enterConcatExpr(self, ctx:TinyHiParser.ConcatExprContext):
        pass

    # Exit a parse tree produced by TinyHiParser#concatExpr.
    def exitConcatExpr(self, ctx:TinyHiParser.ConcatExprContext):
        pass


    # Enter a parse tree produced by TinyHiParser#functioncall.
    def enterFunctioncall(self, ctx:TinyHiParser.FunctioncallContext):
        pass

    # Exit a parse tree produced by TinyHiParser#functioncall.
    def exitFunctioncall(self, ctx:TinyHiParser.FunctioncallContext):
        pass


    # Enter a parse tree produced by TinyHiParser#actualparams.
    def enterActualparams(self, ctx:TinyHiParser.ActualparamsContext):
        pass

    # Exit a parse tree produced by TinyHiParser#actualparams.
    def exitActualparams(self, ctx:TinyHiParser.ActualparamsContext):
        pass


    # Enter a parse tree produced by TinyHiParser#formalparams.
    def enterFormalparams(self, ctx:TinyHiParser.FormalparamsContext):
        pass

    # Exit a parse tree produced by TinyHiParser#formalparams.
    def exitFormalparams(self, ctx:TinyHiParser.FormalparamsContext):
        pass


    # Enter a parse tree produced by TinyHiParser#identifier.
    def enterIdentifier(self, ctx:TinyHiParser.IdentifierContext):
        pass

    # Exit a parse tree produced by TinyHiParser#identifier.
    def exitIdentifier(self, ctx:TinyHiParser.IdentifierContext):
        pass


    # Enter a parse tree produced by TinyHiParser#number.
    def enterNumber(self, ctx:TinyHiParser.NumberContext):
        pass

    # Exit a parse tree produced by TinyHiParser#number.
    def exitNumber(self, ctx:TinyHiParser.NumberContext):
        pass


    # Enter a parse tree produced by TinyHiParser#string.
    def enterString(self, ctx:TinyHiParser.StringContext):
        pass

    # Exit a parse tree produced by TinyHiParser#string.
    def exitString(self, ctx:TinyHiParser.StringContext):
        pass



del TinyHiParser