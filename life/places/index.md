---
layout: page
title: 风景名胜
description: 南京著名景点和历史遗迹
---

# 风景名胜

南京拥有众多著名的风景名胜，是一座值得深度探索的城市。

## 景点列表

<ul>
{% for page in site.pages %}
  {% if page.url contains '/life/places/' and page.url != '/life/places/' %}
    <li><a href="{{ page.url | relative_url }}">{{ page.title }}</a></li>
  {% endif %}
{% endfor %}
</ul>
