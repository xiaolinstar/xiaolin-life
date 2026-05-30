---
layout: page
title: 桌游时光
description: 桌游聚会记录
---

享受桌游带来的欢乐时光。

## 桌游列表

<ul>
{% for page in site.pages %}
  {% if page.url contains '/life/table-game/' and page.url != '/life/table-game/' %}
    <li><a href="{{ page.url | relative_url }}">{{ page.title }}</a></li>
  {% endif %}
{% endfor %}
</ul>
