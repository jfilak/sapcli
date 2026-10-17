LINK_ABAP_CODE = '''DATA lt_return TYPE bapiret2_t.
DATA lv_abap_package TYPE devclass.
lv_abap_package = `$PKG`.
DATA lv_git_repo_url TYPE string.
lv_git_repo_url = `https://github.com/jfilak/sapcli.git`.
DATA lv_git_user TYPE string.
lv_git_user = `user`.
DATA lv_git_password TYPE string.
lv_git_password = `pass``word`.
DATA lv_branch TYPE string.
lv_branch = `refs/heads/main`.
DATA lv_folder_logic TYPE string.
lv_folder_logic = `FULL`.
DATA lv_ignore_subpackages TYPE xfeld.
lv_ignore_subpackages = `X`.
DATA lv_main_lang_only TYPE xfeld.
lv_main_lang_only = ``.
DATA lv_starting_folder TYPE string.
lv_starting_folder = `/abap/`.
CALL FUNCTION 'ZABAPGIT_API_RFC_LINK'
  EXPORTING
    abap_package = lv_abap_package
    git_repo_url = lv_git_repo_url
    git_user = lv_git_user
    git_password = lv_git_password
    branch = lv_branch
    folder_logic = lv_folder_logic
    ignore_subpackages = lv_ignore_subpackages
    main_lang_only = lv_main_lang_only
    starting_folder = lv_starting_folder
  TABLES
    return = lt_return.
LOOP AT lt_return INTO DATA(ls_return).
  out->write( |SAPCLI-BAPIRET\\|{ ls_return-type }\\|{ ls_return-id }\\|{ ls_return-number }\\|{ ls_return-message }| ).
ENDLOOP.
out->write( `SAPCLI-END` ).'''

LINK_OUTPUT_OK = '''SAPCLI-BAPIRET|I|||Running migrations
SAPCLI-BAPIRET|I|||Linking https://github.com/jfilak/sapcli.git with $PKG
SAPCLI-BAPIRET|I|||Done
SAPCLI-END
'''

LINK_OUTPUT_ERROR = '''SAPCLI-BAPIRET|I|||Running migrations
SAPCLI-BAPIRET|E|||Repository already exists | in package $PKG
SAPCLI-END
'''

LINK_OUTPUT_NOISE = '''Some unrelated line
SAPCLI-BAPIRET|W|ZMSG|042|Careful
Another unrelated line
SAPCLI-END
'''

LINK_OUTPUT_TRUNCATED = '''SAPCLI-BAPIRET|I|||Running migrations
'''
