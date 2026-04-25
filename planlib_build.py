#!/usr/bin/env python3
"""planlib_build.py — PlanLib build tool.

Commands:
    build   Generate HTML pages from problem directories.
    serve   Serve the output on a local HTTP server (clean URLs, no file://).
    new     Scaffold a new empty problem directory.

Examples:
    python planlib_build.py build --all
    python planlib_build.py serve
    python planlib_build.py serve --port 3000
    python planlib_build.py build problems/prob001-blocksworld/
    python planlib_build.py new prob005-mystery
    python planlib_build.py new prob005-mystery --domains base typed

Problem directory structure:
    prob001-blocksworld/
      general.md          -- front matter + Description, History, Variants, Complexity
      references.md       -- ## References and ## BibTeX  (optional)
      domains/
        <key>/
          domain.md       -- domain front matter + State Space, Types, Objects,
                             Predicates, Actions, Goal, Instances sections
          domain.pddl     -- PDDL domain file  (optional / placeholder)
          instances/
            *.pddl        -- PDDL instance files  (optional / placeholder)
"""

import argparse
import datetime
import http.server
import os
import re
import shutil
import sys
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    sys.exit("Jinja2 is required:  pip install jinja2")

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  pip install pyyaml")

SCRIPT_DIR       = Path(__file__).parent
DEFAULT_PROBLEMS = SCRIPT_DIR / "problems"
DEFAULT_TMPL     = SCRIPT_DIR / "templates"
DEFAULT_STATIC   = SCRIPT_DIR / "static"
DEFAULT_OUTPUT   = SCRIPT_DIR / "output"
TEMPLATE            = "problem.html.j2"
INDEX_TEMPLATE      = "index.html.j2"
LIST_TEMPLATE       = "list.html.j2"
GROUPED_TEMPLATE    = "grouped_list.html.j2"
CONTRIBUTE_TEMPLATE = "contribute.html.j2"

# ── Tag colour helpers (used by both make_env and build_index) ────────────────
_BLUE_TAGS  = frozenset({'Typed', 'ADL', 'FOND', 'Probabilistic', 'Stochastic', 'Partial'})
_GREEN_TAGS = frozenset({'Classical', 'STRIPS'})

def _tag_class(tag: str) -> str:
    if tag in _BLUE_TAGS:  return 'tag-blue'
    if tag in _GREEN_TAGS: return 'tag-green'
    return 'tag-neutral'

_GREEN_CHIPS = frozenset({'Classical', 'STRIPS'})
_BLUE_CHIPS  = frozenset({'Typed', 'ADL', 'FOND'})

def _chip_style(tag: str) -> str:
    if tag in _GREEN_CHIPS: return 'on-green'
    if tag in _BLUE_CHIPS:  return 'on-blue'
    return 'on-neutral'

def _group_slug(label: str) -> str:
    """Convert a group label to a URL-safe slug, e.g. 'PDDL 2.1' -> 'pddl-21'."""
    s = label.lower().replace(' ', '-').replace('.', '')
    return re.sub(r'-+', '-', s).strip('-')

# Tags too universal to be useful as filters
_SKIP_FILTER_TAGS = frozenset({'Fully Observable', 'Deterministic'})


# ══════════════════════════════════════════════════════════════════════════════
# Shared helpers
# ══════════════════════════════════════════════════════════════════════════════

def _split_fm(text: str) -> tuple[dict, str]:
    """Split YAML front matter from body. Returns (fm_dict, body_str)."""
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def _split_sections(body: str, marker: str = '##') -> dict[str, str]:
    """Split body on `## Heading` markers. Returns {heading: content} dict."""
    sections: dict[str, str] = {}
    current_key:   str | None = None
    current_lines: list[str]  = []
    pat = re.compile(rf'^{re.escape(marker)} (.+)$')
    for line in body.splitlines():
        m = pat.match(line)
        if m:
            if current_key is not None:
                sections[current_key] = '\n'.join(current_lines).strip()
            current_key   = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_key is not None:
        sections[current_key] = '\n'.join(current_lines).strip()
    return sections


def _parse_predicate_table(text: str) -> list[dict]:
    predicates = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('|---') or re.match(r'^\| *name', ln, re.I):
            continue
        if ln.startswith('|'):
            cells = [c.strip() for c in ln.strip('|').split('|')]
            if len(cells) >= 2:
                predicates.append({'name': cells[0], 'desc': cells[1]})
    return predicates


