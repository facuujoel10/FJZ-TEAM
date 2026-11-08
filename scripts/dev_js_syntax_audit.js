const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const html = fs.readFileSync('public/index.html', 'utf8');
const scriptRe = /<script([^>]*)>([\s\S]*?)<\/script>/gi;
const executableTypes = new Set([
  '',
  'text/javascript',
  'application/javascript',
  'application/ecmascript',
  'text/ecmascript',
  'module',
]);

function readAttr(attrs, name) {
  const re = new RegExp('\\b' + name + '\\s*=\\s*["\\\']([^"\\\']+)["\\\']', 'i');
  return (attrs.match(re) || [])[1] || '';
}

function safeName(value) {
  return String(value || 'script').replace(/[^a-z0-9_.-]+/gi, '_').slice(0, 90);
}

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'team-fjz-v22-js-audit-'));
const failures = [];
const skippedExternal = [];
const skippedNonExecutable = [];
let found = 0;
let classic = 0;
let modules = 0;
let match;

try {
  while ((match = scriptRe.exec(html))) {
    found += 1;
    const attrs = match[1] || '';
    const body = match[2] || '';
    const id = readAttr(attrs, 'id') || ('inline-script-' + found);
    const src = readAttr(attrs, 'src');
    const type = readAttr(attrs, 'type').trim().toLowerCase();
    const htmlStartLine = html.slice(0, match.index).split('\n').length;

    if (src) {
      skippedExternal.push({ id, src });
      continue;
    }
    if (!body.trim()) continue;
    if (!executableTypes.has(type)) {
      skippedNonExecutable.push({ id, type: type || '(none)' });
      continue;
    }

    const isModule = type === 'module';
    const file = path.join(
      tempDir,
      String(found).padStart(3, '0') + '-' + safeName(id) + (isModule ? '.mjs' : '.js')
    );
    fs.writeFileSync(file, body, 'utf8');

    const parsed = spawnSync(process.execPath, ['--check', file], {
      encoding: 'utf8',
      env: process.env,
    });
    if (isModule) modules += 1;
    else classic += 1;

    if (parsed.status !== 0) {
      const raw = String(parsed.stderr || parsed.stdout || '').trim();
      const firstLine = raw.split('\n')[0] || '';
      const lineMatch = firstLine.match(/:(\d+)(?::\d+)?$/);
      const localLine = lineMatch ? Number(lineMatch[1]) : 0;
      const sourceLines = body.split('\n');
      const context = localLine
        ? sourceLines.slice(Math.max(0, localLine - 5), Math.min(sourceLines.length, localLine + 4))
            .map((line, offset) => {
              const n = Math.max(1, localLine - 4) + offset;
              return String(n).padStart(4, ' ') + ' | ' + line;
            }).join(' || ')
        : '';
      failures.push({
        id,
        index: found,
        type: isModule ? 'module' : 'classic',
        htmlStartLine,
        error: raw.split('\n').slice(0, 10).join(' | '),
        context,
      });
    }
  }
} finally {
  fs.rmSync(tempDir, { recursive: true, force: true });
}

console.log('TEAM FJZ V22 GENERATED JAVASCRIPT AUDIT');
console.log('script tags found:', found);
console.log('classic scripts checked:', classic);
console.log('module scripts checked:', modules);
console.log('external src scripts skipped (not generated inline):', skippedExternal.length);
console.log('non-executable script blocks skipped:', skippedNonExecutable.length);

if (failures.length) {
  console.log('SCRIPT_SYNTAX_FAILURES', JSON.stringify(failures));
  process.exit(1);
}

console.log('SCRIPT_SYNTAX_FAILURES []');
console.log('TEAM FJZ V22 GENERATED JAVASCRIPT AUDIT OK');
