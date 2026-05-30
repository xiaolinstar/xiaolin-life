---
layout: page
title: 美食探店
description: 南京美食推荐
---

探索南京的美食文化。

## 美食列表

<ul>
{% for page in site.pages %}
  {% if page.url contains '/life/entertainment/' and page.url != '/life/entertainment/' %}
    <li><a href="{{ page.url | relative_url }}">{{ page.title }}</a></li>
  {% endif %}
{% endfor %}
</ul>
