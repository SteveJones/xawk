#!/usr/bin/python

import lxml.etree
import lxml.html
import sys
import os
import re
import xawk_lang
import yapps

name = os.path.basename(sys.argv[0])
matchers = sys.argv[1:]

if name == "hawk":
    module = lxml.html
else:
    module = lxml.etree

debug = False

class Parser(xawk_lang.xawk):
    def xpath_string(self, xpath):
        def func(node):
            matches = node.xpath(xpath)
            matches = [match
                       if isinstance(match, basestring)
                       else module.tostring(match)
                       for match
                       in matches]
            return u"".join(matches)
        return func

    def command_evaluator(self, command, args):
        if command == "print":
            def func(node):
                if debug:
                    print "Evaluating %s on %s" % (command, args)
                values = [arg(node) for arg in args]
                print u"".join(values)
            return func
        else:
            raise Exception("Unrecognised command: %s" % command)

    def evaluator(self, actions):
        def func(node):
            for action in actions:
                action(node)
        return func

    def match_evaluator(self, xpath, action):
        def func(node):
            if debug:
                print "Searching for '%s' in: %s" % (xpath, node)
            results = node.xpath(xpath)
            if debug:
                print "  Got %s" % results
            for result in results:
                action(result)

        return func

doc = module.parse(sys.stdin)

inline = False

for program in matchers:
    # Worst options parsing ever
    if program == "-e":
        inline = True
        continue
    if inline:
        program_text = program
    else:
        fh = open(program, "rb")
        program_text = fh.read()
    inline = False
    p = Parser(xawk_lang.xawkScanner(program_text))
    matcher = yapps.runtime.wrap_error_reporter(p, "program")
    matcher(doc)
