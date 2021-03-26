clean:
	./manage.py clean_pyc
	./manage.py clear_cache

runserver:
	./manage.py runserver

shell:
	./manage.py shell_plus

urls:
	./manage.py show_urls

migrate:
	./manage.py migrate

migrations:
	./manage.py makemigrations

showmigrations:
	./manage.py showmigrations

compilemessages:
	./manage.py compilemessages

test:
	./manage.py test
