import sys
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), ".."))
from tgraph import t_cells, is_black
from construct import longest_path, longest_length

CELL = 34

def svg(p, path=None, numbers=True, mark=(), note_cells=(), prefix=None, cap=""):
    W, H1, w, H2, left = p
    cells = t_cells(*p)
    rows = H1 + H2
    pad = 6
    width, height = W * CELL + 2 * pad, rows * CELL + 2 * pad
    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" role="img">']
    on = {}
    if path:
        use = path if prefix is None else path[:prefix]
        on = {c: i + 1 for i, c in enumerate(use)}
    for (r, c) in cells:
        x, y = pad + c * CELL, pad + r * CELL
        fill = "var(--blk)" if is_black((r, c)) else "var(--wht)"
        stroke = "var(--grid)"
        out.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
    for (r, c) in note_cells:
        x, y = pad + c * CELL, pad + r * CELL
        out.append(f'<rect x="{x+2}" y="{y+2}" width="{CELL-4}" height="{CELL-4}" fill="none" stroke="var(--warn)" stroke-width="3" rx="4"/>')
    if path:
        use = path if prefix is None else path[:prefix]
        pts = " ".join(f"{pad + c * CELL + CELL / 2},{pad + r * CELL + CELL / 2}" for r, c in use)
        # bar part / stem part in two colours
        segs = []
        cur, kind = [], None
        for (r, c) in use:
            k = "bar" if r < H1 else "stem"
            if kind is not None and k != kind:
                segs.append((kind, cur + [(r, c)]))
                cur = [(r, c)]
            else:
                cur.append((r, c))
            kind = k
        segs.append((kind, cur))
        for k, seg in segs:
            pts = " ".join(f"{pad + c * CELL + CELL / 2},{pad + r * CELL + CELL / 2}" for r, c in seg)
            col = "var(--bar)" if k == "bar" else "var(--stem)"
            out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" opacity="0.85"/>')
        if numbers:
            for (r, c), i in on.items():
                x, y = pad + c * CELL + CELL / 2, pad + r * CELL + CELL / 2
                out.append(f'<circle cx="{x}" cy="{y}" r="9.5" fill="var(--bg)" stroke="var(--ink2)" stroke-width="0.8"/>')
                out.append(f'<text x="{x}" y="{y + 3.6}" font-size="10" text-anchor="middle" fill="var(--ink)" font-family="ui-monospace,monospace">{i}</text>')
        s, e = use[0], use[-1]
        for (r, c), col in ((s, "var(--start)"), (e, "var(--end)")):
            x, y = pad + c * CELL, pad + r * CELL
            out.append(f'<rect x="{x+1.5}" y="{y+1.5}" width="{CELL-3}" height="{CELL-3}" fill="none" stroke="{col}" stroke-width="3"/>')
        if prefix is None:
            for (r, c) in cells:
                if (r, c) not in on:
                    x, y = pad + c * CELL + CELL / 2, pad + r * CELL + CELL / 2
                    out.append(f'<path d="M{x-8},{y-8}L{x+8},{y+8}M{x+8},{y-8}L{x-8},{y+8}" stroke="var(--miss)" stroke-width="3" stroke-linecap="round"/>')
    for (r, c) in mark:
        x, y = pad + c * CELL + CELL / 2, pad + r * CELL + CELL / 2
        bx, by = x + CELL / 2 - 7, y - CELL / 2 + 7
        out.append(f'<circle cx="{bx}" cy="{by}" r="6.5" fill="var(--warn)"/>')
        out.append(f'<text x="{bx}" y="{by + 3.5}" font-size="10" font-weight="700" text-anchor="middle" fill="#fff">!</text>')
    out.append("</svg>")
    return f'<figure>{"".join(out)}<figcaption>{cap}</figcaption></figure>'


def ltr(s):
    return f'<span class="ltr">{s}</span>'


def P(p):
    return ltr("T(" + ", ".join(map(str, p)) + ")")


def info(p):
    W, H1, w, H2, left = p
    n = W * H1 + w * H2
    cells = t_cells(*p)
    b = sum(is_black(c) for c in cells)
    return n, b, n - b


def example(p, title, explain, extra_figs="", numbers=True, mark=(), note=()):
    n, b, wh = info(p)
    path = longest_path(*p)
    L = len(path)
    W, H1, w, H2, left = p
    right = W - w - left
    params = (f'<div class="params">{ltr(f"W={W}")} {ltr(f"H1={H1}")} {ltr(f"w={w}")} {ltr(f"H2={H2}")} '
              f'{ltr(f"left={left}")} {ltr(f"right={right}")}</div>')
    counts = f'<p class="counts">تعداد رأس‌ها {ltr(f"n = {W}×{H1} + {w}×{H2} = {n}")} · سیاه {b} · سفید {wh} · سقف رنگ‌آمیزی {n}</p>'
    fig = svg(p, path, numbers=numbers, mark=mark, note_cells=note,
              cap=f'جواب: مسیری با <b>{L}</b> رأس از {n} رأس. شماره‌ها ترتیب حرکت روی مسیرند.')
    return f'''<div class="example"><h4>{title} {P(p)}</h4>{params}{counts}
<div class="figs">{extra_figs}{fig}</div><div class="explain">{explain}</div></div>'''


