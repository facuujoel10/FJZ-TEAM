const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('public/index.html', 'utf8');
const re = /<script([^>]*)>([\s\S]*?)<\/script>/gi;
let match;
let index = 0;
const failures = [];

while ((match = re.exec(html))) {
  index += 1;
  const attrs = match[1] || '';
  const body = match[2] || '';
  if (!body.trim()) continue;
  if (/\bsrc\s*=/.test(attrs)) continue;
  if (/\btype\s*=\s*["']module["']/.test(attrs)) continue;
  const id = (attrs.match(/\bid\s*=\s*["']([^"']+)["']/) || [])[1] || ('inline-script-' + index);
  try {
    new vm.Script(body, { filename: id });
  } catch (err) {
    failures.push({
      id,
      name: err.name,
      message: err.message,
      line: err.stack ? err.stack.split('\n').slice(0, 4).join(' | ') : ''
    });
  }
}

console.log('TEAM FJZ V22 INLINE SCRIPT AUDIT');
console.log('inline scripts checked:', index);
if (failures.length) {
  console.log('SCRIPT_SYNTAX_FAILURES', JSON.stringify(failures));
  process.exit(1);
}
console.log('SCRIPT_SYNTAX_FAILURES []');
console.log('TEAM FJZ V22 INLINE SCRIPT AUDIT OK');
