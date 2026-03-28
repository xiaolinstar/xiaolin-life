const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '../docs');
const distDir = path.join(__dirname, '../docs/.vitepress/dist');

function getHtmlFiles(dir, baseDir = '') {
  const files = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;
    if (entry.name === 'node_modules') continue;
    if (entry.name === '.vitepress') continue;
    
    const fullPath = path.join(dir, entry.name);
    const relativePath = path.join(baseDir, entry.name);
    
    if (entry.isDirectory()) {
      files.push(...getHtmlFiles(fullPath, relativePath));
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      let htmlPath = relativePath.replace(/\.md$/, '.html');
      
      if (entry.name === 'README.md') {
        htmlPath = path.join(path.dirname(htmlPath), 'index.md');
      } else {
        htmlPath = htmlPath.replace(/\.html$/, '.md');
      }
      
      files.push({
        mdPath: fullPath,
        htmlPath: htmlPath
      });
    }
  }
  return files;
}

function copyMdToDist() {
  if (!fs.existsSync(distDir)) {
    console.error('Dist directory not found. Run build first.');
    process.exit(1);
  }

  const mdFiles = getHtmlFiles(srcDir);
  let copied = 0;

  for (const file of mdFiles) {
    const targetPath = path.join(distDir, file.htmlPath);
    const targetDir = path.dirname(targetPath);
    
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
    
    let content = fs.readFileSync(file.mdPath, 'utf8');
    
    content = content.replace(/^---[\s\S]*?---\n\n?/gm, '');
    
    fs.writeFileSync(targetPath, content, 'utf8');
    copied++;
  }

  console.log(`Copied ${copied} markdown source files to dist/`);
}

copyMdToDist();
