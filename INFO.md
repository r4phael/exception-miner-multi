984
---------------- try-except STATS -----------------
# try-except found:                   31669
% try-except per file:                40.20%
% try-except per function definition: 19.11%

--------------- bad practice STATS ----------------
% try-pass per file:                  11.10%
% try-pass per function definition:   3.53%
# try-pass:                           5849
# generic exception handling:         9313

-------- TBLD STATS --------
#Python methods   52580
#TryNum=1         21641
#TryNum≥2         4649
#MaxTokens        7736
#AverageTokens    169.37
#MaxStatements    99
#AverageStatement 17.62
#UniqueTokens     320811
-------- Top 10 Unique Tokens Ranking --------
( - 764384
) - 764384
<NEWLINE>  - 705088
. - 561471
, - 483717
= - 403224
: - 271494
self - 185865
[ - 152946
] - 152946

-------- CBGD STATS --------
#Try-catch pairs         16346
#ExceptNum=1             12442
#ExceptNum≥2             3904
#MaxTokens of Source     11977
#AverageTokens of Source 132.97
#MaxTokens of Target     1398
#AverageTokens of Target 51.14
#UniqueTokens            105293
-------- Top 10 Unique Tokens Ranking --------
<NEWLINE> - 257280
) - 214378
( - 214376
' - 166330
. - 155395
: - 119782
, - 117768
= - 107914
self - 46013
[ - 37207

       hasCatch                                              lines                                             labels
0             1  [def post_trigger_action ( self ) : <NEWLINE> ...         [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
1             1  [def trigger_action ( self ) : <NEWLINE> , <IN...                                 [0, 0, 0, 0, 1, 1]
2             1  [def post_trigger_action ( self ) : <NEWLINE> ...                        [0, 1, 1, 1, 1, 1, 1, 1, 1]
3             1  [def has_bank_count ( device ) : <NEWLINE> , <...                                       [0, 0, 1, 1]
4             1  [def has_main_bank ( device , definitions ) : ...                                       [0, 0, 1, 1]
...         ...                                                ...                                                ...
52575         0  [def user_has_add_permission ( self , user , p...                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
52576         0  [def _check_bom ( self ) : <NEWLINE> , <INDENT...               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
52577         0  [def slowparts ( d , re , preDz , preWz , SRW ...                        [0, 0, 0, 0, 0, 0, 0, 0, 0]
52578         0  [def __init__ ( self , ** kwargs ) : <NEWLINE>...  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...
52579         0  [def __init__ ( self , field_name , row ) : <N...               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

[52580 rows x 3 columns]
                                                     try                                             except
0      [def post_trigger_action ( self ) : <NEWLINE>,...  [<INDENT> <INDENT> except Live . Base . Limita...
1      [def post_trigger_action ( self ) : <NEWLINE>,...  [<INDENT> <INDENT> except RuntimeError : <NEWL...
2      [def has_main_bank ( device , definitions ) : ...  [<INDENT> <INDENT> except ( AttributeError , R...
3      [def has_bank_names ( device , definitions ) :...  [<INDENT> <INDENT> except ( AttributeError , R...
4      [def _set_skin_light ( self , value ) : <NEWLI...  [<INDENT> except SkinColorMissingError : <NEWL...
...                                                  ...                                                ...
17830  [def fetch_tweet_data ( tweet_id : str ) -> Op...  [<INDENT> <INDENT> <INDENT> t = e . args [ 0 ]...
17831  [def fetch_open_graph_image ( url : str ) -> O...  [<INDENT> except requests . RequestException :...
17832  [def sanitize_url ( url : str ) -> Optional [ ...  [<INDENT> except ValueError : <NEWLINE>, <INDE...
17833  [def topic_links ( linkifiers_key : int , topi...  [<INDENT> <INDENT> except re2 . error : <NEWLI...
17834  [def runsource ( self , source : str , filenam...  [<INDENT> except ( ValueError , SyntaxError ) ...

[17835 rows x 2 columns]