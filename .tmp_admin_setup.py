import os, time
from apex.web.main import create_admin
import apex.web.security as sec

config = os.path.join(os.getcwd(), 'web.json')
print('config=', config)
secret = sec.new_totp_secret()
orig = sec.new_totp_secret
sec.new_totp_secret = lambda: secret
code = sec.totp_code(secret, int(time.time() // 30))
print('admin_email=atobateleheritage@gmail.com')
print('admin_password=Princemy@24')
print('admin_totp_code=' + code)
rc = create_admin(config, 'atobateleheritage@gmail.com', password='Princemy@24', confirm_code=code)
sec.new_totp_secret = orig
print('create_admin_rc=', rc)