def _parse_actions(text: str) -> list[dict]:
    actions = []
    for block in re.split(r'^#### ', text, flags=re.MULTILINE):
        if not block.strip():
            continue
        bl    = block.splitlines()
        hdr   = bl[0].strip()
        parts = re.split(r' [—–-] ', hdr, maxsplit=1)
        name  = parts[0].strip()
        desc  = parts[1].strip() if len(parts) > 1 else ''
        code  = re.search(r'```[^\n]*\n(.*?)```', block, re.DOTALL)
        schema = code.group(1).rstrip() if code else ''
        actions.append({'name': name, 'desc': desc, 'schema': schema})
    return actions


def _cell(cells: list[str], i: int) -> str:
    return cells[i] if i < len(cells) else ''


# ══════════════════════════════════════════════════════════════════════════════
# Domain markdown parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_domain_md(domain_md_path: Path, key: str) -> tuple[dict, list[dict]]:
    """Parse domains/<key>/domain.md.

    Returns:
        domain_entry  -- dict ready for problem['domains']['entries']
        inst_rows     -- raw instance rows (id/domain added by caller)

    Instances table columns: | name | n | k* | status | source | file |
    File paths in the table are relative to the domain folder (e.g. instances/foo.pddl).
    The caller rewrites them to be relative to the problem root.
    """
    text = domain_md_path.read_text(encoding='utf-8')
    fm, body = _split_fm(text)
    sub = _split_sections(body)

    predicates = _parse_predicate_table(sub.get('Predicates', ''))
    actions    = _parse_actions(sub.get('Actions', ''))

    # Instances table: | name | n | k* | status | source | file |
    inst_rows: list[dict] = []
    for ln in sub.get('Instances', '').splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('|---') or re.match(r'^\| *name', ln, re.I):
            continue
        if not ln.startswith('|'):
            continue
        cells  = [c.strip() for c in ln.strip('|').split('|')]
        name   = _cell(cells, 0)
        n_raw  = _cell(cells, 1)
        k_raw  = _cell(cells, 2)
        status = _cell(cells, 3)
        src    = _cell(cells, 4)
        fpath  = _cell(cells, 5)

        def _int_or(s: str):
            return int(s) if s.lstrip('-').isdigit() else (None if s in ('', '-') else s)

        inst_rows.append({
            'name':       name,
            'n':          _int_or(n_raw),
            'optimal':    _int_or(k_raw),
            'status':     status,
            'source_ref': src or None,
            'language':   'PDDL',
            'domain':     key,        # filled in by caller
            'file':       fpath or None,
        })

    viewpoint = {
        'state_space': sub.get('State Space', ''),
        'types':       sub.get('Types', ''),
        'objects':     sub.get('Objects', ''),
        'predicates':  predicates,
        'actions':     actions,
        'goal':        sub.get('Goal', ''),
    }

    entry: dict = {
        'key':      key,
        'title':    fm.get('title', key),
        'language': fm.get('language', 'PDDL'),
        'file':     f"domains/{key}/domain.pddl",
        'notes':    fm.get('notes', ''),
        'viewpoint': viewpoint,
        # stash per-domain instance metadata; caller may use as fallback
        '_instances_description': fm.get('instances_description', ''),
        '_generator_note':        fm.get('generator_note', ''),
    }
    if 'source' in fm:
        entry['source_ref'] = fm['source']

    return entry, inst_rows


# ══════════════════════════════════════════════════════════════════════════════
# References markdown parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_references_md(ref_text: str) -> tuple[list[dict], str]:
    """Parse references.md -> (refs list, bibtex string).

    The file starts with ## References (no front matter expected, but handled).
    """
    if ref_text.lstrip().startswith('---'):
        _, body = _split_fm(ref_text)
    else:
        body = ref_text

    top = _split_sections(body)

    refs: list[dict] = []
    current_ref: dict | None = None
    for ln in top.get('References', '').splitlines():
        ln = ln.strip()
        m = re.match(r'^\[(\w+)\]:\s*(.+)$', ln)
        if m:
            if current_ref:
                refs.append(current_ref)
            current_ref = {'key': m.group(1), 'title': m.group(2).strip()}
        elif current_ref:
            kv = re.match(r'^(\w[\w ]*?):\s*(.+)$', ln)
            if kv:
                current_ref[kv.group(1).strip().lower()] = kv.group(2).strip()
    if current_ref:
        refs.append(current_ref)

    bibtex_raw = top.get('BibTeX', '')
    bm = re.search(r'```(?:bibtex)?\n(.*?)```', bibtex_raw, re.DOTALL)
    bibtex = bm.group(1).strip() if bm else ''

    return refs, bibtex


# ══════════════════════════════════════════════════════════════════════════════
# Problem directory parser
# ══════════════════════════════════════════════════════════════════════════════

