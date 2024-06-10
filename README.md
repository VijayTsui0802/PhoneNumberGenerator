
启动Django：
python manage.py runserver

进入虚拟环境：
conda activate PhoneNumberGenerator

进入项目目录：
cd /Users/vijaytsui/开发/GitHub/手机号生成器/Django后端

启动celery：
celery -A PhoneNumberGenerator worker --loglevel=info