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

PULL_ABAP_CODE = '''DATA lt_return TYPE bapiret2_t.
DATA lv_abap_package TYPE devclass.
lv_abap_package = `$PKG`.
DATA lv_git_user TYPE string.
lv_git_user = `user`.
DATA lv_git_password TYPE string.
lv_git_password = `pass``word`.
DATA lv_corrnr TYPE trkorr.
lv_corrnr = `C50K000001`.
CALL FUNCTION 'ZABAPGIT_API_RFC_PULL'
  EXPORTING
    abap_package = lv_abap_package
    git_user = lv_git_user
    git_password = lv_git_password
    corrnr = lv_corrnr
  TABLES
    return = lt_return.
LOOP AT lt_return INTO DATA(ls_return).
  out->write( |SAPCLI-BAPIRET\\|{ ls_return-type }\\|{ ls_return-id }\\|{ ls_return-number }\\|{ ls_return-message }| ).
ENDLOOP.
out->write( `SAPCLI-END` ).'''

PULL_OUTPUT_OK = '''SAPCLI-BAPIRET|I|||Run migration
SAPCLI-BAPIRET|I|||Deserializing
SAPCLI-BAPIRET|I|||Finished
SAPCLI-END
'''

PULL_OUTPUT_ERROR = '''SAPCLI-BAPIRET|I|||Run migration
SAPCLI-BAPIRET|E|||Unable to find repo for package $PKG!
SAPCLI-END
'''

LIST_ABAP_CODE = '''DATA lt_return TYPE bapiret2_t.
DATA lt_repositories TYPE zabapgit_api_rfc_repo_t.
CALL FUNCTION 'ZABAPGIT_API_RFC_LIST'
  TABLES
    repositories = lt_repositories
    return = lt_return.
LOOP AT lt_repositories INTO DATA(ls_repositories).
  out->write( `SAPCLI-ROW|REPOSITORIES` ).
  out->write( |SAPCLI-FIELD\\|REPO_KEY\\|{ ls_repositories-repo_key }| ).
  out->write( |SAPCLI-FIELD\\|NAME\\|{ ls_repositories-name }| ).
  out->write( |SAPCLI-FIELD\\|ABAP_PACKAGE\\|{ ls_repositories-abap_package }| ).
  out->write( |SAPCLI-FIELD\\|URL\\|{ ls_repositories-url }| ).
  out->write( |SAPCLI-FIELD\\|BRANCH_NAME\\|{ ls_repositories-branch_name }| ).
  out->write( |SAPCLI-FIELD\\|DESERIALIZED_AT\\|{ ls_repositories-deserialized_at }| ).
ENDLOOP.
LOOP AT lt_return INTO DATA(ls_return).
  out->write( |SAPCLI-BAPIRET\\|{ ls_return-type }\\|{ ls_return-id }\\|{ ls_return-number }\\|{ ls_return-message }| ).
ENDLOOP.
out->write( `SAPCLI-END` ).'''

LIST_OUTPUT_OK = '''SAPCLI-ROW|REPOSITORIES
SAPCLI-FIELD|REPO_KEY|000000000007
SAPCLI-FIELD|NAME|CLAS | test
SAPCLI-FIELD|ABAP_PACKAGE|$SAPCLI_AGRFC
SAPCLI-FIELD|URL|https://github.com/abapGit-tests/CLAS.git
SAPCLI-FIELD|BRANCH_NAME|refs/heads/main
SAPCLI-FIELD|DESERIALIZED_AT|20261017200708.0661700

SAPCLI-ROW|REPOSITORIES
SAPCLI-FIELD|REPO_KEY|000000000008
SAPCLI-FIELD|NAME|sapcli
SAPCLI-FIELD|ABAP_PACKAGE|$SAPCLI
SAPCLI-FIELD|URL|https://github.com/jfilak/sapcli.git
SAPCLI-FIELD|BRANCH_NAME|refs/heads/master
SAPCLI-FIELD|DESERIALIZED_AT|0.0000000

SAPCLI-BAPIRET|I|||Running migrations
SAPCLI-BAPIRET|I|||Found 2 repositories
SAPCLI-END
'''

LIST_OUTPUT_ERROR = '''SAPCLI-BAPIRET|I|||Running migrations
SAPCLI-BAPIRET|E|||Migration failed
SAPCLI-END
'''

COMMIT_ABAP_CODE = '''DATA lt_return TYPE bapiret2_t.
DATA lv_abap_package TYPE devclass.
lv_abap_package = `$PKG`.
DATA lv_git_user TYPE string.
lv_git_user = `user`.
DATA lv_git_password TYPE string.
lv_git_password = `pass``word`.
DATA lv_comment TYPE string.
lv_comment = `Fix bug`.
DATA lv_body TYPE string.
lv_body = `First line`
  && cl_abap_char_utilities=>newline
  && `Second line`.
DATA lv_all TYPE xfeld.
lv_all = `X`.
DATA lv_committer_name TYPE string.
lv_committer_name = `Committer`.
DATA lv_committer_email TYPE string.
lv_committer_email = `committer@example.com`.
DATA lv_author_name TYPE string.
lv_author_name = `Author`.
DATA lv_author_email TYPE string.
lv_author_email = `author@example.com`.
CALL FUNCTION 'ZABAPGIT_API_RFC_COMMITPUSH'
  EXPORTING
    abap_package = lv_abap_package
    git_user = lv_git_user
    git_password = lv_git_password
    comment = lv_comment
    body = lv_body
    all = lv_all
    committer_name = lv_committer_name
    committer_email = lv_committer_email
    author_name = lv_author_name
    author_email = lv_author_email
  TABLES
    return = lt_return.
LOOP AT lt_return INTO DATA(ls_return).
  out->write( |SAPCLI-BAPIRET\\|{ ls_return-type }\\|{ ls_return-id }\\|{ ls_return-number }\\|{ ls_return-message }| ).
ENDLOOP.
out->write( `SAPCLI-END` ).'''

COMMIT_OUTPUT_OK = '''SAPCLI-BAPIRET|I|||Running migrations
SAPCLI-BAPIRET|I|||Pushing as Committer <committer@example.com>
SAPCLI-BAPIRET|S|||Committed: CLAS ZCL_AG_UNIT_TEST
SAPCLI-BAPIRET|I|||Pushed 1 objects
SAPCLI-BAPIRET|I|||Done
SAPCLI-END
'''

COMMIT_OUTPUT_ERROR = '''SAPCLI-BAPIRET|E|||Cannot push offline repo of the package $PKG
SAPCLI-END
'''
