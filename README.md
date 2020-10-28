# Ferramenta para a Unisul Digital

Uma ferramenta feita por estudantes para estudantes, que busca automatizar as ações diárias realizadas no site da unisul digital, mais conhecido como EVA.

 
## Instalando

Aqui será abordado a instalação em modo de desenvolvimento.

### Windows
1. Instalar o python
Instale o python [aqui](https://www.python.org/downloads/windows/).
A versão recomendada é a `3.9` encontrada [aqui](https://www.python.org/downloads/release/python-390/).

**OBS:** No instalador, garanta de selecionar a opção para colocar o executável do python na variável de ambiente `PATH` para facilitar o seu manuseio

2. Baixe e extraia o projeto.

3. Instale a plataforma .NET para desenvolvimento desktop [aqui](https://visualstudio.microsoft.com/vs/features/net-development/#tab-55e56d1435216f4b164).

4. Instale algumas dependências para o Windows:
A lib `lxml` e `twisted`, dependências do projeto, requerem a realização do build durante a instalação, então a solução mais fácil é usar as versões já compiladas pela [comunidade](https://www.lfd.uci.edu/~gohlke/pythonlibs/). Seguem os links:
- lxml 4.5.2 [x86_64](https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/lxml-4.5.2-cp39-cp39-win_amd64.whl) [x86](https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/lxml-4.5.2-cp39-cp39-win32.whl)

- Twisted 20.3 [x86_64](https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/Twisted-20.3.0-cp39-cp39-win_amd64.whl) [x86](https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/Twisted-20.3.0-cp39-cp39-win32.whl)

Para instala-las, execute no prompt de comando para cada lib:
```powershell
> python -m pip install LIB.whl
```

5. Dentro do projeto, execute no prompt de comando:
```powershell
> python -m pip install .
```

### Linux
1. Instalar as dependências de desenvolvimento

#### Baseados no Debian
Como root, execute no terminal:
```bash
$ apt install python3 python3-pip python3-dev gcc
```

#### Fedora (e talvez Centos 8)
Como root, execute no terminal:
```bash
$ dnf install python3 python3-pip python3-devel gcc
```

#### Outros
Apenas os nomes das dependências devem alterar, sendo que é necessário uma pesquisa melhor.

2. Baixe e extraia o projeto.

3. Dentro do projeto, execute no terminal:
```bash
$ pip install . --user
```