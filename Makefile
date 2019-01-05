prod:
	python manage.py migrate
	python manage.py collectstatic --noinput

dev:
	npm run-script start

sync-upstream:
	@git fetch upstream
	@git rebase upstream/master

stop-celery-backend:
	echo 'Stoping Redis'
	@docker run -p6379:6379 --name redis -d redis

start-celery-backend:
	echo 'Starting Redis'
	@docker run -p6379:6379 --name redis -d redis

start-scheduler:
	echo 'Invoking Celery beat'
	CELERY_TASK_FREQUENCY=0.5 celery -A kamu beat -l debug

start-worker:
	echo 'Invoking Celery Worker'
	celery -A kamu worker -l info
