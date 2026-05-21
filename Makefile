.PHONY: dev build build-github build-self clean help

RUBY_PATH := /opt/homebrew/opt/ruby/bin
GEM_PATH := /opt/homebrew/lib/ruby/gems/3.4.0/bin
PATH := $(RUBY_PATH):$(GEM_PATH):$(PATH)

dev:
	@echo "🚀 启动开发服务器..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle exec jekyll serve --livereload

build:
	@echo "📦 构建站点 (本地)..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle exec jekyll build

build-github:
	@echo "📦 构建站点 (GitHub Pages)..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle exec jekyll build --config _config.yml,_config.github-pages.yml

build-self:
	@echo "📦 构建站点 (自托管)..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle exec jekyll build --config _config.yml,_config.self-hosted.yml

clean:
	@echo "🧹 清理构建文件..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle exec jekyll clean

install:
	@echo "📥 安装依赖..."
	@PATH="$(RUBY_PATH):$(GEM_PATH):$(PATH)" bundle install

help:
	@echo "可用命令:"
	@echo "  make dev          - 启动开发服务器 (带热重载)"
	@echo "  make build        - 构建站点 (本地配置)"
	@echo "  make build-github - 构建站点 (GitHub Pages 配置)"
	@echo "  make build-self   - 构建站点 (自托管配置)"
	@echo "  make clean        - 清理构建文件"
	@echo "  make install      - 安装依赖"
