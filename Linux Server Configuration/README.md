# Linux Server Configuration


## My current values of LightSail instance
Public IP: 54.172.139.223

SSH Port: 2200

Complete URL: http://54.172.139.223/

### Steps of configuration

1. Create an Ubuntu machine on Amazon Lightsail (https://lightsail.aws.amazon.com) and download the private key (PK).

Change the access permission of the Public Key running the following:
```
$ chmod 400 LightsailDefaultPrivateKey.pem
``` 

2. Follow the instructions provided to SSH into your server.

Access the machine with ssh:

```
$ ssh ubuntu@54.172.139.223 -p 22 -i LightsailDefaultPrivateKey.pem
```

### Securing the System

3. Update all currently installed packages.

```
$ sudo apt-get update
$ sudo apt-get upgrade
```

4. Change the SSH port from 22 to 2200. Configure the Lightsail firewall to allow it.
Open the file /etc/ssh/sshd_config
```
$ sudo nano /etc/ssh/sshd_config
```
and change the following data:
```
Port 2200
PermitRootLogin no
PasswordAuthentication no
```
restart the ssh service
```
$ sudo service ssh restart
```

5. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123).
```
# close all incoming ports
$ sudo ufw default deny incoming
# open all outgoing ports
$ sudo ufw default allow outgoing
# open ssh port
$ sudo ufw allow 2200/tcp
# open http port
$ sudo ufw allow 80/tcp
# open ntp port
$ sudo ufw allow 123/udp
# turn on firewall
$ sudo ufw enable
```

Also on Lightsail, click on the tab Networking:
Add port Custom TCP 123
Add port Custom TCP 2200
Remove port SSH TCP 22

### Give grader access.

6. Create a new user account named grader.

```
$ sudo adduser grader
```

7. Give grader the permission to sudo.
Open the file
```
$ sudo nano /etc/sudoers.d/grader
```
And set the content
```
grader ALL=(ALL) NOPASSWD:ALL
```

8. Create an SSH key pair for grader using the ssh-keygen tool.
Generate on your machine the keys (private and public) (/home/ubuntu/.ssh/linuxCourse):
```
$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/ubuntu/.ssh/id_rsa): /home/ubuntu/.ssh/linuxCourse
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/ubuntu/.ssh/linuxCourse.
Your public key has been saved in /home/ubuntu/.ssh/linuxCourse.pub.
The key fingerprint is:
SHA256:TdiWWtB/05zJUtnhKBxcPfh7AovipAN7pi58TA9nXWs ubuntu@ip-172-26-3-146
The key's randomart image is:
+---[RSA 2048]----+
|        ......o.+|
|         +oo..o=.|
|        . *+ .+++|
|         *. +.o=o|
|       .S..o +...|
|    + o + E . ...|
| . o B + o     ..|
|  o + * .        |
|   +o+ .         |
+----[SHA256]-----+
```

Create the following directories:
```
$ su --login grader
$ sudo mkdir .ssh
$ sudo touch .ssh/authorized_keysd_keys
$ exit
$ cat .ssh/linuxCourse.pub (copy the ssh key)
$ su --login grader
$ sudo nano .ssh/authorized_keys (paste the key here)
$ sudo chmod 700 .ssh
$ sudo chmod 600 .ssh/authorized_keys
$ exit
```


### Prepare to deploy your project.

9. Configure the local timezone to UTC.
Configure the time zone:
```
$ sudo dpkg-reconfigure tzdata
```
Choose the option 'None of the Above' and then select UTC.

10. Install and configure Apache to serve a Python mod_wsgi application.
```
$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi
```

11. Install and configure PostgreSQL:
```
$ sudo apt-get install postgresql
````

* Do not allow remote connections
* Create a new database user named catalog that has limited permissions to your catalog application database.
```
$ sudo adduser catalog
$ sudo -u postgres -i
$ postgres:~$ createuser catalog
$ postgres:~$ createdb catalog
$ postgres:~$ psql
$ postgres=# ALTER DATABASE catalog OWNER TO catalog;
$ postgres=# ALTER USER catalog WITH PASSWORD 'catalog';
$ postgres=# \q
$ postgres:~$ exit
```

12. Install git.
```
$ sudo apt-get install git
```

### Deploy the Item Catalog project.

13. Clone and setup your Item Catalog project from the Github repository.
```
$ git clone https://github.com/rafaelpossenti/full-stack-web-developer.git (folder Item Catalog)
```

Open project.py and database_setup.py and replace the the create_engine for:
```
engine = create_engine('postgresql://catalog:catalog@localhost:5432/catalog')
```

14. Install the dependencies:
```
$ sudo apt-get -y install python-pip
$ sudo pip install SQLAlchemy
$ sudo pip install psycopg2
$ sudo pip install flask
$ sudo pip install oauth2client
$ sudo pip install requests
```

Modify the file /etc/apache2/sites-enabled/000-default.conf to add the following line (Right before the closing </VirtualHost>):
```
WSGIScriptAlias / /var/www/html/myapp.wsgi
```

Modify the file /var/www/html/myapp.wsgi to add the following content:
```
#!/usr/bin/python
import sys
import os
import logging
logging.basicConfig(stream=sys.stderr)
##Replace the standard out
sys.stdout = sys.stderr
sys.path.insert(0,"/home/ubuntu/item-catalog-vagrant-virtualbox-sqlite/")
os.chdir("/home/ubuntu/item-catalog-vagrant-virtualbox-sqlite/")
from project import app as application   
```

Restart the server:
```
$ sudo apache2ctl restart
```
item catalog was working on http://54.172.139.223/