def parse_problem_dir(prob_dir: Path) -> dict:
    """Parse a problem directory into the dict the Jinja2 template expects.

    Expected layout:
        prob_dir/
          general.md
          references.md    (optional)
          domains/
            <key>/
              domain.md
              domain.pddl  (optional)
              instances/   (optional)
                *.pddl
    """
    # ── general.md ───────────────────────────────────────────────────────────
    gm_text = (prob_dir / 'general.md').read_text(encoding='utf-8')
    fm, body = _split_fm(gm_text)
    if not fm:
        raise ValueError(f"{prob_dir}/general.md: missing YAML front matter")
    sections = _split_sections(body)

    problem = dict(fm)

    # ── meta sidebar ─────────────────────────────────────────────────────────
    cs = problem.get('complexity_summary', {})
    complexity_display = (
        '\n'.join(f"{k}: {v}" for k, v in cs.items())
        if isinstance(cs, dict) else str(cs) if cs else ''
    )
    problem['meta'] = {
        'ID':           problem.get('id', ''),
        'Origin':       problem.get('origin', ''),
        'Proposer':     ', '.join(problem.get('proposers', [])),
        'Category':     (problem.get('category', '') + ' planning').strip(),
        'Complexity':   complexity_display,
        'IPC editions': ', '.join(str(e) for e in problem.get('ipc_editions', [])),
    }

    # ── description sections ─────────────────────────────────────────────────
    def _parse_generic_section(text: str, heading: str) -> dict:
        """Parse a ## section body into a dict with 'heading', 'variants', 'body'."""
        text = text.strip()
        variant_lines: list[dict] = []
        body_lines:    list[str]  = []
        in_variants = False
        for ln in text.splitlines():
            if re.match(r'^- .+', ln):
                item = ln[2:].strip()
                # Support [label](href) markdown links in variant items
                m_link = re.match(r'^\[(.+?)\]\((.+?)\)$', item)
                if m_link:
                    variant_lines.append({'label': m_link.group(1), 'href': m_link.group(2)})
                else:
                    variant_lines.append({'label': item, 'href': None})
                in_variants = True
            elif in_variants and not ln.strip():
                # blank line immediately after the list — skip it as a separator
                continue
            else:
                in_variants = False   # back to normal body text
                body_lines.append(ln)
        body_text  = '\n'.join(body_lines).strip()
        paragraphs = [p.strip() for p in re.split(r'\n\n+', body_text) if p.strip()]
        sec: dict = {'heading': heading}
        if variant_lines:
            sec['variants'] = variant_lines
        if paragraphs:
            sec['body'] = '\n\n'.join(paragraphs)  # preserve paragraph breaks for md_body
        return sec

    desc_sections: list[dict] = []

    for sec_name, sec_body in sections.items():
        if sec_name == 'Complexity':
            pass  # handled below
        elif sec_name in ('Variants', 'Variants and Extensions'):
            desc_sections.append(_parse_generic_section(sec_body, 'Variants and Extensions'))
        else:
            desc_sections.append(_parse_generic_section(sec_body, sec_name))

    problem['description'] = {'overview': [], 'sections': desc_sections}

    # ── Complexity table ──────────────────────────────────────────────────────
    complexity_rows = []
    for line in sections.get('Complexity', '').splitlines():
        line = line.strip()
        if not line or line.startswith('|---') or re.match(r'^\| *Problem', line, re.I):
            continue
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) >= 4:
                complexity_rows.append({
                    'problem':   cells[0],
                    'qualifier': cells[1] or None,
                    'result':    cells[2],
                    'class':     cells[3].lower(),
                })

    problem['formal']  = {'complexity': complexity_rows}
    problem['results'] = {'mathematical': []}

    # ── Domain entries ────────────────────────────────────────────────────────
    domains_dir = prob_dir / 'domains'
    domain_entries: list[dict] = []
    all_inst_rows:  list[dict] = []

    if domains_dir.is_dir():
        for domain_subdir in sorted(d for d in domains_dir.iterdir() if d.is_dir()):
            domain_md = domain_subdir / 'domain.md'
            if not domain_md.exists():
                continue
            key = domain_subdir.name
            try:
                entry, inst_rows = parse_domain_md(domain_md, key)
            except Exception as e:
                print(f"  WARN  {domain_md}: {e}")
                continue

            domain_entries.append(entry)
            for row in inst_rows:
                # Rewrite instance file path relative to problem root
                if row.get('file'):
                    row['file'] = f"domains/{key}/{row['file']}"
                row['id'] = len(all_inst_rows) + 1
                all_inst_rows.append(row)

    # First domain populates problem.formal with viewpoint data
    if domain_entries:
        vp = domain_entries[0]['viewpoint']
        problem['formal'].update({
            'state_space': vp['state_space'],
            'types':       vp.get('types', ''),
            'objects':     vp['objects'],
            'predicates':  vp['predicates'],
            'actions':     vp['actions'],
            'goal':        vp['goal'],
        })

    # instances_description / generator_note: general.md fm wins; else first domain
    inst_desc = fm.get('instances_description', '')
    gen_note  = fm.get('generator_note', '')
    if not inst_desc and domain_entries:
        inst_desc = domain_entries[0].get('_instances_description', '')
    if not gen_note and domain_entries:
        gen_note = domain_entries[0].get('_generator_note', '')

    for entry in domain_entries:
        entry.pop('_instances_description', None)
        entry.pop('_generator_note', None)

    problem['domains'] = {
        'entries': domain_entries,
    }
    problem['instances'] = {
        'description':    inst_desc,
        'generator_note': gen_note,
        'rows':           all_inst_rows,
    }

    # ── References + BibTeX ───────────────────────────────────────────────────
    ref_path = prob_dir / 'references.md'
    if ref_path.exists():
        refs, bibtex = parse_references_md(ref_path.read_text(encoding='utf-8'))
    else:
        refs, bibtex = [], ''

    problem['references'] = refs
    problem['bibtex']     = bibtex

    return problem


