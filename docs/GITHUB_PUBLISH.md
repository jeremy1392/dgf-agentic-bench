# Publishing this repository on GitHub

## 1. Choose a repository name

Suggested: `DGF-Bench`.

## 2. Licensing

The original DGF-Bench source code and original benchmark documentation are dual-licensed under **MIT OR Apache-2.0**, at the user's option.

Relevant files:

- `LICENSE` — scope and dual-license notice;
- `LICENSE-MIT` — full MIT License;
- `LICENSE-APACHE` — full Apache License 2.0;
- `NOTICE` — notice file for the Apache-2.0 option;
- `THIRD_PARTY_NOTICES.md` — material with separate terms.

The `paper/` directory is included for reproducibility but is not automatically relicensed by the software dual license. Microsoft Azure icons remain under Microsoft's own included terms regardless of the project license.

## 3. Run preflight

```bash
make test
make preflight
```

## 4. Initialize Git

```bash
git init
git add .
git commit -m "Initial DGF-Bench release"
git branch -M main
```

## 5. Connect GitHub

```bash
git remote add origin git@github.com:YOUR_USERNAME/DGF-Bench.git
git push -u origin main
```

or use the HTTPS remote.

## 6. After the first push

Update `CITATION.cff` with the final repository URL if desired, then commit that change. You may also add the arXiv identifier to the README and citation metadata once the paper has a permanent identifier.

## 7. Never commit

- `.env`;
- OpenRouter API keys;
- private hidden evaluation datasets intended for leaderboard use;
- confidential enterprise evidence;
- local evaluation output containing provider/account metadata you do not want public.
