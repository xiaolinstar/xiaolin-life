---
layout: page
title: 生活感悟
description: 关于生活的思考
---

记录生活中的思考与成长。

## 文章列表

<ul>
{% for page in site.pages %}
  {% if page.url contains '/life/thinks/' and page.url != '/life/thinks/' %}
    <li><a href="{{ page.url | relative_url }}">{{ page.title }}</a></li>
  {% endif %}
{% endfor %}
</ul>