# ══════════════════════════════════════════════════════════════════════════════
# File inlining helpers
# ══════════════════════════════════════════════════════════════════════════════

def _inline_file_contents(problem: dict, base_dir: Path) -> list[str]:
    """Attach `_content` to domain/instance entries that have a `file` key."""
    missing = []

    def _read(rel: str) -> str | None:
        p = base_dir / rel
        if p.exists():
            return p.read_text(encoding='utf-8')
        missing.append(rel)
        return None

    for domain in problem.get('domains', {}).get('entries', []):
        if domain.get('file'):
            domain['_content'] = _read(domain['file'])
    for row in problem.get('instances', {}).get('rows', []):
        if row.get('file'):
            row['_content'] = _read(row['file'])

    return missing


# ══════════════════════════════════════════════════════════════════════════════
# Build pipeline
# ══════════════════════════════════════════════════════════════════════════════

def build_problem(prob_dir: Path, output_dir: Path, env) -> dict | None:
    """Parse *prob_dir* and write an HTML file to *output_dir*.

    PDDL file contents are inlined as JavaScript strings in the HTML
    (domainContents / instanceContents arrays) for the download buttons,
    so no separate asset files are copied to the output directory.

    Returns the parsed problem dict on success, None on failure.
    """
    try:
        problem = parse_problem_dir(prob_dir)
    except Exception as e:
        print(f"  ERROR  {prob_dir.name}: {e}")
        return None

    missing = _inline_file_contents(problem, prob_dir)

    template = env.get_template(TEMPLATE)
    html     = template.render(problem=problem, base='../../')

    slug     = problem['slug']
    html_dir = output_dir / 'problems' / slug
    html_dir.mkdir(parents=True, exist_ok=True)
    html_path = html_dir / 'index.html'
    html_path.write_text(html, encoding='utf-8')

    warn = f"  MISSING: {', '.join(missing)}" if missing else ""
    print(f"  OK  {prob_dir.name}  ->  problems/{slug}/index.html{warn}")
    return problem


def build_index(problems: list[dict], output_dir: Path, env) -> None:
    """Build output/index.html from all parsed problem dicts."""
    total_problems  = len(problems)
    total_domains   = sum(len(p.get('domains', {}).get('entries', [])) for p in problems)
    total_instances = sum(len(p.get('instances', {}).get('rows', [])) for p in problems)

    template = env.get_template(INDEX_TEMPLATE)
    html = template.render(
        base='',
        stats={
            'problems':  total_problems,
            'domains':   total_domains,
            'instances': total_instances,
        },
    )

    out = output_dir / 'index.html'
    out.write_text(html, encoding='utf-8')
    print(f"  OK  index.html  ({total_problems} problems, {total_domains} domains, {total_instances} instances)")


def build_list(
    output_slug: str,
    page_title: str,
    breadcrumb: list[dict],
    items: list[dict],
    output_dir: Path,
    env,
    description: str = '',
    tag_chips: list[dict] | None = None,
    all_ipc: list[str] | None = None,
    all_langs: list[str] | None = None,
    base: str = '../',
) -> None:
    """Render list.html.j2 to *output_dir*/*output_slug*/index.html.

    breadcrumb: list of {'label': str, 'href': str|None}
                The final (current) item should have href=None.
    """
    template = env.get_template(LIST_TEMPLATE)
    html = template.render(
        base=base,
        page_title=page_title,
        breadcrumb=breadcrumb,
        items=items,
        description=description,
        tag_chips=tag_chips or [],
        all_ipc=all_ipc or [],
        all_langs=all_langs or [],
    )
    out_dir = output_dir / output_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'index.html').write_text(html, encoding='utf-8')
    print(f"  OK  {output_slug}/index.html  ({len(items)} items)")