S = []

# ---------- case 1 definition ----------
pd = (3, 1, 1, 2, 1)
pd_short = [(0, 0), (0, 1), (0, 2)]
pd_long = longest_path(*pd)
pe = (7, 3, 1, 4, 3)
pe_a = [(r, 3) for r in range(6, 2, -1)] + [(2, 3), (1, 3), (0, 3), (0, 2), (1, 2), (2, 2), (2, 1), (1, 1), (0, 1), (0, 0), (1, 0), (2, 0)]
S.append(f"""
<section id="def"><h2>تعریف حالت ۱</h2>
<p>یه گراف T داریم. می‌خوایم توش یه <b>مسیر</b> پیدا کنیم که تا جای ممکن طولانی باشه.</p>
<p><b>مسیر</b> یعنی:</p>
<ul>
<li>از یه خونه شروع می‌کنیم و هر بار به یکی از خونه‌های کناری (بالا، پایین، چپ یا راست) میریم. حرکت مورب نداریم.</li>
<li>از هیچ خونه‌ای دو بار رد نمیشیم.</li>
<li><b>طول مسیر</b> = تعداد خونه‌هایی که مسیر ازشون رد میشه، با خونه اول و آخر.</li>
</ul>
<p>به خونه شروع مسیر میگیم {ltr("s")} و به خونه پایان میگیم {ltr("t")}.</p>
<p class="cond">حالت ۱ (s نامشخص، t نامشخص): هیچ محدودیتی روی شروع و پایان نیست. خودمون هر {ltr("s")} و هر {ltr("t")} که بخوایم انتخاب می‌کنیم، به شرطی که مسیر بلندترین بشه.</p>
<p><b>ورودی:</b> پنج عدد شکل T. &nbsp; <b>خروجی:</b> طول بلندترین مسیر، و خود مسیر (این‌که از کجا شروع بشه، از چه خونه‌هایی رد بشه و کجا تموم بشه).</p>
<p>برای مقایسه، دو حالت دیگه این‌ها هستن:</p>
<div class="tablewrap"><table><thead><tr><th>حالت</th><th>شروع {ltr("s")}</th><th>پایان {ltr("t")}</th><th>سوال</th></tr></thead><tbody>
<tr><td><b>۱ (همین فایل)</b></td><td>نامشخص (خودمون انتخاب می‌کنیم)</td><td>نامشخص</td><td>بلندترین مسیر کل گراف چنده؟</td></tr>
<tr><td>۲</td><td>مشخص (داده شده)</td><td>نامشخص</td><td>از این خونه شروع کنیم، بلندترین مسیر چنده؟</td></tr>
<tr><td>۳</td><td>مشخص</td><td>مشخص</td><td>بلندترین مسیر از این خونه به اون خونه چنده؟</td></tr>
</tbody></table></div>
<p>توی ربات جاروبرقی، حالت ۱ یعنی ربات می‌تونه از هر جای اتاق شروع کنه و هر جا تموم کنه، و می‌خوایم بیشترین خونه‌ها رو بدون تکرار تمیز کنه.</p>
<div class="example"><h4>یه مثال کوچیک: {P(pd)}</h4>
<p>این T فقط ۵ خونه داره: یه ردیف ۳ خونه‌ای بالا و یه ستون ۲ خونه‌ای زیر خونه وسط.</p>
<div class="figs">
{svg(pd, pd_short, cap="یه مسیر ممکن: ۳ خونه. مسیر درستیه ولی بلندترین نیست.")}
{svg(pd, pd_long, cap=f"بلندترین مسیر: <b>{len(pd_long)}</b> خونه. از ته ستون شروع میشه و به یه سر ردیف ختم میشه.")}
</div>
<p>چرا نمیشه هر ۵ خونه رو رفت؟ مسیر وقتی از خونه وسط رد بشه، فقط می‌تونه دو تا از سه طرف (چپ، راست، پایین) رو بره، پس همیشه یه بخش جا می‌مونه. جواب حالت ۱ برای این گراف <b>۴</b> هست.</p></div>
<div class="example"><h4>یه مثال بزرگ‌تر: {P(pe)}</h4>
<div class="figs">
{svg(pe, pe_a, cap="یه مسیر ممکن با ۱۶ خونه: رفته سمت چپ و توی گوشه گیر کرده، چون همه همسایه‌های خونه آخر قبلاً رفته شدن. کل سمت راست جا مونده.")}
{svg(pe, longest_path(*pe), cap=f"بلندترین مسیر: <b>{len(longest_path(*pe))}</b> خونه از ۲۵ خونه.")}
</div>
<p>کار ما توی حالت ۱ اینه که برای <b>هر</b> T فرد، بدون امتحان کردن همه مسیرها، جواب شکل دوم رو مستقیم پیدا کنیم. بقیه این فایل نشون میده چطوری.</p></div>
</section>""")

