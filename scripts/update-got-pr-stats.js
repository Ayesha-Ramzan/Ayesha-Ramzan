const fs = require('node:fs/promises');

const owner = process.env.GOT_REPO_OWNER || 'gobind-trades';
const repo = process.env.GOT_REPO_NAME || 'Gobind-trades-Admin-dashboard-';
const token = process.env.GOT_REPO_TOKEN || process.env.GITHUB_TOKEN;

if (!token) {
  throw new Error('GOT_REPO_TOKEN is required to read the GOT repository.');
}

async function getClosedPulls(page) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page=${page}`,
    {
      headers: {
        Accept: 'application/vnd.github+json',
        Authorization: `Bearer ${token}`,
        'X-GitHub-Api-Version': '2022-11-28',
      },
    },
  );

  if (!response.ok) {
    throw new Error(`GitHub API failed (${response.status}): ${await response.text()}`);
  }

  return response.json();
}

const mergedPulls = [];
for (let page = 1; ; page += 1) {
  const pulls = await getClosedPulls(page);
  mergedPulls.push(
    ...pulls.filter(
      (pull) => pull.merged_at && pull.user?.login?.toLowerCase() === 'ayesha-ramzan',
    ),
  );
  if (pulls.length < 100) break;
}

mergedPulls.sort((a, b) => new Date(b.merged_at) - new Date(a.merged_at));
const latest = mergedPulls.slice(0, 4);
const escapeXml = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&apos;');

const truncate = (value, length) => value.length > length ? `${value.slice(0, length - 1)}…` : value;
const rows = latest.length
  ? latest.map((pull, index) => {
      const y = 139 + index * 19;
      const title = escapeXml(truncate(`#${pull.number} ${pull.title}`, 68));
      return `<a href="${escapeXml(pull.html_url)}"><text x="34" y="${y}" fill="#f7e8df" font-family="Arial, sans-serif" font-size="12">${title}</text></a>`;
    }).join('')
  : '<text x="34" y="139" fill="#f7e8df" font-family="Arial, sans-serif" font-size="12">No merged PRs found yet</text>';

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="220" viewBox="0 0 640 220" role="img" aria-labelledby="title desc">
  <title id="title">GOT project merged pull requests</title>
  <desc id="desc">${mergedPulls.length} pull requests merged by Ayesha-Ramzan in ${owner}/${repo}</desc>
  <defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#2e2522"/><stop offset="1" stop-color="#5c4a43"/></linearGradient></defs>
  <rect width="640" height="220" rx="16" fill="url(#bg)"/>
  <text x="34" y="38" fill="#f6d3c6" font-family="Arial, sans-serif" font-size="18" font-weight="700">GOT PROJECT · MERGED PRs</text>
  <text x="34" y="82" fill="#ffffff" font-family="Arial, sans-serif" font-size="42" font-weight="700">${mergedPulls.length}</text>
  <text x="96" y="80" fill="#f7e8df" font-family="Arial, sans-serif" font-size="14">merged pull requests</text>
  <text x="34" y="108" fill="#d9c6bc" font-family="Arial, sans-serif" font-size="12">${escapeXml(owner)}/${escapeXml(repo)}</text>
  <line x1="34" y1="120" x2="606" y2="120" stroke="#e9b49c" stroke-opacity=".45"/>
  ${rows}
</svg>
`;

await fs.writeFile('got-pr-stats.svg', svg);
console.log(`Generated GOT PR stats: ${mergedPulls.length} merged PRs`);
