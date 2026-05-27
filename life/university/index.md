---
layout: page
title: 高校巡礼
description: 南京知名高校介绍
---

# 高校巡礼

南京是中国高等教育的重要基地，拥有众多知名高校。

## 高校列表

<ul>
{% for page in site.pages %}
  {% if page.url contains '/life/university/' and page.url != '/life/university/' %}
    <li><a href="{{ page.url | relative_url }}">{{ page.title }}</a></li>
  {% endif %}
{% endfor %}
</ul>