# ---------- intro ----------
p0 = (9, 3, 4, 4, 2)
S.append(f'''
<section id="setup"><h2>۱. گراف T چیه و با چه عددهایی تعریف میشه</h2>
<p>هر گراف T با پنج عدد ساخته میشه:</p>
<ul>
<li>{ltr("W")}: پهنای میله افقی بالا</li>
<li>{ltr("H1")}: ارتفاع میله افقی</li>
<li>{ltr("w")}: پهنای ستون پایینی</li>
<li>{ltr("H2")}: ارتفاع ستون</li>
<li>{ltr("left")}: تعداد ستون‌های میله که سمت چپ ستون پایینی هستن، و {ltr("right = W − w − left")} تعداد ستون‌های سمت راست</li>
</ul>
<p>شماره سطرها از بالا و شماره ستون‌ها از چپ شروع میشه، هر دو از صفر. هر خونه یه رأسه و دو خونه‌ای که یه ضلع مشترک دارن به هم وصلن.</p>
<p><b>اندازه فرد</b> یعنی تعداد کل رأس‌ها، {ltr("n = W×H1 + w×H2")}، فرده.</p>
<div class="figs">{svg(p0, None, cap=f"مثال {P(p0)}: میله ۹×۳ و ستون ۴×۴، یعنی ۴۳ رأس")}</div>
</section>''')

S.append(f'''
<section id="color"><h2>۲. رنگ‌آمیزی و سقف</h2>
<p>خونه‌ها رو مثل صفحه شطرنج رنگ می‌کنیم: اگه {ltr("سطر + ستون")} زوج باشه سیاه (توی شکل‌ها خاکستری)، وگرنه سفید. هر قدم روی مسیر از یه رنگ به رنگ دیگه میره، پس رنگ‌ها روی مسیر یکی‌درمیون عوض میشن.</p>
<p>توی T فرد یه اتفاق جالب میفته:</p>
<ul>
<li>مستطیلی که مساحتش زوجه، به همون تعداد سیاه و سفید داره.</li>
<li>مستطیلی که مساحتش فرده، یه خونه بیشتر از رنگ گوشه‌هاش داره.</li>
<li>چون {ltr("n")} فرده، دقیقاً یکی از دو تا مستطیل (میله یا ستون) مساحت فرد داره.</li>
</ul>
<p>پس توی هر T فرد، تعداد دو رنگ <b>دقیقاً یکی</b> با هم فرق داره، و سقف رنگ‌آمیزی همیشه برابر خود {ltr("n")} میشه. یعنی سوال فقط اینه: <b>آیا مسیری هست که از همه خونه‌ها رد بشه؟</b> (به این مسیر میگن مسیر همیلتونی.)</p>
</section>''')

# ---------- two facts ----------
pf = (7, 1, 1, 4, 2)
S.append(f'''
<section id="facts"><h2>۳. دو تا واقعیت ساده که همه استدلال‌ها روشون بنا شده</h2>
<div class="fact"><b>واقعیت الف: خونه بن‌بست باید سر یا ته مسیر باشه.</b>
<p>خونه‌ای که فقط یه همسایه داره، اگه وسط مسیر باشه باید هم ازش وارد بشی هم ازش خارج بشی، که دو تا همسایه لازم داره. پس اگه مسیر بخواد ازش رد بشه، حتماً باید سر یا ته مسیر باشه.</p></div>
<div class="fact"><b>واقعیت ب: مسیری که از همه خونه‌ها رد بشه، سر و تهش رنگ اکثریت دارن.</b>
<p>رنگ‌ها روی مسیر یکی‌درمیون عوض میشن. اگه سیاه‌ها یکی بیشتر باشن و بخوایم همه رو بریم، مسیر باید این شکلی باشه: سیاه، سفید، سیاه، ...، سیاه. پس هم سر و هم ته مسیر سیاه (رنگ اکثریت) هستن.</p></div>
<div class="figs">{svg(pf, None, mark=[(0,0),(0,6),(4,2)], cap=f"{P(pf)}: سه تا خونه بن‌بست (نشان نارنجی !)")}</div>
<p>نتیجه: اگه یه T بیشتر از دو تا خونه بن‌بست داشته باشه، یا خونه بن‌بستش رنگ اقلیت باشه، مسیری که از همه خونه‌ها رد بشه وجود نداره.</p>
</section>''')

