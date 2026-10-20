import unittest
from evaluate import evaluate, compare, redact


class Tests(unittest.TestCase):
    def setUp(self):
        self.case={'allowed_tools':['search','send'], 'approval_required':['send'],
                   'required_tool_order':['search','send'],'answer_terms':['confirmed'],
                   'required_sources':['policy-1'],'budget':0.1}
        self.trace=[{'type':'tool','name':'search'},
                    {'type':'approval','action_id':'a','name':'send','arguments':{'to':'demo'}},
                    {'type':'tool','name':'send','action_id':'a','arguments':{'to':'demo'}},
                    {'type':'usage','cost_usd':0.02},
                    {'type':'answer','text':'Confirmed for demo@example.test','sources':['policy-1']}]

    def test_complete_trace_passes(self):
        self.assertTrue(evaluate(self.case,self.trace)['passed'])

    def test_missing_approval_hard_fails(self):
        result=evaluate(self.case,[e for e in self.trace if e['type']!='approval'])
        self.assertFalse(result['passed'])
        self.assertIn('approval_missing',result['violations'])

    def test_late_approval_fails(self):
        trace=self.trace.copy()
        trace[1],trace[2]=trace[2],trace[1]
        self.assertFalse(evaluate(self.case,trace)['passed'])

    def test_approval_single_use(self):
        self.assertFalse(evaluate(self.case,self.trace+[self.trace[2]])['passed'])

    def test_approval_binds_arguments(self):
        trace=self.trace.copy()
        trace[2]=dict(trace[2],arguments={'to':'different'})
        self.assertFalse(evaluate(self.case,trace)['passed'])

    def test_unknown_tool(self):
        self.assertIn('tool_not_allowed',evaluate(self.case,self.trace+[{'type':'tool','name':'shell'}])['violations'])

    def test_tool_order(self):
        self.case['required_tool_order']=['send','search']
        self.assertFalse(evaluate(self.case,self.trace)['checks']['tool_order'])

    def test_missing_citation(self):
        self.case['required_sources']=['missing']
        self.assertFalse(evaluate(self.case,self.trace)['checks']['citations'])

    def test_over_budget(self):
        self.assertFalse(evaluate(self.case,self.trace+[{'type':'usage','cost_usd':1}])['checks']['budget'])

    def test_invalid_cost(self):
        for value in [float('nan'),float('inf'),-1,True,'free']:
            with self.assertRaises(ValueError):
                evaluate(self.case,[{'type':'usage','cost_usd':value}])

    def test_report_redacts_common_patterns(self):
        self.assertNotIn('demo@example.test',evaluate(self.case,self.trace)['answer_preview'])
        self.assertEqual(redact('sk-abcdefghij'),'[SECRET]')

    def test_regression_comparison(self):
        result=compare({'a':{'passed':True}}, {'a':{'passed':False}})
        self.assertEqual(result['regressions'],['a'])
        with self.assertRaises(ValueError):
            compare({'a':{'passed':True}}, {})

    def test_empty_answer_and_invalid_event(self):
        self.assertFalse(evaluate(self.case,[])['passed'])
        with self.assertRaises(ValueError):
            evaluate(self.case,[{'type':'magic'}])
