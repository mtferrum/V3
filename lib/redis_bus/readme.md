Install redis server

    sudo apt-get install redis-server
    sudo systemctl enable redis-server.service
    sudo nano /etc/redis/redis.conf
    
Set params:

    maxmemory 256mb
    maxmemory-policy allkeys-lru
    
Restart

    sudo systemctl restart redis-server.service
    
Install requirements.txt

    pip install -r requirements.txt