# ---------- rule table ----------
S.append(f'''
<section id="rules"><h2>قانون کامل حالت ۱</h2>
<p>قانون‌ها رو به همین ترتیب چک کن. اولین قانونی که شرطش برقرار بود، جواب رو میده.</p>
<div class="tablewrap"><table>
<thead><tr><th>قانون</th><th>شرط</th><th>طول بلندترین مسیر</th></tr></thead>
<tbody>
<tr><td>۱</td><td>{ltr("H1 = 1")} و {ltr("w = 1")}</td><td>{ltr("n − min(left, right, H2)")}</td></tr>
<tr><td>۲</td><td>{ltr("H1 = 1")}، {ltr("w ≥ 2")}، {ltr("W")} زوج</td><td>{ltr("n − 1")}</td></tr>
<tr><td>۳</td><td>{ltr("w = 1")}، و {ltr("H1")}، {ltr("W")}، {ltr("left")} هر سه فرد</td><td>{ltr("n − 1")}</td></tr>
<tr><td>۴</td><td>بقیه حالت‌ها</td><td>{ltr("n")} (از همه خونه‌ها رد میشه)</td></tr>
</tbody></table></div>
<div class="legend"><span><i class="sw bar"></i>بخش مسیر توی میله</span><span><i class="sw stem"></i>بخش مسیر توی ستون</span>
<span><i class="sq start"></i>شروع مسیر</span><span><i class="sq end"></i>پایان مسیر</span><span><b class="x">✕</b> خونه‌ای که مسیر ازش رد نمیشه</span><span><b class="warn">!</b> خونه بن‌بست</span></div>
</section>''')

# ---------- rule 1 ----------
r1a, r1b = (7, 1, 1, 4, 2), (7, 1, 1, 2, 3)
S.append(f'''
<section id="rule1"><h2>قانون ۱: میله یک ردیفه و ستون یک‌خونه‌ای</h2>
<p class="cond">شرط: {ltr("H1 = 1")} و {ltr("w = 1")} &nbsp;←&nbsp; جواب: {ltr("n − min(left, right, H2)")}</p>
<p><b>چرا؟</b> اینجا شکل در واقع سه تا خط صافه (بازوی چپ، بازوی راست، ستون) که به یه خونه وسط وصل شدن، و سر هر سه بن‌بسته. مسیر فقط یه بار از خونه وسط رد میشه، پس فقط دو تا از بازوها رو می‌تونه بره. بهترین کار اینه که دو تا بازوی بلندتر رو بره و کوتاه‌ترین رو کنار بذاره.</p>
<p><b>الگوریتم:</b> از ته بلندترین بازو شروع کن، برو تا خونه وسط، بعد برو تا ته دومین بازوی بلند.</p>
{example(r1a, "مثال ۱", f"بازوها: چپ ۲، راست ۴، ستون ۴. کوتاه‌ترین بازو ۲ خونه‌ست، پس جواب {ltr('11 − 2 = 9')}. مسیر از ته ستون شروع میشه، تا خونه وسط بالا میاد و بعد کل بازوی راست رو میره. دو خونه بازوی چپ جا می‌مونن.", mark=[(0,0),(0,6),(4,2)])}
{example(r1b, "مثال ۲", f"بازوها: چپ ۳، راست ۳، ستون ۲. این بار ستون کوتاه‌ترینه، پس جواب {ltr('9 − 2 = 7')}. مسیر کل میله رو از چپ به راست میره و ستون جا می‌مونه.", mark=[(0,0),(0,6),(2,3)])}
</section>''')

