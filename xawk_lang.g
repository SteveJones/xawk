parser xawk:
    ignore: '\\s+'
    token XPATH: '\\S*[^\\{;\\s]'
    token STRING: '"([^\\"]+|\\\\.)*"'
    token COMMAND: 'print'
    token END: '$'

    rule program: matcher_list END {{ return matcher_list }}
    rule matcher_list: {{ matchers = [] }} (matcher {{ matchers += [matcher] }})+ {{ return self.evaluator(matchers) }}
    rule matcher: XPATH (
                    actions
                    | ";" {{ actions = self.command_evaluator("print", [self.xpath_string(".")]) }}
                ) {{ return self.match_evaluator(XPATH, actions) }}
            | actions {{ return actions }}
    rule xpath_actions: XPATH actions {{ return self.match_evaluator(XPATH, actions) }}
    rule xpath_default: XPATH ";" {{ return self.match_evaluator(XPATH, self.command_evaluator("print", ".")) }}
    rule actions: "{" {{ actions = [] }} (action {{ actions += [action] }})+ "}" {{ return self.evaluator(actions) }}
    rule action: COMMAND {{ args = [] }} (arg {{ args += [arg] }})+ ";" {{ return self.command_evaluator(COMMAND, args) }}
            | "\\[" matcher_list "\\]" {{ return matcher_list }}
    rule arg: XPATH {{ return self.xpath_string(XPATH) }}
            | STRING {{ return lambda _: eval(STRING) }} 
