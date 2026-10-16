const fs = require('fs');

function updateQuote() {
  try {
    const quotes = require('./quotes.json');
    const { quote, author } = quotes[Math.floor(Math.random() * quotes.length)];

    const cardDesign = `
<!--STARTS_HERE_QUOTE_CARD-->
<p align="center">
    <img src="https://readme-daily-quotes.vercel.app/api?author=${encodeURIComponent(author)}&quote=${encodeURIComponent(quote)}&theme=dark&bg_color=3F3533&author_color=E9B49C&accent_color=F6D3C6">
</p>
<!--ENDS_HERE_QUOTE_CARD-->
`;

    const readmePath = './README.md';
    const readme = fs.readFileSync(readmePath, 'utf-8');
    fs.writeFileSync(readmePath, readme.replace(/<!--STARTS_HERE_QUOTE_CARD-->(.|\n)*<!--ENDS_HERE_QUOTE_CARD-->/, cardDesign.trim()));
  } catch (error) {
    console.error('Error updating quote:', error);
    process.exit(1);
  }
}

updateQuote();