# ---------- rule 2 ----------
r2a, r2b = (8, 1, 3, 3, 2), (6, 1, 3, 1, 1)
r2c = (7, 1, 3, 2, 2)
S.append(f'''
<section id="rule2"><h2>قانون ۲: میله یک ردیفه، ستون پهن، {ltr("W")} زوج</h2>
<p class="cond">شرط: {ltr("H1 = 1")}، {ltr("w ≥ 2")}، {ltr("W")} زوج &nbsp;←&nbsp; جواب: {ltr("n − 1")}</p>
<p><b>چرا نمیشه از همه خونه‌ها رد شد؟</b></p>
<ol>
<li>میله یک ردیفه‌ست، پس دو سرش، خونه‌های {ltr("(0, 0)")} و {ltr("(0, W−1)")}، بن‌بستن.</li>
<li>طبق واقعیت الف، هر دو باید سر یا ته مسیر باشن.</li>
<li>طبق واقعیت ب، سر و ته مسیر باید هم‌رنگ باشن (رنگ اکثریت).</li>
<li>ولی وقتی {ltr("W")} زوجه، {ltr("(0, 0)")} سیاهه و {ltr("(0, W−1)")} سفید. پس نمیشه.</li>
</ol>
<p><b>چرا {ltr("n − 1")} میشه؟</b> مسیری که فقط یه خونه رو جا بندازه همیشه وجود داره، و الگوریتم پایین اون رو می‌سازه.</p>
<p><b>الگوریتم:</b> بازوی چپ رو برو، بعد بلوک زیر میله (ستون + تکه میله بالاش) رو مارپیچ برو تا برسی بالای سمت راستش، بعد بازوی راست رو برو. چون پهنای ستون فرده و ارتفاع بلوک زوج، مارپیچ مجبوره یه خونه رو جا بندازه.</p>
{example(r2a, "مثال ۱", f"دو سر میله (نشان نارنجی !) رنگ‌های مختلف دارن، پس جواب {ltr('17 − 1 = 16')}. خونه ✕ تنها خونه‌ای هست که جا می‌مونه.", mark=[(0,0),(0,7)])}
{example(r2b, "مثال ۲", f"کوچیک‌ترین نمونه این قانون. {ltr('n = 9')} و جواب {ltr('8')}.", mark=[(0,0),(0,5)])}
<p><b>مقایسه:</b> یه شکل مشابه با {ltr("W")} فرد قانون ۲ رو نداره. اونجا دو سر میله هم‌رنگن و مسیر از همه خونه‌ها رد میشه (قانون ۴):</p>
{example(r2c, "مثال مقایسه", f"{ltr('W = 7')} فرده، دو سر میله هر دو سیاهن، پس مسیر می‌تونه از یه سر شروع و به سر دیگه ختم بشه. جواب {ltr('n = 13')}.", mark=[(0,0),(0,6)])}
</section>''')

# ---------- rule 3 ----------
r3a, r3b = (7, 3, 1, 4, 3), (3, 3, 1, 2, 1)
r3c = (7, 3, 1, 4, 2)
S.append(f'''
<section id="rule3"><h2>قانون ۳: ستون یک‌خونه‌ای، و {ltr("H1")}، {ltr("W")}، {ltr("left")} هر سه فرد</h2>
<p class="cond">شرط: {ltr("w = 1")}، {ltr("H1")} فرد، {ltr("W")} فرد، {ltr("left")} فرد &nbsp;←&nbsp; جواب: {ltr("n − 1")}</p>
<p><b>چرا نمیشه از همه خونه‌ها رد شد؟</b></p>
<ol>
<li>ستون یک‌خونه‌ایه، پس خونه ته ستون بن‌بسته و طبق واقعیت الف باید سر یا ته مسیر باشه.</li>
<li>میله {ltr("W×H1")} هر دو بعدش فرده، پس یه خونه سیاه اضافه داره (گوشه‌هاش سیاهن). چون {ltr("n")} فرده، {ltr("H2")} زوجه و ستون به همون تعداد سیاه و سفید داره. پس رنگ اکثریت کل شکل سیاهه.</li>
<li>خونه ته ستون در سطر {ltr("H1 + H2 − 1")} و ستون {ltr("left")} هست. با این شرط‌ها مجموع این دو عدد فرده، پس این خونه <b>سفیده</b>.</li>
<li>طبق واقعیت ب، سر و ته مسیر باید سیاه باشن. پس نمیشه.</li>
</ol>
<p><b>الگوریتم:</b> از ته ستون برو بالا، بعد سطر پایین میله رو به چپ برو، بخش چپ میله رو مارپیچ برگرد، و بعد بخش راست رو مارپیچ برو. خونه سمت راست ستون، توی سطر پایین میله، جا می‌مونه.</p>
{example(r3a, "مثال ۱", f"خونه ته ستون (نشان نارنجی !) سفیده ولی اکثریت با سیاهه. جواب {ltr('25 − 1 = 24')}.", mark=[(6,3)])}
{example(r3b, "مثال ۲", f"کوچیک‌ترین نمونه: میله ۳×۳ و ستون ۲ خونه. {ltr('n = 11')} و جواب {ltr('10')}.", mark=[(4,1)])}
<p><b>مقایسه:</b> فقط {ltr("left")} رو از ۳ به ۲ عوض کنیم. حالا خونه ته ستون سیاهه و مسیر از همه خونه‌ها رد میشه (قانون ۴):</p>
{example(r3c, "مثال مقایسه", f"{ltr('left = 2')} زوجه، خونه ته ستون سیاهه و می‌تونه سر مسیر باشه. جواب {ltr('n = 25')}.", mark=[(6,2)])}
</section>''')

