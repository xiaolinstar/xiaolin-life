const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { find, loadIndex } = require('../assets/js/search.js');
const Fuse = require('../themes/blowfish/assets/lib/fuse/fuse.min.cjs');

const data = [
  { title: '拿铁', breadcrumb: '奶茶仙人 / 瑞幸咖啡', sectionId: 'drinkzen', permalink: '/luckin/', content: '' },
  { title: '拿铁', breadcrumb: '奶茶仙人 / Manner 咖啡', sectionId: 'drinkzen', permalink: '/manner/', content: '' },
  { title: '咖啡随想', breadcrumb: '生活', sectionId: 'life', permalink: '/coffee/', content: '今天想起瑞幸拿铁' },
  { title: 'Thunderbird 解放收件箱', sectionId: 'office', permalink: '/email/', keywords: ['雷鸟邮箱', '邮件客户端'], content: '' },
  { title: '掼蛋', sectionId: 'life', permalink: '/guandan/', content: '' },
  { title: '升级', sectionId: 'life', permalink: '/upgrade/', content: '也可以试试掼蛋' },
];

test('品牌与品名可跨字段组合，所有关键词都必须匹配', () => {
  assert.deepEqual(find(data, '瑞幸 拿铁').map(x => x.permalink), ['/luckin/', '/coffee/']);
  assert.equal(find(data, '瑞幸 阿瓦隆').length, 0);
});
test('精确标题优先于正文提及，栏目筛选先于排序', () => {
  assert.equal(find(data, '掼蛋')[0].permalink, '/guandan/');
  assert.equal(find(data, '瑞幸 拿铁', 'office').length, 0);
});
test('别称、全角字符和空格均可匹配', () => {
  assert.equal(find(data, '雷鸟')[0].permalink, '/email/');
  assert.equal(find(data, 'ＭＡＮＮＥＲ　 拿铁')[0].permalink, '/manner/');
});
test('中文连写匹配栏目与标题，不被正文中偶然出现的完整短语阻断', () => {
  assert.equal(find(data, '瑞幸拿铁')[0].permalink, '/luckin/');
});
test('英文拼写容错只在没有直接结果时运行', () => {
  assert.equal(find(data, 'thunderbrd', '', Fuse)[0].permalink, '/email/');
  assert.equal(find(data, '毫不相关的内容', '', Fuse).length, 0);
});
test('索引请求并发复用，失败后能够重试', async () => {
  const original = global.fetch;
  let calls = 0;
  global.fetch = async () => { calls += 1; return { ok: false }; };
  try {
    await assert.rejects(loadIndex('/index.json'));
    global.fetch = async () => { calls += 1; return { ok: true, json: async () => data }; };
    const [a, b] = await Promise.all([loadIndex('/index.json'), loadIndex('/index.json')]);
    assert.equal(a, b);
    assert.equal(calls, 2);
  } finally { global.fetch = original; }
});

if (process.env.SEARCH_INDEX) {
  test('生产索引覆盖常见查询，排除目录、分类和草稿', () => {
    const index = JSON.parse(fs.readFileSync(process.env.SEARCH_INDEX, 'utf8'));
    for (const [query, url] of [
      ['雷鸟', '/office/email/'], ['南京 大学', '/life/university/nju/'],
      ['南师大', '/life/university/nnu/'], ['掼蛋', '/life/table-game/guandan/'],
    ]) assert.ok(find(index, query).some(item => item.permalink === url), query);
    assert.ok(find(index, '瑞幸 拿铁').length > 1);
    assert.ok(find(index, 'Manner 拿铁').length > 0);
    assert.ok(index.every(item => item.breadcrumb && item.sectionId));
    assert.ok(!index.some(item => /^\/(tags|categories|articles)\//.test(item.permalink)));
    const source = fs.readFileSync(require('node:path').join(__dirname, '../content/drinkzen/luckincoffee/ethiopia-latte/index.md'), 'utf8');
    if (/^draft:\s*true\s*$/m.test(source.split('---')[1])) {
      assert.ok(!index.some(item => item.permalink === '/drinkzen/luckincoffee/ethiopia-latte/'));
    }
  });
}