def build_grouped_list(
    output_slug: str,
    page_title: str,
    breadcrumb: list[dict],
    groups: list[dict],
    output_dir: Path,
    env,
    description: str = '',
) -> None:
    """Render grouped_list.html.j2 to *output_dir*/*output_slug*/index.html.

    groups: list of {'label': str, 'items': [problem_dict]}
    """
    template = env.get_template(GROUPED_TEMPLATE)
    html = template.render(
        base='../',
        page_title=page_title,
        breadcrumb=breadcrumb,
        groups=groups,
        description=description,
    )
    out_dir = output_dir / output_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'index.html').write_text(html, encoding='utf-8')
    total = sum(len(g['problems']) for g in groups)
    print(f"  OK  {output_slug}/index.html  ({len(groups)} groups, {total} entries)")


def _md_body(text: str):
    """Jinja2 filter: convert a markdown section body to HTML.

    Handles fenced code blocks (``` ... ```) and inline backtick code.
    Everything else is split on blank lines into <p> paragraphs.
    Returns a Markup string safe for Jinja2's autoescape.
    """
    from markupsafe import Markup, escape

    if not text:
        return Markup('')

    # Split on fenced code blocks — odd-indexed pieces are code content
    pieces = re.split(r'(```[^\n]*\n.*?```)', text.strip(), flags=re.DOTALL)
    html_parts: list[str] = []

    for i, piece in enumerate(pieces):
        if i % 2 == 1:
            # Code block — strip the opening/closing fences
            inner = re.sub(r'^```[^\n]*\n', '', piece)
            inner = re.sub(r'```$', '', inner).rstrip()
            html_parts.append(f'<div class="code-wrap"><pre>{escape(inner)}</pre></div>')
        else:
            # Plain text — split into paragraphs, handle inline code
            for para in re.split(r'\n\n+', piece.strip()):
                para = para.strip()
                if not para:
                    continue
                # Inline code: `foo` → <code>foo</code>
                inline = re.split(r'`([^`]+)`', para)
                rendered = ''.join(
                    str(escape(p)) if j % 2 == 0 else f'<code>{escape(p)}</code>'
                    for j, p in enumerate(inline)
                )
                html_parts.append(f'<p>{rendered}</p>')

    return Markup('\n'.join(html_parts))


def make_env(template_dir: Path):
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(['html']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters['md_body']   = _md_body
    env.filters['tag_class'] = _tag_class
    return env


def build_contribute(output_dir: Path, env) -> None:
    """Render the contribute/submit form page."""
    template = env.get_template(CONTRIBUTE_TEMPLATE)
    html = template.render(base='../')
    out_dir = output_dir / 'contribute'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'index.html').write_text(html, encoding='utf-8')
    print('  OK  contribute/index.html')


def copy_static(static_src: Path, output_dir: Path) -> None:
    """Copy static/ assets to output/static/."""
    if not static_src.is_dir():
        print(f"  WARN  static source not found: {static_src}")
        return
    dst = output_dir / 'static'
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(static_src, dst)
    files = [f.name for f in dst.iterdir() if f.is_file()]
    print(f"  static/  ({', '.join(sorted(files))})")


# ══════════════════════════════════════════════════════════════════════════════
# ID assignment
# ══════════════════════════════════════════════════════════════════════════════

def _set_fm_field(path: Path, key: str, value: str) -> None:
    """Set a single YAML front matter field in a file, preserving all other content."""
    text = path.read_text(encoding='utf-8')
    m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    if not m:
        return
    fm_block = m.group(1)
    rest     = text[m.end():]
    key_pat  = re.compile(rf'^{re.escape(key)}:.*$', re.MULTILINE)
    if key_pat.search(fm_block):
        fm_block = key_pat.sub(f'{key}: {value}', fm_block)
    else:
        fm_block = f'{key}: {value}\n' + fm_block
    path.write_text(f'---\n{fm_block}\n---\n{rest}', encoding='utf-8')


def assign_ids(prob_dirs: list[Path]) -> None:
    """Assign stable probNNN IDs to any problems that do not have one yet.

    Problems already carrying a valid probNNN id are left untouched.
    New IDs are assigned in alphabetical order of the directory name and
    written back into general.md so they are stable across all future builds.
    """
    existing_nums: set[int] = set()
    unassigned:    list[Path] = []

    for prob_dir in prob_dirs:
        gm_path = prob_dir / 'general.md'
        try:
            fm, _ = _split_fm(gm_path.read_text(encoding='utf-8'))
        except Exception:
            continue
        m = re.match(r'^prob(\d+)$', str(fm.get('id', '')))
        if m:
            existing_nums.add(int(m.group(1)))
        else:
            unassigned.append(prob_dir)

    if not unassigned:
        return

    next_n = 1
    for prob_dir in sorted(unassigned, key=lambda p: p.name):
        while next_n in existing_nums:
            next_n += 1
        new_id = f'prob{next_n:03d}'
        existing_nums.add(next_n)
        next_n += 1
        _set_fm_field(prob_dir / 'general.md', 'id', new_id)
        print(f"  assigned  {new_id}  ->  {prob_dir.name}/")


