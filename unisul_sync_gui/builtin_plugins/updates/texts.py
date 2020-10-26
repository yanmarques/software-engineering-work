from . import checker

import pkg_resources


unavailable_os = '''
Você está usando um sistema operational ainda não suportado nativamente.
Isso não é um problema, porém todas as atualizações deverão ser feitas manualmente.
'''

unavailable_linux_distribution = '''
Você está usando uma distribuição Linux ainda não suportada nativamente.
Isso não é um problema, porém todas as atualizações deverão ser feitas manualmente.
'''

already_updated = '''
A versão mais recente já foi instalada!
'''

windows_update_instructions = '''
Extraia o arquivo {} no seguinte diretório:
{}
'''.format(checker.WINDOWS_ASSET, pkg_resources.resource_dir)

deb_update_instructions = '''
Execute o seguinte comando no terminal, sendo root:

dpkg -i {} && apt install -f
'''.format(checker.DEBIAN_ASSET)

rpm_update_instructions = '''
Execute o seguinte comando no terminal, sendo root:

dnf install {}
'''.format(checker.RPM_ASSET)

keep_using_after_update_downloaded = '''
Sua atualização já está a caminho...

Deseja continuar usando o aplicativo?
'''