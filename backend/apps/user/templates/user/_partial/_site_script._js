var user = {"id_exist_url":"{% url 'user.id_exist' %}", autocomplete_check_url: "{% url 'user.autocomplete_check' %}" };
var csrf_token =  '{{ csrf_token }}';
var autocomplete_check = {% if config.autocomplete_check %} true{% else %} false{% endif %};