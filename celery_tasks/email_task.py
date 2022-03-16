from celery import Celery
from MyHouse import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyHouse.settings')
django.setup()

app = Celery("celery_tasks.email", broker="redis://:guoht990520_2_redis@127.0.0.1:6379/1")


email_title = '来自 《 MyHouse·智能家居 》 的验证信息'


@app.task
def send_mail_register(email, verify_code):
    from django.core.mail import send_mail
    global email_title

    email_body_reg = f'''Email 地址验证

        尊敬的用户：

            这封信是由 《MyHouse智能家居》 发送的。

            您收到这封邮件，是由于在 《MyHouse智能家居》 进行了·新用户注册·，使用了这个邮箱地址。如果您并没有访问过 《MyHouse智能家居》，或没有进行上述操作，请忽略这封邮件。您不需要退订或进行其他进一步的操作。

            注册验证码：  {verify_code}

            请谨慎操作。

            最后，祝您学业有成、工作顺利。

            '''
    email_body = email_body_reg
    
    send_status = send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])



@app.task
def send_mail_change_pwd(email, verify_code):
    from django.core.mail import send_mail
    global email_title
    
    
    email_body_change = f'''Email 地址验证

        尊敬的用户：

            这封信是由 《MyHouse智能家居》 发送的。

            您收到这封邮件，是由于在 《MyHouse智能家居》 进行了·密码找回·，使用了这个邮箱地址。如果您并没有访问过 《MyHouse智能家居》，或没有进行上述操作，请忽略这封邮件。您不需要退订或进行其他进一步的操作。

            修改密码验证码：  {verify_code}

            请谨慎操作。

            最后，祝您学业有成、工作顺利。

            '''
    
    email_body = email_body_change
    
    send_status = send_mail(email_title, email_body, settings.EMAIL_HOST_USER, [email])
