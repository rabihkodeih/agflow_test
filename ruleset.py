'''
Created on Nov 25, 2018

@author: rabihkodeih
'''
from itertools import product


class RuleSet(object):
    '''
    This class models the set of rules data structure, which is simply a
    triplet of three sets:

        1. option names
        2. dependency rules
        3. conflict rules

    A configuration of options is a specific combination of truth values
    assigned for these options. An evaluation is the truth values of all
    rules under a given configuration.

    An evalution is said to be consistent if all its values are true (i.e.
    all rules are satisfied). A configuration is said to be valid if its
    corresponding evaluation is consistent.

    Testing for coherency is performed by making sure that every option
    is set at least once under all valid configurations.
    '''

    def __init__(self):
        self.options = set()
        self.dependencies = set()
        self.conflicts = set()

    def addDep(self, a, b):
        self.options.add(a)
        self.options.add(b)
        self.dependencies.add((a, b))

    def addConflict(self, a, b):
        self.options.add(a)
        self.options.add(b)
        self.conflicts.add((a, b))

    def evalDep(self, dependency, configuration):
        a, b = dependency
        var_a = configuration[a]
        var_b = configuration[b]
        return (not var_a) or var_b

    def evalConflict(self, conflict, configuration):
        a, b = conflict
        var_a = configuration[a]
        var_b = configuration[b]
        return not(var_a and var_b)

    def isConsistent(self, evaluation):
        return min(evaluation)

    def configurations(self):
        variables = list(self.options)
        combinations = product(*((True, False),)*len(variables))
        configurations = (dict(zip(variables, c)) for c in combinations)
        return configurations

    def validConfigurations(self):
        for configuration in self.configurations():
            dependcy_eval = [self.evalDep(d, configuration) for d in self.dependencies]
            conflict_eval = [self.evalConflict(c, configuration) for c in self.conflicts]
            evaluation = dependcy_eval + conflict_eval
            if self.isConsistent(evaluation):
                yield configuration

    def isCoherent(self):
        entailed = {p: False for p in self.options}
        for configuration in self.validConfigurations():
            for option, val in configuration.items():
                entailed[option] = entailed[option] or val
        return min(entailed.values())


class Options(object):
    '''
    This class models a specific configuration for any given set of rules.

    Once the "toggle" methods is invoked on an option, an internal
    update of configuration is performed in the "update" method. The update
    operation will result in a new valid configuration.

    The update operation happens by querying the rule_set object for all valid
    configurations (with a value consistent with the toggled option) and
    selecting the closest one of them to the current configuration.
    '''

    def __init__(self, rule_set):
        self.rs = rule_set
        self.configuration = {opt: False for opt in self.rs.options}

    def closestConfiguration(self, conf, confs):
        dist = (lambda x, y: sum({k: abs(x[k] - y[k]) for k in x}.values()))
        candidates = [(dist(conf, c), c) for c in confs]
        candidates.sort(key=lambda x: x[0])
        best = candidates[0][1]
        return best

    def update(self, opt):
        filter_val = self.configuration[opt]
        addmissible_confs = [c for c in self.rs.validConfigurations() if c[opt] == filter_val]
        self.configuration = self.closestConfiguration(self.configuration, addmissible_confs)

    def toggle(self, opt):
        if opt not in self.configuration:
            self.configuration[opt] = False
        self.configuration[opt] = not self.configuration[opt]
        self.update(opt)

    def selection(self):
        return set(opt for opt in self.configuration if self.configuration[opt])


# end of file
