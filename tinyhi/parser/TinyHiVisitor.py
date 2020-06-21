# Generated from TinyHi.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .TinyHiParser import TinyHiParser
else:
    from TinyHiParser import TinyHiParser

# This class defines a complete generic visitor for a parse tree produced by TinyHiParser.

class TinyHiVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TinyHiParser#program.
    def visitProgram(self, ctx:TinyHiParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#statements.
    def visitStatements(self, ctx:TinyHiParser.StatementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#assignStat.
    def visitAssignStat(self, ctx:TinyHiParser.AssignStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#ifStat.
    def visitIfStat(self, ctx:TinyHiParser.IfStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#whileStat.
    def visitWhileStat(self, ctx:TinyHiParser.WhileStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#untilStat.
    def visitUntilStat(self, ctx:TinyHiParser.UntilStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#blockStat.
    def visitBlockStat(self, ctx:TinyHiParser.BlockStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#exprStat.
    def visitExprStat(self, ctx:TinyHiParser.ExprStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#block.
    def visitBlock(self, ctx:TinyHiParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#ifstat.
    def visitIfstat(self, ctx:TinyHiParser.IfstatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#whilestat.
    def visitWhilestat(self, ctx:TinyHiParser.WhilestatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#untilstat.
    def visitUntilstat(self, ctx:TinyHiParser.UntilstatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#strExpr.
    def visitStrExpr(self, ctx:TinyHiParser.StrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#indexExpr.
    def visitIndexExpr(self, ctx:TinyHiParser.IndexExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#lenExpr.
    def visitLenExpr(self, ctx:TinyHiParser.LenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#addSubExpr.
    def visitAddSubExpr(self, ctx:TinyHiParser.AddSubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#negExpr.
    def visitNegExpr(self, ctx:TinyHiParser.NegExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#callExpr.
    def visitCallExpr(self, ctx:TinyHiParser.CallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#mulDivExpr.
    def visitMulDivExpr(self, ctx:TinyHiParser.MulDivExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#numExpr.
    def visitNumExpr(self, ctx:TinyHiParser.NumExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#parenExpr.
    def visitParenExpr(self, ctx:TinyHiParser.ParenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#idExpr.
    def visitIdExpr(self, ctx:TinyHiParser.IdExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#concatExpr.
    def visitConcatExpr(self, ctx:TinyHiParser.ConcatExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#functioncall.
    def visitFunctioncall(self, ctx:TinyHiParser.FunctioncallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#actualparams.
    def visitActualparams(self, ctx:TinyHiParser.ActualparamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TinyHiParser#formalparams.
    def visitFormalparams(self, ctx:TinyHiParser.FormalparamsContext):
        return self.visitChildren(ctx)



del TinyHiParser