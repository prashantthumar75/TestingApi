run(){
    cd /home/ubuntu/api
    . /home/ubuntu/env/bin/activate
    pip install -r requirements.txt > install_requirements.log.txt
}

# EXECUTE
run