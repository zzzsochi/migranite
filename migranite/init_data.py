from string import Template

SETTINGS = Template("""\
[migrations]
path = "$migranite_path"
; digits = 3

[templates]
path = "$templates_path"
default = "default.py"

[database]
backend = "json"
path = ".migranite_db.json"

; [database]
; backend = "mongo"
; host = "localhost"
; port = 27017
; name =
; collection = "migrations"
""")

TEMPLATE_DEFAULT = '''\
""" <EMPTY DESCRIPTION>

<EMPTY LONG DESCRIPTION>
"""


def run():
    pass
'''
