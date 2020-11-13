run(){
    cd /home/ubuntu/api
    . /home/ubuntu/env/bin/activate
    python manage.py collectstatic --noinput > collectstatic.log.txt
}

# EXECUTE
run