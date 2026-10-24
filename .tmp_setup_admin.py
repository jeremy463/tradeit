import os, time
from apex.web.main import web_init, create_admin
import apex.web.security as sec

config = os.path.join(os.getcwd(), 'web.json')
print('config=', config)
print('web_init_rc=', web_init(config, 'localhost', 'APEX Trader', 'atobateleheritage@gmail.com', 'Nigeria', 'oanda', '', '', 'EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,USDCHF,NZDUSD', 15000, 45000, 'NGN', True))
secret = sec.new_totp_secret()
orig = sec.new_totp_secret
sec.new_totp_secret = lambda: secret
code = sec.totp_code(secret, int(time.time() // 30))
print('admin_email=atobateleheritage@gmail.com')
print('admin_password=Princrmy @24')
print('admin_totp_code=' + code)
print('create_admin_rc=', create_admin(config, 'atobateleheritage@gmail.com', password='Princrmy @24', confirm_code=code))
sec.new_totp_secret = orig
