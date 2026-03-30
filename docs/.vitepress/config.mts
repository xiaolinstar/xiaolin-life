// import { defineConfig } from 'vitepress'
import { withMermaid } from "vitepress-plugin-mermaid"
import markdownItTaskListPlus from "markdown-it-task-list-plus"
import llms from 'vitepress-plugin-llms'


// @ts-ignore 网站基础路径，区分GitHub部署和常规部署
const basePath = process.env.GITHUB_ACTIONS === 'true' ? '/xiaolin-life/' : '/'

// https://vitepress.dev/reference/site-config
// export default defineConfig({
export default withMermaid({
    base: basePath, // (*)设置域名前缀
    title: "乐享生活",
    description: "记录生活点滴，分享城市探索与生活感悟",
    vite: {
        plugins: [llms()],
    },
    head: [
    ['link', { rel: 'icon', href: '/sparrow.svg' }],
    ['style', {}, `
     @media (max-width: 768px) {
       .beian-container {
         display: block !important;
         text-align: center;
       }
       .beian-container> a,
       .beian-container > span {
         display: block;
         margin: 4px 0;
       }
       .gongan-beian {
         justify-content: center !important;
       }
     }
   `]
  ],
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        logo: '/sparrow.svg',
        nav: [
            { text: '首页', link: `/` },
            { text: '轻松办公', link: `/easy-office/` },
            { text: '南京生活', link: `/life-nanjing/` },
        ],

        sidebar: {
            '/easy-office/': [
                {
                    text: '轻松办公', link: `/easy-office/`,
                    items: [
                        { text: 'Thunderbird 邮件管理', link: `/easy-office/email-thunderbird` },
                        { text: 'Markdown 语法', link: `/easy-office/markdown` },
                        { text: 'Linux 学习', link: `/easy-office/linux-learn` },
                        { text: 'Mac 办公体验', link: `/easy-office/mac` }
                    ]
                }
            ],

            '/life-nanjing/': [
                {
                    text: '南京生活', link: `/life-nanjing/`,
                    items: [
                        {
                            text: '风景名胜',
                            link: `/life-nanjing/entertainment`,
                            items: [
                                { text: "鼓楼滨江", link: `/life-nanjing/entertainment/gulou-riverfront` }
                            ]
                        },
                        {
                            text: '南京高校',
                            link: `/life-nanjing/university`,
                            items: [
                                { text: '南京大学', link: `/life-nanjing/university/nju` },
                                { text: '南京师范大学', link: `/life-nanjing/university/nnu` }
                            ]
                        },
                        {
                            text: '桌游聚会',
                            link: `/life-nanjing/table-game`,
                            items: [
                                { text: '阿瓦隆', link: `/life-nanjing/table-game/avalon` },
                                { text: '掼蛋', link: `/life-nanjing/table-game/guandan` },
                                { text: '谁是卧底', link: `/life-nanjing/table-game/undercover` },
                                { text: '升级', link: `/life-nanjing/table-game/upgrade` }
                            ]
                        },
                        {
                            text: '生活思考',
                            link: `/life-nanjing/thinks`,
                            items: [
                                { text: '人人都是博主', link: `/life-nanjing/thinks/blogger` }
                            ]
                        }
                    ],
                }
            ]
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/xiaolinstar?tab=repositories' }
        ],
        // 页脚
        footer: {
            message: '微信公众号：AI持续运维，掘金：AI持续运维',
            copyright: 'Copyright © 2026 xingxiaolin <br/><span class="beian-container" style="display:inline-flex;align-items:center;gap:8px;"><a href="https://beian.miit.gov.cn/" target="_blank">苏ICP备2026011017号-1</a><span class="gongan-beian" style="display:inline-flex;align-items:center;white-space:nowrap;"><img src="/beian-gongan.png" alt="公安备案" style="width:16px;height:16px;margin-right:4px;"><a href="http://beian.mps.gov.cn/#query/webSearch?code=32010602012313"target="_blank">苏公网安备32010602012313号</a></span></span>'
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
