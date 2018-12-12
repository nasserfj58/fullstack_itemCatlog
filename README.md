
# NasserZon

This project is part of Udacity Full-stack nanodgree.

---

This repo contaian 2 python files and html taemblets folder.


I used Bootstrap, jquery, Google authentaction, bycrypt libarary for hashing,smtplib and MIMEText to create and send emails(for resetpassword) and validate_email libarary for validating emails :) , I did uae session mangment and reset password to make my app more relastic (I got carried out lol).


#### To use google login you need to create app on google api devloper console to get app clientid.

#### You Don't need to do the step above becuses NasserZon has registration and login :).


This project has 2 json api endpoints:

1. All products based on category uri like localhost:8000/api/get/products/smartphone or /api/get/products/ to get all products
2. One product based on product name like localhost:8000/api/get/products/oneplus6

To try this code You need to:

0. Install Vagrant and VirtualBox
1. Clone the fullstack-nanodegree-vm 
2. Run vagrant up
3. Run vagrant ssh to login to your VM.
4. cd/ vagrant to acsees the shared files.
5. move The downladed files to vagrant shared files
6. Run python storedb_setup.py to create the db with required tables and python fillDbdata.py to fill dummy data.
7. download external libariries (bcrypt and validate_email) by runing these commands ('pip install validate_email' and 'pip install bcrypt' ) if you get an error from your VM saying that you dont have acsses run the same commands with '--user' in the end of the command(I run to this problem and adding --user in the end fixed it).
8. run python myproject.py and start to play(you need to create an acount to add delete and edit)
9. type localhost:8000 on your browser to see the webapp.


You can find the link to the fullstack-nanodegree-vm from  https://github.com/udacity/fullstack-nanodegree-vm.


---
 
References:
- https://pypi.org/project/validate_email/
- https://pypi.org/project/bcrypt/
- https://docs.python.org/3/library/smtplib.html?highlight=smtp_ssl
- https://docs.python.org/3/library/email.mime.html
- https://www.programcreek.com/python/example/79006/flask.session.clear
- https://stackoverflow.com/questions/42988977/what-is-the-purpose-pip-install-user
