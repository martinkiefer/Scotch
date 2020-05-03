grammar functiondescription;


function 
	: statement_list # func
    ;

statement_list
	: statement+
	;

statement
	: assignment #assignmentr
	| conditional_assignment #cassignment
    | 'for' ID 'in' numexp 'to' numexp LBRACE statement_list RBRACE #for  
	/*| 'if' LPAREN bool_condition RPAREN LBRACE statement_list RBRACE ('else' LBRACE statement_list RBRACE)? #conditional */
	;

bool_condition 
	: vector_term_l1 '=' vector_term_l1 #bool_condition_eq
	| vector_term_l1 '!=' vector_term_l1 #bool_condition_neq
	| arithmetic_term_l1 '>' arithmetic_term_l1 #bool_condition_ge
	| arithmetic_term_l1 '<' arithmetic_term_l1 #bool_condition_le
	;

conditional_assignment
    :  vectorvar ASSIGNMENT bool_condition  '?' vector_term_l1 ':' vector_term_l1 ';' #conditional_assignment_vv
	|  vectorvar ASSIGNMENT bool_condition  '?' arithmetic_term_l1 ':' vector_term_l1 ';' #conditional_assignment_av
	|  vectorvar ASSIGNMENT bool_condition  '?' vector_term_l1 ':' arithmetic_term_l1 ';' #conditional_assignment_va
	|  vectorvar ASSIGNMENT bool_condition  '?' arithmetic_term_l1 ':' arithmetic_term_l1 ';' #conditional_assignment_aa
    ;

assignment
    : vectorvar ASSIGNMENT vector_term_l1 ';' #vector_assignment
    | vectorvar ASSIGNMENT arithmetic_term_l1 ';' #arithmetic_assignment
    ;

vector_term :
	| vector_term_l1
	| arithmetic_term_l1
	;

arithmetic_term_l1
	: arithmetic_term_l2 ((PLUS | MINUS) arithmetic_term_l2)*; 

arithmetic_term_l2
	: arithmetic_signed_atom ((TIMES | DIV) arithmetic_signed_atom)*; 

arithmetic_signed_atom
	: MINUS arithmetic_signed_atom #neg_arithmetic_signed_atom
	| PLUS arithmetic_signed_atom #pos_arithmetic_signed_atom
	| arithmetic_atom #plain_arithmetic_signed_atom
	;

arithmetic_atom
	: LPAREN arithmetic_term_l1 RPAREN #paren_arith_atom
	| 'unsigned' LPAREN vector_term_l1 RPAREN #unsigned_vector_conversion
	| 'signed' LPAREN vector_term_l1 RPAREN #signed_vector_conversion
	| INT #arithmetic_literal
	| ID #arithmetic_variable
	;

vector_term_l1
	: vector_term_l2 (CARET vector_term_l2)*
	;

vector_term_l2
	: vector_term_l3 (OR vector_term_l3)*
	; 

vector_term_l3
	: vector_term_l4 (AND vector_term_l4)*
	; 

vector_term_l4
	: vector #simple_vector
	| 'expand' LPAREN vector_term_l1 ',' numexp RPAREN #expand_term
	| 'parity' LPAREN vector_term_l1 RPAREN #parity_term
	| LPAREN vector_term_l1 RPAREN #paren_term
	;

vector 
	: vectorvar	#full_vector
	| vectorvar LPAREN numexp DOWNTO numexp RPAREN #vector_range
	| vectorvar LPAREN numexp RPAREN #vector_single
	| BITSTRING #vector_literal
    ;

vectorvar 
	: ID #plain_vector_var
	| vectorvar LBRACKET numexp RBRACKET #indexed_vector_var
	; 

// A numeric expression that can be used as an index to vector sizes
// We do only allow basic arithmetic in here.
numexp
   : numterm ((PLUS | MINUS) numterm)*
   ;

numterm
   : signed_atom ((TIMES | DIV) signed_atom)*
   ;

signed_atom
	: PLUS signed_atom #pos_nexp_signed_atom
	| MINUS signed_atom #neg_nexp_signed_atom
	| atom #nexp_atom
	;

atom 
	: ID #nexp_variable
	| INT #nexp_literal
	| LPAREN numexp RPAREN #nexp_paren
	;

ASSIGNMENT : '<=';

LBRACKET : '[';
RBRACKET : ']';

LBRACE : '{';
RBRACE : '}';

LPAREN : '(';
RPAREN : ')';
CARET : '^';
AND : '&';
OR : '|';

DOWNTO : ' downto ';

PLUS: '+';


MINUS : '-';


TIMES : '*';


DIV : '/';

INT: ('0'..'9')+;

ID: ('a'..'z'|'A'..'Z' | '0'..'9')+;


BITSTRING: '\'' ('0' | '1')+ '\''; 

Whitespace
    :   [ \t]+
        -> skip
    ;

Newline
    :   (   '\r' '\n'?
        |   '\n'
        )
        -> skip
    ;