# ══════════════════════════════════════════════════════════════════════════════
# Problem scaffolding
# ══════════════════════════════════════════════════════════════════════════════

PDDL_PLACEHOLDER = ';; placeholder — PDDL file not yet added\n'


def make_problem(prob_dir: Path, domain_keys: list[str]) -> None:
    """Scaffold a new empty problem directory.

    The directory name is the slug (e.g. 'hanoi').
    A stable probNNN id is assigned automatically on the first build.

    Creates general.md, references.md, and for each domain key:
      domains/<key>/domain.md
      domains/<key>/domain.pddl
      domains/<key>/instances/instance-01.pddl
    """
    if prob_dir.exists():
        sys.exit(f"Directory already exists: {prob_dir}")

    slug  = prob_dir.name
    title = slug.replace('-', ' ').title()
    today = datetime.date.today().isoformat()
    languages = list(dict.fromkeys('PDDL 2.1' for _ in domain_keys))

    # ── general.md ────────────────────────────────────────────────────────────
    # id is intentionally absent — assigned automatically on first build.
    general_md = f"""\
---
slug: {slug}
title: {title}
subtitle: "TODO: one-sentence description of the problem."
proposers: ["First Author", "Second Author"]
origin: "TODO: conference or paper where the domain was introduced"
origin_year: YYYY
last_updated: "{today}"
category: Classical
tags: [Classical, Fully Observable, Deterministic]
languages: [{', '.join(languages)}]
ipc_editions: []
complexity_summary: {{existence: TODO, optimal: TODO}}
---

## Description

TODO: describe the problem setup — what objects exist, what actions are
possible, and what must be achieved.

## History

TODO: when and where was this domain introduced? Mention IPC editions if applicable.

## Variants

- [Variant name](#domain-key)     ← links to domain card on this page
- [Related problem](https://url)  ← links to external page
- Plain text entry for variants without a domain page yet

## Complexity

| Problem | Qualifier | Result | Class |
|---|---|---|---|
| Plan existence | | | hard |
| Optimal plan length | | | hard |
| Satisficing plan | | | easy |
"""

    # ── references.md ─────────────────────────────────────────────────────────
    references_md = """\
## References

[Key1]: TODO: full title of the paper
  authors: TODO
  venue: TODO: conference name, year
  url: https://doi.org/...

## BibTeX

```bibtex
@inproceedings{key1,
  author    = {TODO},
  title     = {TODO},
  booktitle = {TODO},
  year      = {YYYY},
}
```
"""

    # ── domain.md (one per key) ───────────────────────────────────────────────
    def domain_md(key: str) -> str:
        return f"""\
---
title: "TODO: domain title"
language: PDDL 2.1
source: Key1
notes: "TODO: brief notes on this formulation — typed vs untyped, extensions, etc."
instances_description: "TODO: how instances are parameterised (e.g. by number of objects)."
generator_note: "TODO: link to generator or instance archive."
---

## State Space

TODO: describe what a state encodes and the state space size.

## Types

TODO: list types and hierarchy if the domain uses PDDL typing.
If untyped STRIPS, remove this section.

## Objects

TODO: list the kinds of objects present in every instance.

## Predicates

| name | desc |
|---|---|
| pred(?x) | TODO |
| pred(?x, ?y) | TODO |

## Actions

#### action(?x - type) — TODO: short description
```
preconditions: TODO
add effects:   TODO
del effects:   TODO
```

## Goal

TODO: describe the goal condition.

## Instances

| name | n | k* | status | source | file |
|---|---|---|---|---|---|
| instance-01 | - | - | unknown | | instances/instance-01.pddl |
"""

    # ── Write everything ──────────────────────────────────────────────────────
    prob_dir.mkdir(parents=True)
    (prob_dir / 'general.md').write_text(general_md,    encoding='utf-8')
    (prob_dir / 'references.md').write_text(references_md, encoding='utf-8')

    for key in domain_keys:
        domain_dir = prob_dir / 'domains' / key
        inst_dir   = domain_dir / 'instances'
        inst_dir.mkdir(parents=True)
        (domain_dir / 'domain.md').write_text(domain_md(key),  encoding='utf-8')
        (domain_dir / 'domain.pddl').write_text(PDDL_PLACEHOLDER, encoding='utf-8')
        (inst_dir / 'instance-01.pddl').write_text(PDDL_PLACEHOLDER, encoding='utf-8')

    print(f"Created {prob_dir}/")
    print(f"  general.md  (id will be assigned on first build)")
    print(f"  references.md")
    for key in domain_keys:
        print(f"  domains/{key}/domain.md")
        print(f"  domains/{key}/domain.pddl")
        print(f"  domains/{key}/instances/instance-01.pddl")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description='PlanLib build tool.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subs = p.add_subparsers(dest='command', required=True)

    # ── build ─────────────────────────────────────────────────────────────────
    build_p = subs.add_parser(
        'build',
        help='Generate HTML pages from problem directories.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = build_p.add_mutually_exclusive_group(required=True)
    src.add_argument('prob_dir', nargs='?', metavar='PROBLEM_DIR',
                     help='Single problem directory (must contain general.md)')
    src.add_argument('--all', action='store_true',
                     help='Build every problem directory in --problems-dir')
    build_p.add_argument('--problems-dir', default=str(DEFAULT_PROBLEMS),
                         help=f'Parent directory of problem subdirs (default: {DEFAULT_PROBLEMS})')
    build_p.add_argument('--output-dir',   default=str(DEFAULT_OUTPUT),
                         help=f'Directory to write HTML into (default: {DEFAULT_OUTPUT})')
    build_p.add_argument('--template-dir', default=str(DEFAULT_TMPL),
                         help=f'Directory containing {TEMPLATE} (default: {DEFAULT_TMPL})')

    # ── serve ─────────────────────────────────────────────────────────────────
    serve_p = subs.add_parser(
        'serve',
        help='Serve the output directory on a local HTTP server.',
    )
    serve_p.add_argument('--output-dir', default=str(DEFAULT_OUTPUT),
                         help=f'Directory to serve (default: {DEFAULT_OUTPUT})')
    serve_p.add_argument('--port', type=int, default=8000,
                         help='Port to listen on (default: 8000)')

    # ── new ───────────────────────────────────────────────────────────────────
    new_p = subs.add_parser(
        'new',
        help='Scaffold a new empty problem directory.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    new_p.add_argument('name', metavar='SLUG',
                       help='Problem slug — directory name, e.g. "hanoi" or "tower-of-hanoi". A stable probNNN id is assigned automatically on first build.')
    new_p.add_argument('--domains', nargs='+', default=['base'], metavar='KEY',
                       help='Domain keys to scaffold (default: base)')
    new_p.add_argument('--problems-dir', default=str(DEFAULT_PROBLEMS),
                       help=f'Parent directory for new problem (default: {DEFAULT_PROBLEMS})')

    args = p.parse_args()

    # ── dispatch: build ───────────────────────────────────────────────────────
    if args.command == 'build':
        template_dir = Path(args.template_dir)
        if not (template_dir / TEMPLATE).exists():
            sys.exit(f"Template not found: {template_dir / TEMPLATE}")

        env        = make_env(template_dir)
        output_dir = Path(args.output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        if args.all:
            for item in output_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)

        copy_static(DEFAULT_STATIC, output_dir)

        if args.all:
            problems_dir = Path(args.problems_dir)
            prob_dirs = sorted(
                d for d in problems_dir.iterdir()
                if d.is_dir() and (d / 'general.md').exists()
            )
            if not prob_dirs:
                sys.exit(f"No problem directories found in {problems_dir}")
            assign_ids(prob_dirs)
            print(f"\nBuilding {len(prob_dirs)} problem(s) -> {output_dir}/\n")
            built_problems = []
            for d in prob_dirs:
                problem = build_problem(d, output_dir, env)
                if problem:
                    built_problems.append(problem)
            build_index(built_problems, output_dir, env)

            # Shared filter data (reused across list pages)
            all_tags_seen: list[str] = []
            for p in built_problems:
                for t in p.get('tags', []):
                    if t not in _SKIP_FILTER_TAGS and t not in all_tags_seen:
                        all_tags_seen.append(t)
            shared_chips = [{'tag': t, 'style': _chip_style(t)} for t in all_tags_seen]
            shared_ipc   = sorted(set(str(e) for p in built_problems for e in p.get('ipc_editions', [])))
            shared_langs = sorted(set(f for p in built_problems for f in p.get('languages', [])))

            build_list(
                output_slug='problems',
                page_title='Problems',
                breadcrumb=[{'label': 'Problems', 'href': None}],
                items=built_problems,
                output_dir=output_dir,
                env=env,
                description='All planning benchmark domains in the library.',
                tag_chips=shared_chips,
                all_ipc=shared_ipc,
                all_langs=shared_langs,
            )

            # ── Languages ─────────────────────────────────────────────────────
            all_languages = sorted(set(
                f for p in built_problems for f in p.get('languages', [])
            ))
            language_groups = [
                {
                    'label': f,
                    'slug':  _group_slug(f),
                    'problems': [p for p in built_problems if f in p.get('languages', [])],
                }
                for f in all_languages
            ]
            build_grouped_list(
                output_slug='languages',
                page_title='Languages',
                breadcrumb=[{'label': 'Languages', 'href': None}],
                groups=language_groups,
                output_dir=output_dir,
                env=env,
                description='Problems grouped by planning language.',
            )
            for g in language_groups:
                build_list(
                    output_slug=f"languages/{g['slug']}",
                    page_title=g['label'],
                    breadcrumb=[
                        {'label': 'Languages', 'href': '../'},
                        {'label': g['label'],   'href': None},
                    ],
                    items=g['problems'],
                    output_dir=output_dir,
                    env=env,
                    description=f"Problems using {g['label']}.",
                    base='../../',
                )

            # ── IPC editions ──────────────────────────────────────────────────
            all_ipc_editions = sorted(set(
                str(e) for p in built_problems for e in p.get('ipc_editions', [])
            ))
            ipc_groups = [
                {
                    'label': ed,
                    'slug':  _group_slug(ed),
                    'problems': [
                        p for p in built_problems
                        if ed in [str(e) for e in p.get('ipc_editions', [])]
                    ],
                }
                for ed in all_ipc_editions
            ]
            build_grouped_list(
                output_slug='ipc',
                page_title='IPC Editions',
                breadcrumb=[{'label': 'IPC Editions', 'href': None}],
                groups=ipc_groups,
                output_dir=output_dir,
                env=env,
                description='Problems organized by International Planning Competition edition.',
            )
            for g in ipc_groups:
                build_list(
                    output_slug=f"ipc/{g['slug']}",
                    page_title=g['label'],
                    breadcrumb=[
                        {'label': 'IPC', 'href': '../'},
                        {'label': g['label'], 'href': None},
                    ],
                    items=g['problems'],
                    output_dir=output_dir,
                    env=env,
                    description=f"Problems from {g['label']}.",
                    base='../../',
                )

            # ── Tags ──────────────────────────────────────────────────────────
            all_tags = sorted(set(
                t for p in built_problems for t in p.get('tags', [])
            ))
            tag_groups = [
                {
                    'label': t,
                    'slug':  _group_slug(t),
                    'problems': [p for p in built_problems if t in p.get('tags', [])],
                }
                for t in all_tags
            ]
            build_grouped_list(
                output_slug='tags',
                page_title='Tags',
                breadcrumb=[{'label': 'Tags', 'href': None}],
                groups=tag_groups,
                output_dir=output_dir,
                env=env,
                description='Problems grouped by tag.',
            )
            for g in tag_groups:
                build_list(
                    output_slug=f"tags/{g['slug']}",
                    page_title=g['label'],
                    breadcrumb=[
                        {'label': 'Tags', 'href': '../'},
                        {'label': g['label'], 'href': None},
                    ],
                    items=g['problems'],
                    output_dir=output_dir,
                    env=env,
                    description=f"Problems tagged {g['label']}.",
                    base='../../',
                )

            # ── Contribute form ───────────────────────────────────────────────
            build_contribute(output_dir, env)
        else:
            prob_dir = Path(args.prob_dir)
            if not prob_dir.is_dir():
                sys.exit(f"Not a directory: {prob_dir}")
            if not (prob_dir / 'general.md').exists():
                sys.exit(f"No general.md found in: {prob_dir}")
            assign_ids([prob_dir])
            print(f"\nBuilding -> {output_dir}/\n")
            build_problem(prob_dir, output_dir, env)

        print('\nDone.')

    # ── dispatch: serve ───────────────────────────────────────────────────────
    elif args.command == 'serve':
        output_dir = Path(args.output_dir)
        if not output_dir.is_dir():
            sys.exit(f"Output directory not found: {output_dir}  (run 'build --all' first)")
        os.chdir(output_dir)
        addr = ('', args.port)
        handler = http.server.SimpleHTTPRequestHandler
        with http.server.HTTPServer(addr, handler) as srv:
            print(f"Serving {output_dir.resolve()} at http://localhost:{args.port}/")
            print("Press Ctrl+C to stop.")
            try:
                srv.serve_forever()
            except KeyboardInterrupt:
                print("\nStopped.")

    # ── dispatch: new ─────────────────────────────────────────────────────────
    elif args.command == 'new':
        prob_dir = Path(args.problems_dir) / args.name
        make_problem(prob_dir, args.domains)


if __name__ == '__main__':
    main()
