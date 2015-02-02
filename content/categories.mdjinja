---
title-prefix: Stuff Andrew Likes
title: Categories
---
# Categories: #
{% for category, posts in posts|invert_by('categories') %}

## {{category}} ##
<ul class="posts">
{% for post in posts|sort(attribute='date', reverse=True) %}
{% if not post.draft %}
<li><span>{{post.date}}</span> &raquo; <a href="{{post.link}}">{{post.title}}</a></li>
{% endif %}
{% endfor %}
</ul>
{% endfor %}
