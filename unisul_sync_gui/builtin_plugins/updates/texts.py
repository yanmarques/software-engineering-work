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
Extraia o arquivo {} no diretório em que o aplicativo está instalado.
'''

deb_update_instructions = '''
Execute o seguinte comando no terminal, sendo root:

dpkg -i {} && apt install -f
'''

rpm_update_instructions = '''
Execute o seguinte comando no terminal, sendo root:

dnf install {}
'''

keep_using_after_update_downloaded = '''
Seu download está a caminho...

Deseja continuar usando o aplicativo?
'''

windows_not_bundled_on_update = '''
Parece que você não está usando o programa vindo com o bundle, talvez você esteja apenas desenvolvendo o programa no Windows.

Sem problemas, porém não posso fazer a atualização comum para a plataforma Windows. Você deseja baixar a atualização de qualquer forma?
'''

windows_autoupdate_finished = '''
Voilá!

Para concluir a atualização, o aplicativo será reiniciado de forma automática.
Ao abri-lo novamente, você deve presenciar a nova versão instalada.

Aproveite!
'''

confirm_using_unstable_updates = '''
Ao habilitar atualizações de versões não estáveis, você será contemplado com as últimas atualizações desenvolvidas.

Porém isso terá o custo de que estas versões ainda não foram testadas devidamente e por isso podem ser consideradas instáveis.

Deseja continuar?
'''