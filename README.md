# FLUXS – Fluid Experiments at Sapienza

Website of FLUXS (Fluid Experiments at Sapienza), Sapienza University of Rome. Built with Jekyll and published with GitHub Pages.

## Where to edit content

| What | File |
|---|---|
| Group name, description, address, email | `_config.yml` |
| Research areas | `_data/research.yml` |
| Measurement techniques | `_data/techniques.yml` |
| Facilities (wind tunnel, lab) | `_data/facilities.yml` |
| Team | `_data/members.yml` (+ photos in `assets/img/people/`) |
| Courses | `_data/teaching.yml` |
| PhD programmes | `_data/phd.yml` |
| Publications | `_data/publications.yml` |
| Styles / colors | `assets/css/style.css` |
| Home flow animation | `assets/js/flow.js` |

Every push to `main` republishes the site automatically (1–2 minutes).

## Local preview (optional)

```bash
bundle install
bundle exec jekyll serve
```

Ruby 3.3 is needed (Homebrew: `brew install ruby@3.3`, then
`export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"`). Gems install into `vendor/bundle`.
