Item Catalog
==================

##Dependencies

1. Python must be installed in the environment.
2. vagrant virtual machine

##Directory Structure 
  ```
 \
 |--static
 \
  |--bootstrap
  |--style.css
 |--templates
 \
  |--404.html
  |--category.html
  |--index.html
  |--item.html
  |--item_delete.html
  |--item_edit.html
  |--item_new.html
  |--layout.html
  |--list.html
  |--list_delete.html
  |--login.html
 |--client_secrets_fb.json
 |--client_secrets_gplus.json
 |--database_populate.py
 |--heroes.db
 |--models.py
 |--models.pyc
 |--views.py
  ```
  
##Execution
 ```
vagrant up
vagrant ssh
cd /vagrant/item catalog
python models.py
python database_populate.py
python views.py
 ```

This command will execute a  item catalog in your browser at: http://localhost:8000
  