# ---------- rule 4 ----------
r4a = (9, 3, 4, 4, 2)
r4b = (8, 3, 3, 3, 2)
r4c = (5, 2, 1, 1, 2)
pa = longest_path(*r4a)
steps = (svg(r4a, pa, prefix=27, cap="قدم ۱: کل میله رو برو و بالای ستون تموم کن (خونه ۲۷)")
         + svg(r4a, pa, prefix=28, cap="قدم ۲: یه قدم بیا پایین توی ستون (خونه ۲۸)"))
S.append(f'''
<section id="rule4"><h2>قانون ۴: بقیه حالت‌ها، مسیر از همه خونه‌ها رد میشه</h2>
<p class="cond">شرط: هیچ‌کدوم از قانون‌های ۱ تا ۳ برقرار نیست &nbsp;←&nbsp; جواب: {ltr("n")}</p>
<p><b>ایده الگوریتم (وقتی {ltr("H1 ≥ 2")}):</b> T رو دو تا مستطیل ببین، میله و ستون.</p>
<ol>
<li>کل میله رو طوری برو که آخرش برسی به خونه‌ای از سطر پایین میله که درست بالای ستونه (ستون {ltr("c")}).</li>
<li>یه قدم بیا پایین توی ستون.</li>
<li>کل ستون رو برو.</li>
</ol>
<p>دو تا ابزار ساده کافیه:</p>
<ul>
<li><b>مستطیلی که مساحتش زوجه</b> یه دور بسته داره که از همه خونه‌هاش رد میشه. پس از هر خونه‌ای که بخوای می‌تونی شروع کنی و کل مستطیل رو بری.</li>
<li><b>مستطیلی که مساحتش فرده</b> این دور رو نداره. ولی اگه از یه خونه رنگ اکثریت (هم‌رنگ گوشه‌ها) شروع کنی، میشه کلش رو رفت. برای همین ستون عبور {ltr("c")} طوری انتخاب میشه که این خونه رنگ درستی داشته باشه.</li>
</ul>
<div class="example"><h4>قدم‌به‌قدم روی {P(r4a)}</h4><div class="figs">{steps}</div></div>
{example(r4a, "قدم ۳: کل ستون رو برو", f"میله ۹×۳ مساحت فرد داره، پس از ستون {ltr('c = 2')} (خونه سیاه) خارج میشیم. ستون ۴×۴ مساحت زوج داره و دور بسته داره. جواب {ltr('n = 43')}.")}
{example(r4b, "مثال ۲: میله زوج، ستون فرد", f"این بار میله ۸×۳ دور بسته داره و ستون ۳×۳ مساحت فرد داره. ستون رو مارپیچ می‌ریم. جواب {ltr('n = 33')}.")}
{example(r4c, "مثال ۳: ستون یک‌خونه‌ای ولی قانون ۳ برقرار نیست", f"{ltr('H1 = 2')} زوجه، پس قانون ۳ برقرار نیست. خونه ته ستون بن‌بسته ولی اشکالی نداره، چون مسیر همون‌جا تموم میشه. جواب {ltr('n = 11')}.", mark=[(2,2)])}
<p>وقتی {ltr("H1 = 1")} باشه (و قانون‌های ۱ و ۲ برقرار نباشن)، همون روش قانون ۲ استفاده میشه ولی اینجا مارپیچ هیچ خونه‌ای رو جا نمی‌ندازه. مثال مقایسه قانون ۲ همین حالت بود.</p>
</section>''')

# ---------- tests ----------
S.append(f'''
<section id="tests"><h2>از کجا مطمئنیم قانون‌های حالت ۱ درستن؟</h2>
<div class="tablewrap"><table><thead><tr><th>تست</th><th>تعداد</th><th>نتیجه</th></tr></thead><tbody>
<tr><td>مقایسه با جواب الگوریتم دقیق (جستجوی کامل) روی دیتاست</td><td>۴۷۵ گراف</td><td>همه برابر</td></tr>
<tr><td>گراف‌های بزرگ‌تر ({ltr("W ≤ 20")}، {ltr("H1 ≤ 9")}، {ltr("H2 ≤ 11")}): مسیر معتبره و طولش با قانون یکیه</td><td>۴۴٬۹۸۵ گراف</td><td>بدون خطا</td></tr>
<tr><td>پیش‌بینی قبل از اجرا برای گراف‌هایی که توی دیتاست نبودن</td><td>۱۴ گراف</td><td>همه درست</td></tr>
<tr><td>سرعت روی یه T با ۳ میلیون رأس</td><td>۱ گراف</td><td>حدود ۱ ثانیه</td></tr>
</tbody></table></div>
<p class="note">قانون از روی داده‌ها پیدا شده. ساخت مسیر نشون میده جواب حداقل این‌قدره، و استدلال‌های قانون ۱ تا ۳ نشون میدن بیشتر از این نمیشه. اثبات کامل هنوز باید نوشته و بررسی بشه.</p>
<p class="note">کد: {ltr("construct.py")} (الگوریتم)، {ltr("verify_construct.py")} (تست‌ها)، شاخه {ltr("linear-algorithm")} در گیت‌هاب.</p>
</section>''')


