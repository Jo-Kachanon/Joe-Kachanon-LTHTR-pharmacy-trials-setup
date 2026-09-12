# -*- coding: utf-8 -*-
"""Regenerate overleaf/Chapters/ChapterN.tex from the Markdown source.
Counted body only: appendices, provenance notes and the draft-status line are excluded."""
import io, os, re, sys

MD = "/Users/josmacbook/Documents/NHS_Improving Pharmacy_Clinical _Trials _Setup _Capacity/Dissertation"

CITE = [
 (r"\(Department of Health and Social Care, 2025\)", r"\\citep{anon2025Support}"),
 (r"O'Shaughnessy \(2023\)", r"\\citet{OShaughnessy2023Commercial}"),
 (r"Walker et al\. \(2018\)", r"\\citet{Walker2018Metrics}"),
 (r"Whitham et al\. \(2018\)", r"\\citet{Whitham2018Metrics}"),
 (r"Ofosu et al\. \(2021\)", r"\\citet{Ofosu2021ProcessMapping}"),
 (r"Shabtay et al\., 2013", r"\\citealp{Shabtay2013Rejection}"),
 (r"Shabtay et al\. \(2013\)", r"\\citet{Shabtay2013Rejection}"),
 (r"Slotnick and Morton \(2007\)", r"\\citet{SlotnickMorton2007OrderAcceptance}"),
 (r"Slotnick and Morton, 2007", r"\\citealp{SlotnickMorton2007OrderAcceptance}"),
 (r"Lewis and Slotnick \(2002\)", r"\\citet{LewisSlotnick2002MultiPeriod}"),
 (r"Deglise-Hawkinson et al\. \(2020\)", r"\\citet{DegliseHawkinson2020CAPTAIN}"),
 (r"Jones and Tamiz, 2010", r"\\citealp{JonesTamiz2010GoalProgramming}"),
 (r"Munoz et al\. \(2018\)", r"\\citet{Munoz2018ProposalSelection}"),
 (r"Munoz et al\., 2018", r"\\citealp{Munoz2018ProposalSelection}"),
 (r"Blake and Carter \(2002\)", r"\\citet{BlakeCarter2002GP}"),
 (r"Atsmony and Mosheiov \(2023\)", r"\\citet{AtsmonyMosheiov2023OnTime}"),
 (r"Atsmony and Mosheiov", r"\\citet{AtsmonyMosheiov2023OnTime}"),
 (r"Gupta \(2013\)", r"\\citet{Gupta2013Queueing}"),
 (r"Lahiri and Seidmann \(2012\)", r"\\citet{LahiriSeidmann2012HangOvers}"),
 (r"Lahiri and Seidmann", r"\\citeauthor{LahiriSeidmann2012HangOvers}"),
 (r"Svirsko et al\. \(2022\)", r"\\citet{Svirsko2022Medication}"),
 (r"Svirsko et al\.", r"\\citeauthor{Svirsko2022Medication}"),
 (r"Demir et al\., 2017; Harper et al\., 2023", r"\\citealp{Demir2017DemandCapacity,Harper2023Orthopaedic}"),
 (r"Martinez et al\. \(2016\)", r"\\citet{Martinez2016TrialActivation}"),
 (r"Kheiri et al\. \(2021\)", r"\\citet{Kheiri2021Theatre}"),
 (r"Mavrotas et al\. \(2015\)", r"\\citet{Mavrotas2015Robustness}"),
 (r"Morris et al\., 2019", r"\\citealp{Morris2019SimulationStudies}"),
 (r"Morris et al\. \(2019\)", r"\\citet{Morris2019SimulationStudies}"),
 (r"Barton \(2012\)", r"\\citet{Barton2012InputUncertainty}"),
 (r"Qi et al\., 2022", r"\\citealp{Qi2022EquitableEnrolment}"),
 (r"Qi et al\. \(2022\)", r"\\citet{Qi2022EquitableEnrolment}"),
]

# labels the appendices reference; keep these names exactly
SEC = {"1.1":"sec:background","1.2":"sec:opproblem","1.3":"sec:objective","1.4":"sec:questions","1.5":"sec:structure",
 "2.1":"sec:mapping","2.2":"sec:selection","2.3":"sec:ordered","2.4":"sec:shared","2.5":"sec:contribution",
 "3.1":"sec:inpractice","3.2":"sec:scope","3.3":"sec:sets","3.4":"sec:queue","3.5":"sec:model","3.6":"sec:notdecided",
 "4.1":"sec:datasources","4.2":"sec:parameters","4.2.1":"sec:available","4.2.2":"sec:casestudies",
 "4.2.3":"sec:preparation","4.3":"sec:experiments","4.3.1":"sec:comparison","4.4":"sec:verification",
 "5.1":"sec:realqueues","5.2":"sec:whythese","5.3":"sec:delivery","5.4":"sec:levers","5.5":"sec:targeting","5.6":"sec:tradeoff",
 "6.1":"sec:answers","6.2":"sec:contrib6","6.3":"sec:limitations","6.4":"sec:implications"}
