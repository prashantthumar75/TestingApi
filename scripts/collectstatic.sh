run(){
    cd /home/ubuntu/api
    . /home/ubuntu/env/bin/activate
    rm -rf static
    rm -rf staticfiles
    python manage.py collectstatic --noinput > collectstatic.log.txt
    mv staticfiles static
}

# EXECUTE
run