# ---------- cases 2 and 3 (to be completed) ----------
from exact import Solver, SolverST
pd = (3, 1, 1, 2, 1)
s2 = (0, 0)
L2, path2 = Solver(*pd).longest_from(s2)
t3 = (0, 2)
L3, path3, _ = SolverST(*pd).longest_st(s2, t3)
S.append(f"""
<section id="case2"><h2>تعریف حالت ۲</h2>
<p class="cond">حالت ۲ (s مشخص، t نامشخص): خونه شروع {ltr("s")} از قبل داده شده. مسیر باید از همین خونه شروع بشه، ولی می‌تونه هر جایی تموم بشه.</p>
<p><b>ورودی:</b> پنج عدد شکل T و خونه {ltr("s")}. &nbsp; <b>خروجی:</b> طول بلندترین مسیری که از {ltr("s")} شروع میشه، و خود مسیر.</p>
<p>توی ربات جاروبرقی، {ltr("s")} جای ایستگاه شارژه: ربات همیشه از همون‌جا راه میفته.</p>
<div class="example"><h4>مثال: همون {P(pd)}، با {ltr("s = (0, 0)")}</h4>
<div class="figs">{svg(pd, path2, cap=f"بلندترین مسیر از گوشه چپ: <b>{L2}</b> خونه. توی حالت ۱ هم جواب ۴ بود، پس اینجا شروع از این خونه ضرری نداره.")}</div></div>
<p class="todo">قانون‌های حالت ۲: در حال تکمیل. داده‌هاش توی دیتاست آماده‌ست ({ltr("12,275")} ردیف).</p>
</section>""")
S.append(f"""
<section id="case3"><h2>تعریف حالت ۳</h2>
<p class="cond">حالت ۳ (s مشخص، t مشخص): هم خونه شروع {ltr("s")} و هم خونه پایان {ltr("t")} از قبل داده شدن. مسیر باید از {ltr("s")} شروع و دقیقاً به {ltr("t")} ختم بشه.</p>
<p><b>ورودی:</b> پنج عدد شکل T، خونه {ltr("s")} و خونه {ltr("t")}. &nbsp; <b>خروجی:</b> طول بلندترین مسیر از {ltr("s")} به {ltr("t")}، و خود مسیر.</p>
<p>این همون مسئله‌ایه که مقاله‌های قبلی برای مستطیل و L و C حل کردن. توی ربات جاروبرقی یعنی ربات از ایستگاه شارژ راه میفته و باید جای مشخصی (مثلاً کنار در) کارش تموم بشه.</p>
<div class="example"><h4>مثال: همون {P(pd)}، با {ltr("s = (0, 0)")} و {ltr("t = (0, 2)")}</h4>
<div class="figs">{svg(pd, path3, cap=f"بلندترین مسیر از گوشه چپ به گوشه راست: فقط <b>{L3}</b> خونه. اگه مسیر بره توی ستون، دیگه نمی‌تونه برگرده و به {ltr('t')} برسه.")}</div>
<p>می‌بینی که هر چی محدودیت بیشتر باشه، جواب ممکنه کوتاه‌تر بشه: توی حالت ۱ و ۲ جواب ۴ بود، اینجا ۳.</p></div>
<p class="todo">قانون‌های حالت ۳: در حال تکمیل. داده‌هاش توی دیتاست آماده‌ست ({ltr("150,794")} ردیف، گراف‌ها تا ۴۵ رأس).</p>
</section>""")

# ---------- page order ----------
import re as _re
_byid = {_re.search(r'<section id="([^"]+)"', x).group(1): x for x in S}
BANNER = lambda t, sub: f'<div class="part"><h2>{t}</h2><p>{sub}</p></div>'
S = ([_byid[k] for k in ("setup", "color", "facts")]
     + [BANNER("حالت ۱: s نامشخص، t نامشخص", "مسیر از هر جا شروع و به هر جا ختم میشه")]
     + [_byid[k] for k in ("def", "rules", "rule1", "rule2", "rule3", "rule4", "tests")]
     + [BANNER("حالت ۲: s مشخص، t نامشخص", "در حال تکمیل")]
     + [_byid["case2"]]
     + [BANNER("حالت ۳: s مشخص، t مشخص", "در حال تکمیل")]
     + [_byid["case3"]])