EQ = {"3.1":"eq:dueday","3.2":"eq:weight","3.3":"eq:loadselector","3.4":"eq:ontime","3.5":"eq:lateness",
      "3.6":"eq:ontimecount","3.7":"eq:objectives","4.1":"eq:available","4.2":"eq:lead","4.4":"eq:pk"}
TAB = {"1.1":"tab:questions","2.1":"tab:litsummary","4.1":"tab:sources","4.2":"tab:regimes","4.3":"tab:analyses",
       "5.1":"tab:fourtrials5","5.3":"tab:settings","6.1":"tab:answers"}
FIG = {"4.1":"fig:datasources","4.2":"fig:segments","4.3":"fig:solution","5.1":"fig:planactual",
       "5.2":"fig:allcases","5.3":"fig:planuncertainty","5.4":"fig:preparation","5.5":"fig:burdenslack",
       "5.6":"fig:frontier","5.7":"fig:prepsteps","5.8":"fig:tradeoffpair"}
CH = {1:("Introduction","ch:intro"),2:("Literature Review","ch:litreview"),3:("Problem Description","ch:problem"),
      4:("Methodology","ch:method"),5:("Results","ch:results"),6:("Conclusion","ch:conclusion")}

def esc(t):
    """Escape LaTeX specials outside math, then restore inline math."""
    parts = re.split(r"(\$[^$]*\$)", t)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            out.append(p); continue
        p = p.replace("\\", "\\textbackslash{}")
        for c in "&%#":
            p = p.replace(c, "\\" + c)
        p = p.replace("_", "\\_")
        p = p.replace("’", "'").replace("‘", "`").replace("“", "``").replace("”", "''")
        p = p.replace("–", "--").replace("—", "---").replace("…", "\\ldots{}")
        p = p.replace("\u2265", "$\\geq$").replace("\u2264", "$\\leq$").replace("\u2713", "$\\checkmark$").replace("\u2714", "$\\checkmark$")
        out.append(p)
    return "".join(out)

def inline(t):
    t = t.replace("`[edit]`", "").replace("`[edited]`", "")
    t = esc(t)                      # escape first; every command below is inserted after
    for pat, rep in CITE:
        t = re.sub(pat, rep, t)
    t = re.sub(r"§§\s*([0-9]+\.[0-9]+)[^0-9]{1,3}([0-9]+\.[0-9]+)",
               lambda m: "Sections~\\ref{%s} to~\\ref{%s}" % (SEC.get(m.group(1),"sec:x"), SEC.get(m.group(2),"sec:x")), t)
    t = re.sub(r"§\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
               lambda m: "Section~\\ref{%s}" % SEC.get(m.group(1), "sec:x"), t)
    t = re.sub(r"equation \(([0-9]+\.[0-9]+)\)",
               lambda m: "equation~(\\ref{%s})" % EQ.get(m.group(1), "eq:x"), t)
    t = re.sub(r"\bTable ([0-9]+\.[0-9]+)\b",
               lambda m: "Table~\\ref{%s}" % TAB[m.group(1)] if m.group(1) in TAB else m.group(0), t)
    t = re.sub(r"\bFigure ([0-9]+\.[0-9]+)\b",
               lambda m: "Figure~\\ref{%s}" % FIG[m.group(1)] if m.group(1) in FIG else m.group(0), t)
    t = re.sub(r"Appendix ([0-9]\.[A-Z])",
               lambda m: "Appendix~\\ref{app:notation}" if m.group(1) == "3.A" else m.group(0), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"\\emph{\1}", t)
    t = re.sub(r"`([^`]+)`", r"\\texttt{\1}", t)
    return re.sub(r"\s+", " ", t).strip()

def body(path):
    """Counted body only."""
    lines = io.open(path, encoding="utf-8").read().split("\n")
    end = len(lines)
    for i, l in enumerate(lines):
        if l.startswith("## Appendix") or l.startswith("## Source and provenance"):
            end = i; break
    return [l for l in lines[:end]
            if not l.startswith("> ") and not l.startswith("**Draft status.**")]

def table(block, num, cap):
    rows = [r for r in block if r.startswith("|")]
    grid = []
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c): continue
        grid.append(cells)
    n = max(len(r) for r in grid)
    grid = [r + [""] * (n - len(r)) for r in grid]
    head, rest = grid[0], grid[1:]
    spec = "@{}" + ("l" if n > 2 else "L") + "L" * (n - 1) + "@{}"
    o = ["\\begin{table}[htbp]", "  \\centering", "  \\caption{%s}" % inline(cap),
         "  \\label{%s}" % TAB.get(num, "tab:x"),
         "  \\begin{tabularx}{\\textwidth}{%s}" % spec, "    \\toprule",
         "    " + " & ".join("\\textbf{%s}" % inline(c) for c in head) + " \\\\", "    \\midrule"]
    for i, r in enumerate(rest):
        o.append("    " + " & ".join(inline(c) for c in r) + " \\\\")
        if i < len(rest) - 1: o.append("    \\addlinespace")
    o += ["    \\bottomrule", "  \\end{tabularx}", "\\end{table}"]
    return o

