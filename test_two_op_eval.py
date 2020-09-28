from unittest import TestCase
from toolkit import *


class TestExpressionEva(TestCase):
    def test_two_op_eval(self):
        self.assertEqual(two_op_eval(10, '+', 20), 30)
        self.assertEqual(two_op_eval(-10, '+', 20), 10)
        self.assertEqual(two_op_eval(54, '-', 20), 34)
        self.assertEqual(two_op_eval(30, '/', 4), 7.5)
        self.assertEqual(two_op_eval(10, '/', 3), 3.3333333333333335)
        self.assertEqual(two_op_eval(10, '*', 3), 30)
        self.assertEqual(two_op_eval(5, '*', 9), 45)
        with self.assertRaises(operatorNotDefind):
            two_op_eval(5, '^', 9)

    def test_get_exp_tokens(self):
        symtab = {
            "a": "10",
            "apple": "123",
            "banana": "234",
            "haha": "123",
            "log": "987"
        }
        self.assertEqual(get_exp_tokens("35*9+5", symtab), ["35", "*", "9", "+", "5"])
        self.assertEqual(get_exp_tokens("35+1232+566/1234", symtab), ["35", "+", "1232", "+", "566", "/", "1234"])
        self.assertEqual(get_exp_tokens("35*1+566/1234", symtab), ["35", "*", "1", "+", "566", "/", "1234"])
        self.assertEqual(get_exp_tokens("35*1*582+234/592*93", symtab),
                         ["35", "*", "1", "*", "582", "+", "234", "/", "592", "*", "93"])
        with self.assertRaises(symbolNotDefind):
            get_exp_tokens("a*5+b", symtab), ["10", "*", "5", "+", "b"]
        self.assertEqual(get_exp_tokens("apple+5-banana*haha/log", symtab),
                         ["123", "+", "5", "-", "234", "*", "123", "/", "987"])

    def test_expression_eval(self):
        symtab = {
            "a": "123",
            "b": "90",
            "c": "20"
        }
        self.assertEqual(expression_eval("10+5+7", symtab), 22)
        self.assertEqual(expression_eval("10-5-7", symtab), -2)
        self.assertEqual(expression_eval("2*10*5-7-2-1/10", symtab), 90.9)
        self.assertEqual(expression_eval("9*5*2-10-9-4/2+10+5+20-9+39/3+4*9", symtab), 144)
        self.assertEqual(expression_eval("12/2/3", symtab), 2)
        self.assertEqual(expression_eval("a+10-5",symtab),128)
        self.assertEqual(expression_eval("a+b*c", symtab), 1923)
        self.assertEqual(expression_eval("a", symtab), 123)
