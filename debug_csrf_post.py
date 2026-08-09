import re
from django.test import Client
client = Client()
response = client.get('/login/?next=/courses/canva-for-professionals/enroll/')
html = response.content.decode('utf-8')
form_html = html[html.find('<form method="post"'):html.find('</form>', html.find('<form method="post"'))+7]
print('form_html:\n', form_html)
print('csrf present', 'csrfmiddlewaretoken' in form_html)
print('cookies', list(response.cookies.items()))
token_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', form_html)
if token_match:
    token = token_match.group(1)
    print('token', token)
    post_data = {'email': 'test@example.com', 'password': 'wrong', 'csrfmiddlewaretoken': token, 'next': '/courses/canva-for-professionals/enroll/'}
    post_response = client.post('/login/?next=/courses/canva-for-professionals/enroll/', data=post_data)
    print('post status', post_response.status_code)
    print('post content contains invalid', 'Invalid email' in post_response.content.decode('utf-8'))
    print('post cookies', list(post_response.cookies.items()))
else:
    print('no token matched')