CSS = """
:root{--bg:#fbfaf7;--card:#ffffff;--ink:#1d2330;--ink2:#5a6170;--line:#e4e1d9;--blk:#d6d9df;--wht:#ffffff;--grid:#9aa0aa;
--bar:#2563b0;--stem:#c2410c;--start:#15803d;--end:#b91c1c;--miss:#b91c1c;--warn:#b45309;--accent:#2563b0}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15181e;--card:#1d2129;--ink:#e8e6e1;--ink2:#a4a9b3;--line:#2e333d;
--blk:#3a404c;--wht:#252a33;--grid:#555c68;--bar:#6aa5f0;--stem:#f28b54;--start:#4ade80;--end:#f87171;--miss:#f87171;--warn:#fbbf24;--accent:#6aa5f0}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Vazirmatn,Tahoma,sans-serif;line-height:1.9;font-size:16px}
main{max-width:980px;margin:0 auto;padding:28px 16px 80px}
h1{font-size:1.7rem;margin:0 0 4px} .sub{color:var(--ink2);margin:0 0 20px}
h2{font-size:1.3rem;margin:0 0 10px;color:var(--accent)} h4{margin:0 0 6px;font-size:1.05rem}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:18px 0}
.ltr{direction:ltr;unicode-bidi:isolate;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.92em}
.tablewrap{overflow-x:auto}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 6px} nav a{color:var(--accent);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:2px 12px;font-size:.9rem;background:var(--card)}
.cond{background:color-mix(in srgb,var(--accent) 10%,transparent);border-right:4px solid var(--accent);padding:8px 12px;border-radius:6px;font-weight:600}
.fact{border-right:4px solid var(--warn);padding:4px 12px;margin:10px 0;background:color-mix(in srgb,var(--warn) 8%,transparent);border-radius:6px}
.fact p{margin:4px 0}
table{border-collapse:collapse;width:100%;margin:8px 0} th,td{border:1px solid var(--line);padding:8px 10px;text-align:right;vertical-align:top} th{background:color-mix(in srgb,var(--ink) 5%,transparent)}
.example{border-top:1px dashed var(--line);margin-top:16px;padding-top:14px}
.params{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0} .params .ltr{background:color-mix(in srgb,var(--ink) 6%,transparent);padding:1px 8px;border-radius:5px}
.counts{color:var(--ink2);margin:4px 0}
.figs{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start;margin:8px 0}
figure{margin:0;max-width:100%;overflow-x:auto} figure svg{display:block;max-width:100%;height:auto;direction:ltr}
figcaption{font-size:.88rem;color:var(--ink2);margin-top:4px;max-width:420px}
.explain{margin-top:4px}
.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:.9rem;color:var(--ink2);margin-top:10px}
.sw{display:inline-block;width:22px;height:4px;border-radius:2px;vertical-align:middle;margin-left:6px} .sw.bar{background:var(--bar)} .sw.stem{background:var(--stem)}
.sq{display:inline-block;width:13px;height:13px;border:3px solid;vertical-align:middle;margin-left:6px} .sq.start{border-color:var(--start)} .sq.end{border-color:var(--end)}
.x{color:var(--miss)} .warn{color:var(--warn)}
.note{color:var(--ink2);font-size:.93rem}
.part{margin:34px 0 6px;padding:14px 18px;border-radius:12px;background:var(--accent);color:#fff}.part h2{color:#fff;margin:0;font-size:1.45rem}.part p{margin:2px 0 0;opacity:.9}.todo{border:1px dashed var(--line);padding:8px 12px;border-radius:6px;color:var(--ink2)}
@media (max-width:600px){section{padding:16px 14px} h1{font-size:1.4rem}}
"""

html = f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>طولانی‌ترین مسیر در T فرد</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<h1>طولانی‌ترین مسیر در گراف T با اندازه فرد</h1>
<p class="sub">اول مفاهیم پایه، بعد سه حالت مسئله: حالت ۱ (s و t نامشخص)، حالت ۲ (s مشخص)، حالت ۳ (s و t مشخص).</p>
<nav><a href="#setup">تعریف T</a><a href="#color">رنگ‌آمیزی</a><a href="#facts">دو واقعیت</a><a href="#def">حالت ۱</a><a href="#rules">قانون‌های حالت ۱</a>
<a href="#rule1">قانون ۱</a><a href="#rule2">قانون ۲</a><a href="#rule3">قانون ۳</a><a href="#rule4">قانون ۴</a><a href="#tests">تست‌ها</a><a href="#case2">حالت ۲</a><a href="#case3">حالت ۳</a></nav>
{''.join(S)}
</main></body></html>"""

# sanity: every example length matches rule
for p in [r1a, r1b, r2a, r2b, r2c, r3a, r3b, r3c, r4a, r4b, r4c, p0, pf]:
    assert (p[0]*p[1]+p[2]*p[3]) % 2 == 1, p
    assert len(longest_path(*p)) == longest_length(*p), p
    print(p, info(p), len(longest_path(*p)))
open(__import__("os").path.join(__import__("os").path.dirname(__file__), "longest_path_T.html"), "w", encoding="utf-8").write(html)
print("ok", len(html))
