#!/bin/bash
# 使用 Homebrew Ruby 环境启动 Jekyll 开发服务器

export PATH="/opt/homebrew/opt/ruby/bin:/opt/homebrew/lib/ruby/gems/3.4.0/bin:$PATH"
bundle exec jekyll serve --livereload
