# -*- coding: utf-8 -*-
import html, sys
import data as D
E = html.escape

def mmss(t):
    t = int(round(t)); return '%d:%02d' % (t // 60, t % 60)

# where each segment lands in the final cut
t = 0.0; USED = {}; INS_AT = {}
for k, i, d in D.EDL:
    if k == 'seg': USED.setdefault(i, []).append((t, t + d))
    else: INS_AT[i] = (t, t + d)
    t += d
TOTAL = t
tot = sum(D.cost(s) for s in D.SEGS)
w1 = sum(D.cost(s) for s in D.SEGS if int(s['id']) <= 11); w2 = tot - w1
n25 = sum(1 for s in D.SEGS if s['model'][0] == '2.5'); nf = len(D.SEGS) - n25
pilot = [s for s in D.SEGS if s['pilot']]
ACTS = {1: '一、开场', 2: '二、好笑的余额', 3: '三、转折', 4: '四、高潮', 5: '五、尾声'}

CSS = r'''
/* layout: one narrow column on a phone. A receipt-style summary on top, then one card per generated segment, grouped by act. */
:root{
  --bg:#f5f2fa; --surface:#ffffff; --paper:#fffdf7; --ink:#241f30; --muted:#665f76; --line:#e1d9ef;
  --accent:#8a74d6; --accent-ink:#5943ab; --accent-soft:#ece6fb;
  --m25-bg:#5943ab; --m25-fg:#ffffff; --fast-bg:#ece6fb; --fast-fg:#4c3d86;
  --ok:#27805f; --ok-soft:#e1f3ea; --star:#a35a12; --star-soft:#fbefdc;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --sans: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#16131e; --surface:#201c2b; --paper:#262132; --ink:#ece8f5; --muted:#a9a1ba; --line:#372f49;
    --accent:#a996ea; --accent-ink:#cbbdf8; --accent-soft:#2d2643;
    --m25-bg:#a996ea; --m25-fg:#1a1528; --fast-bg:#2d2643; --fast-fg:#cbbdf8;
    --ok:#6fcfa8; --ok-soft:#1d3a30; --star:#f0b46a; --star-soft:#3b2c18; color-scheme: dark;
  }
}
:root[data-theme="dark"]{
  --bg:#16131e; --surface:#201c2b; --paper:#262132; --ink:#ece8f5; --muted:#a9a1ba; --line:#372f49;
  --accent:#a996ea; --accent-ink:#cbbdf8; --accent-soft:#2d2643;
  --m25-bg:#a996ea; --m25-fg:#1a1528; --fast-bg:#2d2643; --fast-fg:#cbbdf8;
  --ok:#6fcfa8; --ok-soft:#1d3a30; --star:#f0b46a; --star-soft:#3b2c18; color-scheme: dark;
}
*{ box-sizing:border-box }
body{ background:var(--bg); color:var(--ink); font-family:var(--sans); font-size:16px; line-height:1.65; -webkit-text-size-adjust:100% }
.wrap{ max-width:720px; margin:0 auto; padding-block:20px 56px; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); display:flex; flex-direction:column; gap:30px }
h1,h2,h3,p,ol,ul{ margin:0 }
h2{ font-size:21px; line-height:1.3; text-wrap:balance }
h3{ font-size:17px; line-height:1.35 }
section{ display:flex; flex-direction:column; gap:14px; min-width:0 }
.sub{ color:var(--muted); font-size:15px }
a{ color:var(--accent-ink) }
:focus-visible{ outline:2px solid var(--accent); outline-offset:2px }

/* the summary, set like a till receipt */
.ticket{ background:var(--paper); border-top:2px dashed var(--line); border-bottom:2px dashed var(--line); padding:20px 18px; display:flex; flex-direction:column; gap:14px }
.ticket .brand{ font-family:var(--mono); font-size:13px; letter-spacing:.14em; color:var(--muted) }
.ticket h1{ font-size:28px; line-height:1.2; letter-spacing:.02em }
.rows{ display:flex; flex-direction:column; gap:6px; font-size:15px }
.row{ display:flex; gap:10px; align-items:baseline; min-width:0 }
.row .k{ color:var(--muted); flex:none }
.row .dots{ flex:1; border-bottom:1px dotted var(--muted); opacity:.5; transform:translateY(-4px); min-width:12px }
.row .v{ font-variant-numeric:tabular-nums; text-align:right }
.meter{ display:flex; flex-direction:column; gap:6px }
.meter .label{ font-size:15px }
.meter .label b{ font-family:var(--mono); font-size:19px }
.track{ height:8px; border-radius:99px; background:var(--accent-soft); overflow:hidden }
.track i{ display:block; height:100%; width:0; background:var(--accent); border-radius:99px; transition:width .25s }
@media (prefers-reduced-motion: reduce){ .track i{ transition:none } }

nav{ display:flex; flex-wrap:wrap; gap:8px }
nav a{ text-decoration:none; font-size:14px; padding:6px 12px; border:1px solid var(--line); border-radius:99px; background:var(--surface); color:var(--ink) }

ol.steps{ padding-left:1.3em; display:flex; flex-direction:column; gap:6px }
ul.plain{ padding-left:1.2em; display:flex; flex-direction:column; gap:6px }

.act{ display:flex; align-items:center; gap:12px; margin-top:6px }
.act h3{ flex:none; color:var(--accent-ink) }
.act::after{ content:""; flex:1; border-top:1px solid var(--line) }

.card{ background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:16px; display:flex; flex-direction:column; gap:12px; min-width:0 }
.card.is-done{ border-color:var(--ok) }
.head{ display:flex; flex-wrap:wrap; align-items:center; gap:8px 10px }
.head h3{ flex:1 1 auto; min-width:0 }
.no{ font-family:var(--mono); color:var(--accent-ink); margin-right:6px }
.tags{ display:flex; flex-wrap:wrap; gap:6px }
.tag{ font-size:12.5px; line-height:1; padding:5px 8px; border-radius:6px; background:var(--fast-bg); color:var(--fast-fg); white-space:nowrap; font-variant-numeric:tabular-nums }
.tag.m25{ background:var(--m25-bg); color:var(--m25-fg); font-weight:600 }
.tag.star{ background:var(--star-soft); color:var(--star); font-weight:600 }
.tag.plain{ background:transparent; border:1px solid var(--line); color:var(--muted) }
.where{ font-size:14px; color:var(--muted); font-variant-numeric:tabular-nums }
.says{ display:flex; flex-direction:column; gap:8px; border-left:3px solid var(--accent-soft); padding-left:12px }
.say .en{ font-family:var(--mono); font-size:14.5px; overflow-wrap:anywhere }
.say .zh{ font-size:14px; color:var(--muted) }
.say .who{ font-size:12.5px; color:var(--accent-ink); margin-right:6px }
.refs{ font-size:14.5px }
.refs ol{ margin:4px 0 0; padding-left:1.4em }
.lbl{ font-size:13px; color:var(--muted) }
.copyrow{ display:flex; flex-wrap:wrap; align-items:center; gap:10px }
button.copy{ font:inherit; font-size:15px; font-weight:600; padding:10px 16px; border-radius:10px; border:1px solid var(--accent); background:var(--accent-soft); color:var(--accent-ink); cursor:pointer }
button.copy.ok{ background:var(--ok-soft); border-color:var(--ok); color:var(--ok) }
.state{ font-size:14px; color:var(--ok) }
details{ border-top:1px solid var(--line); padding-top:10px }
summary{ cursor:pointer; font-size:14.5px; color:var(--accent-ink) }
pre{ margin:10px 0 0; padding:12px; background:var(--bg); border-radius:10px; font-family:var(--mono); font-size:13.5px; line-height:1.65; white-space:pre-wrap; overflow-wrap:anywhere; max-width:100% }
.note{ font-size:14.5px }
.note b{ font-weight:600; margin-right:6px }
.tick{ display:inline-flex; align-items:center; gap:8px; font-size:14.5px; cursor:pointer; padding:4px 0 }
.tick input{ width:20px; height:20px; accent-color:var(--ok) }

.pairs{ display:flex; flex-direction:column; gap:0 }
.pair{ display:flex; flex-direction:column; gap:2px; padding:10px 0; border-bottom:1px solid var(--line) }
.pair:last-child{ border-bottom:0 }
.pair .tagline{ font-size:12.5px; color:var(--accent-ink) }
.pair .en{ font-family:var(--mono); font-size:14.5px; overflow-wrap:anywhere }
.pair .zh{ font-size:14.5px; color:var(--muted) }
.scroll{ overflow-x:auto; max-width:100% }
table{ border-collapse:collapse; width:100%; font-size:14.5px; font-variant-numeric:tabular-nums }
th,td{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top }
th{ font-weight:600; color:var(--muted); font-size:13px }
td.n{ font-family:var(--mono); white-space:nowrap }
'''

JS = r'''
(function(){
  var KEY = 'balance-shotlist-v1';
  function load(){ try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; } }
  function save(o){ try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  var st = load();
  var boxes = Array.prototype.slice.call(document.querySelectorAll('input[data-seg]'));
  function paint(){
    var n = 0;
    boxes.forEach(function(b){
      var on = !!st[b.getAttribute('data-seg')]; b.checked = on;
      var card = b.closest('.card'); if (card) card.classList.toggle('is-done', on);
      if (on) n++;
    });
    var out = document.getElementById('done-n'); if (out) out.textContent = n;
    var bar = document.getElementById('done-bar'); if (bar) bar.style.width = (boxes.length ? n / boxes.length * 100 : 0) + '%';
  }
  boxes.forEach(function(b){ b.addEventListener('change', function(){ st[b.getAttribute('data-seg')] = b.checked; save(st); paint(); }); });
  paint();
  document.addEventListener('click', function(ev){
    var btn = ev.target.closest ? ev.target.closest('button.copy') : null; if (!btn) return;
    var pre = document.getElementById(btn.getAttribute('data-target')); if (!pre) return;
    var state = btn.parentNode.querySelector('.state'); var text = pre.textContent;
    function ok(){ btn.classList.add('ok'); if (state) state.textContent = '已复制'; setTimeout(function(){ btn.classList.remove('ok'); if (state) state.textContent = ''; }, 2200); }
    function fallback(){
      var d = pre.closest('details'); if (d) d.open = true;
      try { var r = document.createRange(); r.selectNodeContents(pre); var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); } catch (e) {}
      if (state) state.textContent = '已选中全文，请长按选"拷贝"';
      try { pre.scrollIntoView({block: 'center'}); } catch (e) {}
    }
    try { if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text).then(ok, fallback); } else { fallback(); } } catch (e) { fallback(); }
  });
})();
'''

def copyblock(pid, text, label='复制提示词', summary='看提示词全文'):
    return ('<div class="copyrow"><button type="button" class="copy" id="btn-%s" data-target="%s">%s</button><span class="state" aria-live="polite"></span></div>'
            '<details><summary>%s</summary><pre id="%s">%s</pre></details>') % (pid, pid, E(label), E(summary), pid, E(text))

def seg_card(s):
    kind, _ = s['model']
    tags = ['<span class="tag %s">%s</span>' % ('m25' if kind == '2.5' else '', 'Seedance 2.5' if kind == '2.5' else '2.0 Fast'),
            '<span class="tag plain">%d 秒</span>' % s['dur']]
    if s['pilot']: tags.append('<span class="tag star">先拍</span>')
    where = '、'.join('%s–%s' % (mmss(a), mmss(b)) for a, b in USED[s['id']])
    says = ''
    if s['lines']:
        says = '<div class="says">' + ''.join('<div class="say"><div class="en"><span class="who">%s</span>%s</div><div class="zh">%s</div></div>' % (E(D.LINES[n][0]), E(D.LINES[n][1]), E(D.LINES[n][2])) for n in s['lines']) + '</div>'
    refs = '<div class="refs"><span class="lbl">按这个顺序上传参考图</span><ol>' + ''.join('<li>%s</li>' % E(r) for r in s['refs']) + '</ol></div>'
    return ('<article class="card" id="s%s"><div class="head"><h3><span class="no">%s</span>%s</h3><div class="tags">%s</div></div>'
            '<p class="where">成片位置 %s · 约占一周额度 %.2f%%</p>%s%s%s'
            '<p class="note"><b>后期由 Claude 加</b>%s</p><p class="note"><b>发出去之前看一眼</b>%s</p>'
            '<label class="tick"><input type="checkbox" id="done-%s" data-seg="%s"><span>这段已通过</span></label></article>') % (
            s['id'], s['id'], E(s['name']), ''.join(tags), where, D.cost(s), says, refs, copyblock('p-' + s['id'], D.prompt(s)), E(s['post']), E(s['look']), s['id'], s['id'])

parts = []
parts.append('<title>《余额》镜头表</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>' + CSS + '</style>\n<div class="wrap">')
parts.append('''<header class="ticket">
<div class="brand">BALANCE · SHOT LIST</div>
<h1>《余额》镜头表</h1>
<div class="rows">
<div class="row"><span class="k">成片</span><span class="dots"></span><span class="v">约 %s</span></div>
<div class="row"><span class="k">要生成</span><span class="dots"></span><span class="v">%d 段</span></div>
<div class="row"><span class="k">Seedance 2.5</span><span class="dots"></span><span class="v">%d 段</span></div>
<div class="row"><span class="k">Seedance 2.0 Fast</span><span class="dots"></span><span class="v">%d 段</span></div>
<div class="row"><span class="k">配音</span><span class="dots"></span><span class="v">英文</span></div>
<div class="row"><span class="k">字幕和画面里的字</span><span class="dots"></span><span class="v">后期加，英中双语</span></div>
<div class="row"><span class="k">每段只拍一遍的额度</span><span class="dots"></span><span class="v">%.1f%%</span></div>
</div>
<div class="meter"><div class="label">已通过 <b id="done-n">0</b> / %d 段</div><div class="track"><i id="done-bar"></i></div></div>
</header>''' % ('%d 分 %d 秒' % divmod(int(round(TOTAL / 5.0) * 5), 60), len(D.SEGS), n25, nf, tot, len(D.SEGS)))
parts.append('<nav aria-label="目录"><a href="#prep">先补三张图</a><a href="#shots">19 段提示词</a><a href="#text">画面里的字</a><a href="#lines">台词</a><a href="#music">配乐</a><a href="#budget">额度</a><a href="#send">怎么发文件</a></nav>')
parts.append('''<section><h2>怎么用</h2>
<ol class="steps">
<li>先在 ChatGPT 里补三张图，见下一节。</li>
<li>在豆包里新开一条消息，按卡片上的顺序上传参考图，点"复制提示词"粘进去发送。</li>
<li>生成完把视频原文件发给 Claude。通过了，回这页把那一段勾上。</li>
</ol>
<p class="sub">每段提示词都写了"不要背景音乐、不要字幕、不要文字"。音乐、字幕和小票上的字都在后期统一加。</p></section>''')
parts.append('''<section><h2>和剧本初稿不一样的四处</h2>
<ul class="plain">
<li>开场不再用手指点屏幕上的"是"，改成按那个淡紫色的实体大按键。</li>
<li>黑猫的胸牌不写"夜班"，是一张带月牙图标的工牌。</li>
<li>尾声里猫不推泡面了，改成它自己用爪子按按键，机器吐出泡面的账单。泡面在收银机另一侧，猫够不着；按键这个动作全片出现三次，正好收尾。</li>
<li>台词是英文，小票和屏幕上的字是英中双语。</li>
</ul></section>''')
parts.append('<section id="prep"><h2>先补三张图</h2><p class="sub">在生成定妆图的那个 ChatGPT 对话里接着发。发的时候带上道具图、柜台图、阿哲设定图和合成定妆照。</p>')
for tag, name, why, pr in D.PLATES:
    pid = 'plate-' + tag[-1]
    parts.append('<article class="card"><div class="head"><h3><span class="no">%s</span>%s</h3></div><p class="note">%s</p>%s</article>' % (E(tag), E(name), E(why), copyblock(pid, pr)))
parts.append('</section>')
parts.append('<section><h2>先拍这 4 段</h2><p class="sub">它们分别验证四件事：双人对话、近景表演、猫推杯子、打电话。这 4 段过了，其余 15 段就是照着做。4 段只拍一遍约占一周额度的 %.1f%%。</p><ul class="plain">%s</ul></section>' % (
    sum(D.cost(s) for s in pilot), ''.join('<li><a href="#s%s">第 %s 段 · %s</a></li>' % (s['id'], s['id'], E(s['name'])) for s in pilot)))
parts.append('<section id="shots"><h2>19 段提示词</h2><p class="sub">阿哲有台词或表情变化的段用 Seedance 2.5，其余用 2.0 Fast。时长和模型都写在提示词第一行里了。</p>')
cur = None
for s in D.SEGS:
    if s['act'] != cur:
        cur = s['act']; parts.append('<div class="act"><h3>%s</h3></div>' % E(ACTS[cur]))
    parts.append(seg_card(s))
parts.append('</section>')
parts.append('<section id="text"><h2>画面里的字</h2><p class="sub">这些字 Seedance 不生成，由 Claude 后期加到空白的屏幕和小票上，数字放大。</p><div class="card"><div class="pairs">')
for name, en, zh in D.TEXTS:
    at = INS_AT.get(name)
    parts.append('<div class="pair"><div class="tagline">%s%s</div><div class="en">%s</div><div class="zh">%s</div></div>' % (E(name), (' · ' + mmss(at[0])) if at else ' · 0:00', E(en), E(zh)))
parts.append('</div></div><p class="sub">小票 7 里的 21 年出自联合国《世界人口展望 2024》的中国生命表：60 岁时平均余寿约 21 年，是男女合计的数字。</p></section>')
parts.append('<section id="lines"><h2>台词</h2><p class="sub">英文是配音，中文是字幕。字幕英文小、在上，中文大、在下。</p><div class="card"><div class="pairs">')
for n in range(1, 16):
    who, en, zh = D.LINES[n]
    seg = next(s['id'] for s in D.SEGS if n in s['lines'])
    parts.append('<div class="pair"><div class="tagline">%d · %s · 第 %s 段</div><div class="en">%s</div><div class="zh">%s</div></div>' % (n, E(who), seg, E(en), E(zh)))
parts.append('</div></div></section>')
parts.append('''<section id="music"><h2>配乐</h2>
<ul class="plain">
<li>0:00 到 %s 不放音乐，只有便利店的环境声。</li>
<li>%s "剩余 21 次"那张小票出来时，钢琴进一个长音。</li>
<li>打电话中间那两秒停顿，音乐停。</li>
<li>妈妈说"买排骨"时主题进来，数字滚到 252 时推到最高，之后回到钢琴独奏，在片尾卡上收住。</li>
</ul>
<p class="sub">用你手上的 AI 音乐工具生成两三条纯音乐，挑你听着最对的发给 Claude，按画面剪进去。中文工具用第一段，英文工具用第二段。</p>''' % (mmss(INS_AT['小票 6'][0]), mmss(INS_AT['小票 6'][0])))
parts.append('<article class="card"><div class="head"><h3>音乐提示词（中文）</h3></div>%s</article>' % copyblock('music-zh', D.MUSIC_ZH, '复制', '看全文'))
parts.append('<article class="card"><div class="head"><h3>音乐提示词（英文）</h3></div>%s</article>' % copyblock('music-en', D.MUSIC_EN, '复制', '看全文'))
parts.append('</section>')
parts.append('''<section id="budget"><h2>额度</h2>
<p class="sub">按 11 月 14 日实测：10 秒的 Seedance 2.5 占一周额度 1.92%%，2.0 Fast 占 1.16%%。5 秒的段按一半估，这一点还没实测。</p>
<div class="card"><div class="scroll"><table>
<thead><tr><th>范围</th><th>只拍一遍</th><th>平均拍 2.5 遍</th></tr></thead>
<tbody>
<tr><td>第 01–11 段（开场到转折）</td><td class="n">%.1f%%</td><td class="n">%.0f%%</td></tr>
<tr><td>第 12–19 段（高潮和尾声）</td><td class="n">%.1f%%</td><td class="n">%.0f%%</td></tr>
<tr><td>全片</td><td class="n">%.1f%%</td><td class="n">%.0f%%</td></tr>
</tbody></table></div></div>
<p class="sub">提示词里现在都写的是 720p。想要 1080p，先把第 02 段用 1080p 拍一遍，看额度涨多少再定。</p>
<p class="sub">建议分两周拍：11 月 18 日 09:07 额度重置前拍第 01–11 段，重置后拍第 12–19 段。重置那天赠送套餐到期，后半部同样的量会贵两成左右，这是按套餐倍数推算的。</p></section>''' % (w1, w1 * 2.5, w2, w2 * 2.5, tot, tot * 2.5))
parts.append('''<section id="send"><h2>怎么把文件发给 Claude</h2>
<ul class="plain">
<li>从豆包下载视频后，先存到"文件"App，再当文件发。走相册会被压缩，三条样片都只剩 0.5 MB 左右。</li>
<li>一段拍了几遍，就把你觉得最好的那一遍发来，并说一句是第几段。</li>
<li>Claude 听不到声音。台词有没有说对、镜头有没有动可以测出来，嗓音好不好听要靠你判断。</li>
</ul></section>''')
parts.append('</div>\n<script>' + JS + '</script>\n')
out = '\n'.join(parts)
open(sys.argv[1], 'w', encoding='utf-8').write(out)
print('wrote', sys.argv[1], len(out.encode('utf-8')), 'bytes')
