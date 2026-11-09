# FLUXS website

FLUXS = Fluid Experiments at Sapienza (formerly FLEXLab): experimental fluid dynamics group (PI: Giovanni Paolo Romano). Jekyll site published by GitHub Pages
from `main` of `FLUXS-Lab/FLUXS-Lab.github.io` at https://fluxs-lab.github.io (root URL, `baseurl: ""`).
Only plugins in the `github-pages` gem whitelist may be used; `theme: null` must stay, otherwise
Pages injects the Primer theme. English only.

- Content lives in `_data/*.yml` (research, techniques, facilities, members, teaching, phd, publications);
  pages are thin Liquid templates over that data. Empty member groups are hidden automatically.
- Internal links go through `| relative_url`.
- Logos in `assets/img/logo/`: SVG originals `fluxs-symbol.svg`, `fluxs-logo-compact.svg`,
  `fluxs-logo-horizontal.svg` (do not edit); header SVG, favicons and `fluxs-og.png` are derived from them with
  `python3 tools/make_logos.py`, which also refreshes the `LOGOS/` kit (SVG + PNG, not published on the site). Logo colors: navy `#1B2A4A` (`--blue`),
  maroon `#822433`.
- Design: one CSS file, fonts Archivo (headings) + Source Sans 3 (body), palette tokens in `:root`
  (maroon `#822433`, ink, muted, line, panel). The only JS is `assets/js/flow.js` (home hero canvas).
- `noindex: true` in `_config.yml` keeps the site out of search engines during the preview phase;
  set it to false only when the user says the site is launched.
- Home page is only the hero: no content that repeats other pages. No News page.
- CSS/JS links carry `?v={{ site.time }}` for cache busting; keep it on any new asset link.
- Team links are icons (`assets/img/icons/`: Sapienza seal, ORCID iD); no emails on the Team page.
- Publications page is "Selected publications": journal articles from 2020 onward, each with a DOI,
  curated by hand. Team names to bold are in `highlight_authors` in `_config.yml`.
- Photos in `assets/img/photos/` come from the group's open-access CC BY papers; each needs a caption,
  credit and DOI (`_includes/photo.html`). Do not use figures from non-open-access or NC-ND papers.
- Member photos: square JPG, ~400px, in `assets/img/people/`, referenced by file name in `members.yml`.
- Preview locally (Ruby 3.3 from Homebrew) before pushing; check desktop and 375px mobile.
- Workflow: edit, preview, commit with a clear message, push to `main`.
