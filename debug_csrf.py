from django.test import Client
client = Client()
response = client.get('/login/?next=/courses/canva-for-professionals/enroll/')
print('status', response.status_code)
print('cookies', list(response.cookies.items()))
html = response.content.decode('utf-8')
start = html.find('<form')
end = html.find('</form>', start) + 7
print('form html:\n', html[start:end])
print('csrf field present', 'csrfmiddlewaretoken' in html[start:end])
print('action attr', html[start:end].split('action=')[1].split()[0] if 'action=' in html[start:end] else 'none')
print('method post', 'method="post"' in html[start:end].lower() or "method='post'" in html[start:end].lower())