def figure(num, cap, img, note):
    o = ["\\begin{figure}[htbp]", "  \\centering",
         "  \\includegraphics[width=\\textwidth]{%s}" % os.path.basename(img)]
    c = inline(cap)
    if note: c += " " + inline(note)
    o += ["  \\caption{%s}" % c, "  \\label{%s}" % FIG.get(num, "fig:x"), "\\end{figure}"]
    return o

def convert(n, src):
    L = body(os.path.join(MD, src))
    title, chlab = CH[n]
    out = ["%% Chapter %d, %s." % (n, title),
           "%% Generated from Dissertation/%s by tools/md2tex.py." % src,
           "%% The draft-status line, the provenance notes and the [edit] markers in the",
           "%% Markdown source are not part of the submitted text and are absent here.",
           "%% Markdown is the source. Regenerate this file when it changes; do not hand-edit.",
           "", "\\chapter{%s}" % title, "\\label{%s}" % chlab,
           "\\lhead{Chapter %d. \\emph{%s}}" % (n, title), ""]
    i, para = 0, []
    def flush():
        if para:
            out.append(inline(" ".join(para))); out.append("")
            para.clear()
    while i < len(L):
        l = L[i]
        m = re.match(r"^(#{1,3}) ([0-9.]+) (.+)$", l)
        if m and len(m.group(1)) > 1:
            flush()
            num, t = m.group(2), m.group(3).replace("`[edit]`", "").strip()
            cmd = "section" if len(m.group(1)) == 2 else "subsection"
            out += ["\\%s{%s}" % (cmd, inline(t)), "\\label{%s}" % SEC.get(num, "sec:x"), ""]
            i += 1; continue
        if l.startswith("# "): i += 1; continue
        m = re.match(r"^\*\*Table ([0-9]+\.[0-9]+)\*\*", l)
        if m:
            flush(); num = m.group(1); j = i + 1
            while j < len(L) and not L[j].strip(): j += 1
            cap = L[j].strip().strip("*"); j += 1
            while j < len(L) and not L[j].startswith("|"): j += 1
            k = j
            while k < len(L) and (L[k].startswith("|") or not L[k].strip()):
                if not L[k].strip() and k + 1 < len(L) and not L[k + 1].startswith("|"): break
                k += 1
            out += table(L[j:k], num, cap); out.append("")
            while k < len(L) and (not L[k].strip() or L[k].startswith("Note.") or L[k].startswith("*Note.")):
                if L[k].strip().startswith(("Note.", "*Note.")):
                    out.append("\\begin{tablenotes}" if False else "\\noindent\\footnotesize %s\\normalsize" % inline(L[k]))
                    out.append("")
                k += 1
            i = k; continue
        m = re.match(r"^\*\*Figure ([0-9]+\.[0-9]+)\*\*", l)
        if m:
            flush(); num = m.group(1); j = i + 1
            while j < len(L) and not L[j].strip(): j += 1
            cap = L[j].strip().strip("*"); j += 1
            img, note = None, None
            while j < len(L):
                mm = re.match(r"^!\[.*?\]\((.+?)\)\s*$", L[j])
                if mm: img = mm.group(1); j += 1; continue
                if L[j].strip().startswith("*Note.*"): note = L[j].strip(); j += 1; continue
                if not L[j].strip(): j += 1
                else: break
            out += figure(num, cap, img or "missing.png", note); out.append("")
            i = j; continue
        if l.startswith("$$"):
            flush()
            eq = l.strip().strip("$")
            tag = re.search(r"\\tag\{([0-9.]+)\}", eq)
            eq = re.sub(r"\\tag\{[0-9.]+\}", "", eq).strip()
            out += ["\\begin{equation}", "  " + eq,
                    "  \\label{%s}" % EQ.get(tag.group(1) if tag else "", "eq:x"),
                    "\\end{equation}", ""]
            i += 1; continue
        if not l.strip(): flush(); i += 1; continue
        if l.startswith("- "):
            flush(); items = []
            while i < len(L) and L[i].startswith("- "):
                items.append("  \\item " + inline(L[i][2:])); i += 1
            out += ["\\begin{itemize}"] + items + ["\\end{itemize}", ""]; continue
        para.append(l); i += 1
    flush()
    return "\n".join(out).replace("\n\n\n", "\n\n") + "\n"

if __name__ == "__main__":
    files = {1:"Chapter1_Introduction.md",2:"Chapter2_Literature_Review.md",3:"Chapter3_Problem_Description.md",
             4:"Chapter4_Methodology.md",5:"Chapter5_Results.md",6:"Chapter6_Conclusion.md"}
    outdir = sys.argv[1]
    for n, f in files.items():
        t = convert(n, f)
        io.open(os.path.join(outdir, "Chapter%d.tex" % n), "w", encoding="utf-8").write(t)
        print("Chapter%d.tex  %5d bytes  %4d words" % (n, len(t), len(t.split())))
