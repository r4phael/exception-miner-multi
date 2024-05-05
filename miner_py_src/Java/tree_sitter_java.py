from tree_sitter._binding import Query

from tree_sitter_languages import get_language, get_parser

JAVA_LANGUAGE = get_language('java')

parser = get_parser('java')
parser.set_language(JAVA_LANGUAGE)

QUERY_METHOD_DEF: Query = JAVA_LANGUAGE.query(
    "(method_declaration) @function.def")

QUERY_METHOD_IDENTIFIER: Query = JAVA_LANGUAGE.query(
    """(method_declaration (identifier) @function.def)""")

QUERY_METHOD_BODY: Query = JAVA_LANGUAGE.query(
    """(method_declaration body: (block) @body)""")

QUERY_EXPRESSION_STATEMENT: Query = JAVA_LANGUAGE.query(
    """(expression_statement) @expression.stmt""")

QUERY_TRY_STMT: Query = JAVA_LANGUAGE.query(
    """(try_statement) @try.statement""")

QUERY_TRY_CATCH: Query = JAVA_LANGUAGE.query(
    """(try_statement
        (catch_clause)* @catch.clause) @try.stmt""")

QUERY_CATCH_CLAUSE: Query = JAVA_LANGUAGE.query(
    """(catch_clause) @catch.clause""")

QUERY_CATCH_IDENTIFIER_BODY: Query = JAVA_LANGUAGE.query(
    """
    (catch_clause 
        (catch_formal_parameter 
            (identifier) @catch.identifier)
        (block) @catch.body
    )
    """
)

QUERY_CATCH_BLOCK: Query = JAVA_LANGUAGE.query(
    """(catch_clause (block) @body)""")

QUERY_CATCH_STATEMENTS: Query = JAVA_LANGUAGE.query(
    """(catch_clause (block [(_) @catch.expression]*))""")

QUERY_CATCH_EXPRESSION: Query = JAVA_LANGUAGE.query(
    """(catch_clause (_) @catch.expression)""")

QUERY_FIND_IDENTIFIERS: Query = JAVA_LANGUAGE.query(
    """(identifier) @identifier""")

QUERY_THROW_STATEMENT: Query = JAVA_LANGUAGE.query(
    """(throw_statement) @throw.stmt""")

QUERY_THROW_STATEMENT_IDENTIFIER: Query = JAVA_LANGUAGE.query(
    """(throw_statement 
	(object_creation_expression
                (type_identifier) @throw.identifier
            ) @throw.identifier)""")

QUERY_FINALLY_BLOCK: Query = JAVA_LANGUAGE.query(
    """ (finally_clause) @finally.clause""")

QUERY_CATCH_ASSIGNMENT: Query = JAVA_LANGUAGE.query(
    """(catch_clause 
        (catch_formal_parameter 
            (identifier)? @catch.type 
            (identifier)? @catch.identifier 
        )
        (block
            (local_variable_declaration
                (type_identifier)? @type.identifier
                (variable_declarator
                    (identifier) @variable.identifier
                    (method_invocation
                        (identifier) @exception.identifier
                        (identifier) @method.identifier
                    )
                )
            )
        )
    )""")
