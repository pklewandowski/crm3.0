# TEMPLATE RENDERING

## Render with Django template engin

```python
from django.template import Template
from django.template import Context

tmpl = Template('<div>{{some_value}}</div>')
tmpl_str = tmpl.render(Context({'some_value': 'Alamakota'}))
```