396
---------------- try-except STATS -----------------
# try-except found:                   23451
% try-except per file:                39.25%
% try-except per function definition: 17.77%

--------------- bad practice STATS ----------------
% try-pass per file:                  11.07%
% try-pass per function definition:   3.36%
# try-pass:                           4434
# generic exception handling:         6300

-------- TBLD STATS --------
#Python methods   38916
#TryNum=1         16084
#TryNum≥2         3373
#MaxTokens        7736
#AverageTokens    171.21
#MaxStatements    99
#AverageStatement 17.64
#UniqueTokens     249890
-------- Top 10 Unique Tokens Ranking --------
( - 571400
) - 571400
<NEWLINE>  - 521648
. - 421832
, - 373380
= - 306237
: - 202876
self - 134257
[ - 113979
] - 113979

-------- CBGD STATS --------
#Try-catch pairs         12490
#ExceptNum=1             9517
#ExceptNum≥2             2973
#MaxTokens of Source     11977
#AverageTokens of Source 133.80
#MaxTokens of Target     1398
#AverageTokens of Target 50.76
#UniqueTokens            85912
-------- Top 10 Unique Tokens Ranking --------
<NEWLINE> - 195611
( - 163489
) - 163488
' - 129354
. - 117840
, - 92351
: - 92188
= - 83620
self - 32990
[ - 28923

       hasCatch                                              lines                                             labels
0             1  [def load_kline_df ( symbol_key ) : <NEWLINE> ...                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
1             1  [def browser_down_csv_zip ( open_browser = Fal...                                 [0, 0, 1, 1, 1, 1]
2             1  [@ AbuDeprecated ( 'only read old symbol db, m...         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
3             1  [def __call__ ( self , cls ) : <NEWLINE> , <IN...                     [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
4             1  [def __init__ ( self , symbol , json_dict ) : ...  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ...
...         ...                                                ...                                                ...
38911         0  [def test_fake_update_external_chrome_only ( s...                        [0, 0, 0, 0, 0, 0, 0, 0, 0]
38912         0  [def _walk_for_powershell ( directory ) : <NEW...                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
38913         0  [def test_send ( self , friend , file_path , i...  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ...
38914         0  [def __str__ ( self , prefix = '' , printElemN...                        [0, 0, 0, 0, 0, 0, 0, 0, 0]
38915         0  [def _stack_arrays ( tuples , dtype : np . dty...                           [0, 0, 0, 0, 0, 0, 0, 0]

[38916 rows x 3 columns]
                                                     try                                             except
0      [def load_kline_df ( symbol_key ) : <NEWLINE>,...  [<INDENT> except HDF5ExtError as e : <NEWLINE>...
1      [def kline_pd ( symbol , data_mode , n_folds =...  [<INDENT> except HDF5ExtError : <NEWLINE>, <IN...
2      [def __get__ ( self , obj , p_type = None ) : ...  [<INDENT> <INDENT> <INDENT> except AttributeEr...
3      [def load_pickle ( file_name ) : <NEWLINE>, <I...  [<INDENT> except EOFError : <NEWLINE>, <INDENT...
4      [def _parse_version ( version_string ) : <NEWL...  [<INDENT> <INDENT> except ValueError : <NEWLIN...
...                                                  ...                                                ...
13571  [def fetch_tweet_data ( tweet_id : str ) -> Op...  [<INDENT> <INDENT> <INDENT> raise <NEWLINE>, <...
13572  [def fetch_tweet_data ( tweet_id : str ) -> Op...  [<INDENT> <INDENT> <INDENT> t = e . args [ 0 ]...
13573  [def fetch_open_graph_image ( url : str ) -> O...  [<INDENT> except requests . RequestException :...
13574  [def sanitize_url ( url : str ) -> Optional [ ...  [<INDENT> except ValueError : <NEWLINE>, <INDE...
13575  [def topic_links ( linkifiers_key : int , topi...  [<INDENT> <INDENT> except re2 . error : <NEWLI...

[13576 rows x 2 columns]