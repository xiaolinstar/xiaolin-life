// import { defineConfig } from 'vitepress'
import {withMermaid} from "vitepress-plugin-mermaid"
import markdownItTaskListPlus from "markdown-it-task-list-plus"

// @ts-ignore 网站基础路径，区分GitHub部署和常规部署
const basePath = process.env.GITHUB_ACTIONS === 'true' ? '/xiaolin-docs/' : '/'

// https://vitepress.dev/reference/site-config
// export default defineConfig({
export default withMermaid({
    base: basePath, // (*)设置域名前缀
    title: "持续运维",
    description: "系统运维管理员日常工作经验交流与分享",
    head: [['link', {rel: 'icon', href: '/sparrow.svg'}]],
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        logo: '/sparrow.svg',
        nav: [
            {text: '首页', link: `/`},
            {text: '运维', link: `/sre/`},
            {text: '开发', link: `/software-development/`},
            {text: '人工智能', link: `/ai/`},
            {text: '轻松办公', link: `/easy-office/`},
            {text: '南京生活', link: `/life-nanjing/`},
        ],

        sidebar: {
            '/sre/': [
                {
                    text: '运维', link: `/sre/`,
                    items: [
                        {
                            text: '学习与思考',
                            link: `/sre/ops`,
                            items: [
                                {text: 'SRE 实践：服务可靠性案例', link: `/sre/ops/time-geek`},
                                {text: '阿里云 ACP 云原生微服务', link: `/sre/ops/acp-micro-service`},
                            ]
                        },
                        {
                            text: 'CI/CD 与 DevOps',
                            link: `/sre/devops`,
                            items: [
                                {text: 'Web 静态资源网站', link: `/sre/devops/front-dist`},
                                {text: '起步', link: `/sre/devops/start`},
                                {text: '容器化', link: `/sre/devops/containerize`},
                                {text: '声明式 API', link: `/sre/devops/docker-compose`},
                                {text: 'Pipeline 流水线', link: `/sre/devops/pipeline`},
                                {text: 'Github Actions 理论概念', link: `/sre/devops/github-actions`},
                                {text: 'Github Actions 工作流实践', link: `/sre/devops/github-actions-workflows`},
                            ]
                        },
                        {
                            text: 'Jenkins',
                            link: `/sre/jenkins`,
                            items: [
                                {text: '你好 Jenkins', link: `/sre/jenkins/hello-jenkins`},
                                {text: 'CI/CD 初体验', link: `/sre/jenkins/cicd-taste`},
                                {text: 'VitePress 快速搭建个人网站', link: `/sre/jenkins/vitepress-docs`},
                            ],
                        },
                        {
                            text: '可观测性',
                            link: `/sre/observability`,
                            items: [
                                {text: '什么是可观测性？', link: `/sre/observability/what-is-observability`},
                                {text: '日志', link: `/sre/observability/log`},
                                {text: '日志系统发展与演进', link: `/sre/observability/log-evolution`},
                                {text: 'Elastic ELK', link: `/sre/observability/ELK-stack`},
                                {text: 'Grafana Loki', link: `/sre/observability/grafana-loki`},
                                // { text: 'Prometheus', link: `/sre/observability/prometheus` },
                                // { text: 'Grafana', link: `/sre/observability/grafana` },
                                // { text: 'Kibana', link: `/sre/observability/kibana` },
                                // { text: 'ELK', link: `/sre/observability/elk` },
                                // { text: 'Jaeger', link: `/sre/observability/jaeger` },
                                // { text: 'Zipkin', link: `/sre/observability/zipkin` },
                                // { text: 'OpenTelemetry', link: `/sre/observability/opentelemetry` },
                            ]
                        }
                    ]
                }
            ],
            '/software-development/': [
                {
                    text: '开发', link: `/software-development/`,
                    items: [
                        {
                            text: '系统架构设计师',
                            link: `/software-development/system-architecture-designer`,
                            items: [
                                {
                                    text: '软考高级：系统架构设计师',
                                    link: `software-development/system-architecture-designer/ruankao-advanced`
                                }
                            ]
                        }
                    ]
                }
            ],

            '/ai/': [
                {
                    text: '人工智能', link: `/ai/`,
                    items: [
                        {text: 'LLM', link: `/ai/llm`},
                        {text: 'LangChain', link: `/ai/langchain`},
                    ]
                }
            ],

            '/easy-office/': [
                {
                    text: '轻松办公', link: `/easy-office/`,
                    items: [
                        {text: 'Thunderbird 解放收件箱', link: `/easy-office/email-thunderbird`},
                        {text: '易读易写 Markdown', link: `/easy-office/markdown`},
                    ]
                }
            ],

            '/life-nanjing/': [
                {
                    text: '南京生活', link: `/life-nanjing/`,
                    items: [
                        {
                            text: '南京高校',
                            link: `/life-nanjing/university`,
                            items: [
                                {text: '南京大学', link: `/life-nanjing/university/nju`},
                                {text: '南京师范大学', link: `/life-nanjing/university/nnu`}
                            ]
                        },
                        {
                            text: '桌游聚会',
                            link: `/life-nanjing/table-game`,
                            items: [
                                {text: '阿瓦隆', link: `/life-nanjing/table-game/avalon`}
                            ]
                        }
                    ],
                }
            ]
        },

        socialLinks: [
            {icon: 'github', link: 'https://github.com/xiaolinstar?tab=repositories'}
        ],
        // 页脚
        footer: {
            message: '微信公众号：持续运维，掘金：老实巴交的麻匪',
            copyright: 'Copyright © 2025  XingXiaolin'
        },
        // 支持模糊搜索
        search: {
            provider: 'local'
        }
    },
    // 支持mermaid
    mermaid: {},
    mermaidPlugin: {
        class: "mermaid my-class"
    },
    // pnpm install markdown-it-mathjax3
    // pnpm install markdown-it-task-lists
    markdown: {
        // 支持数学公式
        math: true,
        // 支持代码块行号
        lineNumbers: true,
        config: (md) => {
            md.use(markdownItTaskListPlus)
        }
    },

    // 上次更新
    lastUpdated: true,
    ignoreDeadLinks: 'localhostLinks'
})
