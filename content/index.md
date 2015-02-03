---
title: Stuff Andrew Likes
---
#Posts#
<ul class="posts">
{% for post in posts|sort(attribute='date', reverse=True)|limit(20) %}
<li><span>{{post.date}}</span> &raquo; <a href="{{post.link}}">{{post.title}}</a></li>
{% endfor %}
</ul>
