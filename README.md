# oniloan

Sistema de gerenciamento de empréstimos

## Funcionalidades

* Usuários devem ser capazes de inserir empréstimos e seus respectivos pagamentos
* Usuários devem ser capazer de visualizar seus empréstimos e pagamentos
* Usuários devem ser capazes de visualizar o saldo devedor de cada um dos seus empréstimos
    * Você pode decidir onde e como mostrar a informação
    * O saldo devedor nada mais é do que o quanto o cliente ainda deve para o banco
    * O saldo devedor deve considerar a taxa de juros do empréstimo e descontar o que já foi pago
* Usuários não podem ver ou editar empréstimos ou pagamentos de outros usuários
* A autenticação da API deve ser feita via token
    * Não é necessário desenvolver endpoints para criação/gerenciamento de usuários
* Os empréstimos devem conter no mínimo as informações abaixo:

    ```
    Identificador - um identificador aleatório gerado automaticamente
    Valor nominal - o valor emprestado pelo banco
    Taxa de juros - a taxa de juros mensal do empréstimo
    Endereço de IP - endereço de IP que cadastrou o empréstimo
    Data de solicitação - a data em que o empréstimo foi solicitado
    Banco - informações do banco que emprestou o dinheiro (pode ser um simples campo de texto)
    Cliente - informações do cliente que pegou o empréstimo (pode ser um simples campo de texto)
    ```

* Os pagamentos devem conter no mínimo as informações abaixo:

    ```
    Identificador do empréstimo
    Data do pagamento
    Valor do pagamento
    ```

## Tecnologias

- Python 3.8
- Django
- Django Rest Framework
- PostgreSQL

## Executar

* Configuração

    * Criar um ambiente virtual python

        ```
        mkvirtualenv oniloan
        ```

    * Intalar dependências

        ```
        pip install -r requirements/dev.txt
        ```

    * Criar arquivo .env e popular variáveis de ambiente

        ```
        cp .env.example .env
        ```

    * Criar local_settings

        ```
        cp local_settings.example.py local_settings.py
        ```

    * Iniciar docker com banco de dados postgres

        ```
        docker-compose up -d
        ```

    * Executar migrations de criação das tabelas no banco

        ```
        ./manage.py showmigrations
        ./manage.py migrate
        ```

* Iniciar aplicação

    ```
    make runserver
    ```

* Testes Unitários

    ```
    make tests
    ```

* Documentação:
    * [Swagger](http://localhost:8000/api/docs/)
    * [Redoc](http://localhost:8000/api/redoc/)