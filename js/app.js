(function () {
  'use strict';
  const C = window.Chart, $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  function el(n, a, t) { const e = document.createElementNS(NS, n); for (const k in a) if (a[k] != null) e.setAttribute(k, a[k]); if (t != null) e.textContent = t; return e; }
  function rnd(seed) { const x = Math.sin(seed * 127.1) * 43758.5453; return x - Math.floor(x); }
  function corr(pts) {
    const n = pts.length;
    if (n < 3) return NaN;
    const mx = pts.reduce((a, p) => a + p[0], 0) / n, my = pts.reduce((a, p) => a + p[1], 0) / n;
    let sxy = 0, sxx = 0, syy = 0;
    pts.forEach(p => { sxy += (p[0] - mx) * (p[1] - my); sxx += (p[0] - mx) ** 2; syy += (p[1] - my) ** 2; });
    return (sxx && syy) ? sxy / Math.sqrt(sxx * syy) : 0;
  }

  /* ---------- 事例データ ---------- */
  const CASES = [
    { title: 'アイスの売上と水難事故の件数（日別・90日）',
      xLabel: 'アイスの売上（万円）', yLabel: '水難事故の件数',
      lurk: '気温', lurkUnit: '℃', lurkMin: 8, lurkMax: 34,
      why: '暑い日はアイスがよく売れ、同時に海や川へ行く人も増えて事故も増えます。アイスを買うことが事故を起こすわけではありません。',
      mk: (t, i) => [Math.round(15 + t * 2.6 + (rnd(i) - .5) * 12), Math.round(Math.max(0, 0.4 * t - 3 + (rnd(i + 99) - .5) * 3.4))]
    },
    { title: '出動した消防車の台数と火災の被害額（100件）',
      xLabel: '消防車の台数（台）', yLabel: '被害額（万円）',
      lurk: '火災の規模', lurkUnit: '', lurkMin: 1, lurkMax: 10,
      why: '火事が大きいから消防車がたくさん来るのであって、消防車が被害を大きくしているのではありません。原因と結果が逆に見えている例です。',
      mk: (t, i) => [Math.round(1 + t * 1.2 + (rnd(i) - .5) * 2.2), Math.round(30 + t * 95 + (rnd(i + 55) - .5) * 130)]
    },
    { title: '小学生の足の大きさと漢字テストの点数（120人）',
      xLabel: '足の大きさ（cm）', yLabel: '漢字テストの点数',
      lurk: '学年', lurkUnit: '年', lurkMin: 1, lurkMax: 6,
      why: '学年が上がれば体も大きくなり、習った漢字も増えます。足が大きいから漢字が書けるわけではありません。',
      mk: (t, i) => [Math.round((17 + t * 1.5 + (rnd(i) - .5) * 1.8) * 10) / 10, Math.round(Math.min(100, 38 + t * 8 + (rnd(i + 77) - .5) * 16))]
    }
  ];
  let ci = 0, dataset = [];

  function buildData(k) {
    const c = CASES[k], out = [];
    const n = 90;
    for (let i = 0; i < n; i++) {
      const t = c.lurkMin + rnd(i * 3.7 + k * 11) * (c.lurkMax - c.lurkMin);
      const [x, y] = c.mk(t, i * 5 + k * 100);
      out.push({ x, y, t });
    }
    return out;
  }
  function bandColor(t, c) {
    const p = (t - c.lurkMin) / (c.lurkMax - c.lurkMin);
    const pal = ['#0f6a78', '#1f7a3d', '#8a5a00', '#8a2f1f', '#b3261e'];
    return pal[Math.min(pal.length - 1, Math.floor(p * pal.length))];
  }

  function showCase(k) {
    ci = k;
    const c = CASES[k];
    document.querySelectorAll('[data-case]').forEach(b => b.setAttribute('aria-pressed', +b.dataset.case === k));
    dataset = buildData(k);
    $('caseTitle').textContent = c.title;
    const pts = dataset.map(d => [d.x, d.y]);
    C.scatter($('caseChart'), { W: 440, H: 310, points: pts, xLabel: c.xLabel, yLabel: c.yLabel, regression: true });
    const r = corr(pts);
    $('caseR').textContent = (r >= 0 ? '+' : '') + r.toFixed(3);
    $('caseWhy').textContent = c.why;
    $('caseLegend').innerHTML = '';
    $('lurkName').textContent = c.lurk;
    $('rAll').textContent = (r >= 0 ? '+' : '') + r.toFixed(3);
    drawDiagram();
    drawStrat();
  }

  /* ---------- STEP2 層別 ---------- */
  function drawStrat() {
    const c = CASES[ci];
    const w = +$('strat').value;                       // 1〜10（10＝全部）
    const span = (c.lurkMax - c.lurkMin) * w / 10;
    const center = (c.lurkMin + c.lurkMax) / 2;
    const lo = center - span / 2, hi = center + span / 2;
    $('stratV').textContent = w === 10 ? '全部（そろえない）'
      : c.lurk + ' ' + lo.toFixed(1) + c.lurkUnit + ' 〜 ' + hi.toFixed(1) + c.lurkUnit;
    const sel = dataset.filter(d => d.t >= lo && d.t <= hi);
    const pts = sel.map(d => [d.x, d.y]);
    const all = dataset.map(d => [d.x, d.y]);
    const xs = all.map(p => p[0]), ys = all.map(p => p[1]);
    C.scatter($('stratChart'), { W: 440, H: 310, points: pts,
      xMin: Math.min(...xs), xMax: Math.max(...xs), yMin: Math.min(...ys), yMax: Math.max(...ys),
      xLabel: c.xLabel, yLabel: c.yLabel, regression: pts.length > 2,
      colors: sel.map(d => bandColor(d.t, c)) });
    $('stratLegend').innerHTML = '点の色は' + c.lurk + 'の高さ（' +
      ['低', 'やや低', '中', 'やや高', '高'].map((l, i) =>
        '<span><i style="background:' + ['#0f6a78', '#1f7a3d', '#8a5a00', '#8a2f1f', '#b3261e'][i] + '"></i>' + l + '</span>').join('') + '）';
    const rs = corr(pts);
    $('rStrat').textContent = isNaN(rs) ? '—' : (rs >= 0 ? '+' : '') + rs.toFixed(3);
    $('nStrat').textContent = sel.length;
    const rAll = corr(all);
    const n = $('stratNote');
    if (w === 10) {
      n.className = 'note warn';
      n.innerHTML = 'いまは全部のデータを見ています。相関係数は <strong>' + rAll.toFixed(3) +
        '</strong> と高く、関係があるように見えます。スライダーを左へ動かして、' + c.lurk + 'が近いものだけを取り出してください。';
    } else if (Math.abs(rs) < Math.abs(rAll) * 0.52) {
      n.className = 'note ok';
      n.innerHTML = c.lurk + 'をそろえたら、相関係数が <strong>' + rAll.toFixed(3) + ' → ' + rs.toFixed(3) +
        '</strong> まで小さくなりました。<strong>2つの間に直接の関係はほとんどなく、' + c.lurk +
        'が両方を動かしていた</strong>ということです。これが擬似相関（見せかけの相関）です。';
    } else {
      n.className = 'note info';
      n.innerHTML = 'まだ範囲が広いので相関が残っています（' + rs.toFixed(3) + '）。もっと' + c.lurk + 'をそろえてみましょう。';
    }
  }

  function drawDiagram() {
    const c = CASES[ci];
    const box = $('diagram'); box.innerHTML = '';
    const W = 560, H = 190;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: '100%', role: 'img', 'aria-label': '交絡の関係図' });
    const boxes = [
      { x: W / 2 - 70, y: 14, w: 140, h: 44, t: c.lurk, sub: '（かくれた原因）', col: '#8a5a00' },
      { x: 30, y: 120, w: 190, h: 46, t: c.xLabel, sub: '', col: '#123a6b' },
      { x: W - 220, y: 120, w: 190, h: 46, t: c.yLabel, sub: '', col: '#123a6b' }
    ];
    const defs = el('defs'); const mk = el('marker', { id: 'ah', markerWidth: 8, markerHeight: 8, refX: 7, refY: 3, orient: 'auto' });
    mk.appendChild(el('path', { d: 'M0,0 L7,3 L0,6 Z', fill: '#8a5a00' })); defs.appendChild(mk); svg.appendChild(defs);
    svg.appendChild(el('line', { x1: W / 2 - 30, y1: 60, x2: 140, y2: 116, stroke: '#8a5a00', 'stroke-width': 2.2, 'marker-end': 'url(#ah)' }));
    svg.appendChild(el('line', { x1: W / 2 + 30, y1: 60, x2: W - 140, y2: 116, stroke: '#8a5a00', 'stroke-width': 2.2, 'marker-end': 'url(#ah)' }));
    svg.appendChild(el('line', { x1: 222, y1: 143, x2: W - 224, y2: 143, stroke: '#b3261e', 'stroke-width': 1.6, 'stroke-dasharray': '6 4' }));
    svg.appendChild(el('text', { x: W / 2, y: 136, 'text-anchor': 'middle', 'font-size': 11, fill: '#b3261e' }, '直接の因果はない'));
    svg.appendChild(el('text', { x: W / 2, y: 158, 'text-anchor': 'middle', 'font-size': 11, fill: '#b3261e' }, '（相関だけが見える）'));
    boxes.forEach(b => {
      svg.appendChild(el('rect', { x: b.x, y: b.y, width: b.w, height: b.h, fill: '#fff', stroke: b.col, 'stroke-width': 1.8 }));
      svg.appendChild(el('text', { x: b.x + b.w / 2, y: b.y + (b.sub ? 18 : b.h / 2), 'text-anchor': 'middle',
        'dominant-baseline': 'middle', 'font-size': 13, 'font-weight': 700, fill: '#15181c' }, b.t));
      if (b.sub) svg.appendChild(el('text', { x: b.x + b.w / 2, y: b.y + 33, 'text-anchor': 'middle',
        'font-size': 10, fill: '#4a4f57' }, b.sub));
    });
    box.appendChild(svg);
  }

  /* ---------- STEP3 パターン分類 ---------- */
  const PATS = [
    { t: '朝食を食べる生徒は成績がよい傾向がある。', a: '① 交絡（第3の変数）',
      why: '生活習慣が整っている家庭では、朝食も食べるし勉強時間も確保されやすい。家庭環境や生活習慣が両方に効いています。' },
    { t: '病院の医師数が多い地域ほど、病人の数が多い。', a: '② 逆の因果',
      why: '病人が多い地域だから医師が多く配置されるのです。医師が病人を増やしているわけではありません。' },
    { t: 'ある年、日本のアニメ映画の興行収入と、ある国の輸出額が同じように増えた。', a: '③ 偶然',
      why: '互いにまったく関係のない指標が、たまたま似た動きをしただけです。データの期間が短いときに起こりやすい現象です。' },
    { t: '身長が高い小学生ほど計算が速い。', a: '① 交絡（第3の変数）',
      why: '学年（年齢）が両方に効いています。同じ学年の中で比べれば関係はほとんど消えます。' },
    { t: '救急車の到着が早いほど、患者の回復率が低いというデータが出た。', a: '② 逆の因果',
      why: '重症の患者ほど優先的に救急車が早く向かいます。重症度が結果を悪くしているのであって、早く着いたことが原因ではありません。' },
    { t: 'アイスの売上が多い日は水難事故も多い。', a: '① 交絡（第3の変数）',
      why: '気温が両方に効いています。STEP 2 で確かめたとおりです。' },
    { t: '靴のサイズが大きい人ほど年収が高いというデータが出た（成人男女混合）。', a: '① 交絡（第3の変数）',
      why: '性別や年齢が両方に関係しています。男女や年齢をそろえて比べると関係は薄くなります。' }
  ];
  const PCHOICES = ['① 交絡（第3の変数）', '② 逆の因果', '③ 偶然'];
  let pList = [], pi = 0, pScore = 0;
  const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  function startP() { pList = shuffle(PATS); pi = 0; pScore = 0; renderP(); }
  function renderP() {
    if (pi >= pList.length) {
      $('pText').textContent = pScore + ' / ' + pList.length + ' 問正解';
      $('pChoices').innerHTML = ''; $('pFb').hidden = true; $('pNext').disabled = true;
      $('pProgress').textContent = pList.length + ' / ' + pList.length; return;
    }
    $('pProgress').textContent = (pi + 1) + ' / ' + pList.length;
    $('pScore').textContent = pScore;
    $('pText').textContent = pList[pi].t;
    const box = $('pChoices'); box.className = 'choice4'; box.innerHTML = '';
    PCHOICES.forEach(c => {
      const b = document.createElement('button');
      b.className = 'btn'; b.textContent = c; b.dataset.c = c;
      b.addEventListener('click', () => answerP(c));
      box.appendChild(b);
    });
    $('pFb').hidden = true; $('pNext').disabled = true;
    $('pNext').textContent = (pi === pList.length - 1) ? '結果を見る' : '次の問題';
  }
  function answerP(c) {
    const it = pList[pi], ok = c === it.a, box = $('pChoices');
    box.classList.add('locked');
    [...box.children].forEach(b => {
      if (b.dataset.c === it.a) b.classList.add('correct');
      else if (b.dataset.c === c) b.classList.add('wrong');
    });
    if (ok) pScore++;
    const fb = $('pFb');
    fb.className = 'note ' + (ok ? 'ok' : 'ng');
    fb.innerHTML = (ok ? '正解。' : '正解は <strong>' + it.a + '</strong>。') + it.why;
    fb.hidden = false;
    $('pScore').textContent = pScore; $('pNext').disabled = false;
  }

  /* ---------- STEP4 主張の判定 ---------- */
  const JUDGES = [
    { t: '調査した90日間では、アイスの売上と水難事故の件数に強い正の相関があった。', ok: true,
      why: 'データから読み取れる事実そのものです。相関の有無を述べるのは適切です。' },
    { t: 'アイスの販売を減らせば、水難事故を減らせる。', ok: false,
      why: '相関があるだけで、原因と結果の関係は示されていません。両方に効いているのは気温です。' },
    { t: 'アイスの売上と水難事故には、気温という共通の原因が考えられる。', ok: true,
      why: '交絡の可能性を指摘しているだけなので適切です。実際に気温をそろえると相関は消えました。' },
    { t: '消防車を減らせば火災の被害額を減らせる。', ok: false,
      why: '原因と結果が逆です。火災が大きいから消防車が多く出動します。' },
    { t: '相関係数が 0.9 と非常に高いので、因果関係があると結論できる。', ok: false,
      why: '相関係数がどれだけ高くても、それだけでは因果関係の証拠になりません。相関の強さと因果の有無は別の話です。' },
    { t: 'ランダムに2グループに分けて片方だけに新しい教材を使わせ、点数の差を比べた。この差は教材の効果と考えてよい。', ok: true,
      why: 'くじ引きで分けているので、他の条件の差は両グループに均等に散らばります。因果を確かめる標準的な方法です。' },
    { t: '同じ学年の中で比べたら、足の大きさと漢字テストの点数の相関はほとんどなくなった。だから学年が交絡変数だったと考えられる。', ok: true,
      why: '交絡変数をそろえたら相関が消えた、という筋道は正しい推論です。' }
  ];
  let jList = [], ji = 0, jScore = 0;
  function startJ() { jList = shuffle(JUDGES); ji = 0; jScore = 0; renderJ(); }
  function renderJ() {
    if (ji >= jList.length) {
      $('jText').textContent = jScore + ' / ' + jList.length + ' 問正解';
      $('jFb').hidden = true; $('jNext').disabled = true;
      $('jOk').disabled = $('jNg').disabled = true;
      $('jProgress').textContent = jList.length + ' / ' + jList.length; return;
    }
    $('jProgress').textContent = (ji + 1) + ' / ' + jList.length;
    $('jScore').textContent = jScore;
    $('jText').textContent = jList[ji].t;
    $('jOk').disabled = $('jNg').disabled = false;
    $('jOk').className = $('jNg').className = 'btn';
    $('jFb').hidden = true; $('jNext').disabled = true;
    $('jNext').textContent = (ji === jList.length - 1) ? '結果を見る' : '次の問題';
  }
  function answerJ(v) {
    const it = jList[ji], ok = v === it.ok;
    if (ok) jScore++;
    $('jOk').disabled = $('jNg').disabled = true;
    (it.ok ? $('jOk') : $('jNg')).classList.add('correct');
    if (!ok) (v ? $('jOk') : $('jNg')).classList.add('wrong');
    const fb = $('jFb');
    fb.className = 'note ' + (ok ? 'ok' : 'ng');
    fb.innerHTML = (ok ? '正解。' : 'ちがいます。') + it.why;
    fb.hidden = false;
    $('jScore').textContent = jScore; $('jNext').disabled = false;
  }

  /* ---------- STEP5 ランダム化 ---------- */
  let trial = null;
  function runTrial() {
    // 40人。半分は「もともと勉強が得意」という隠れた特性を持つ
    const people = [];
    for (let i = 0; i < 40; i++) people.push({ hidden: Math.random() < .5, g: Math.random() < .5 ? 0 : 1 });
    const g0 = people.filter(p => p.g === 0), g1 = people.filter(p => p.g === 1);
    trial = { g0: g0.length, g1: g1.length,
              h0: g0.filter(p => p.hidden).length, h1: g1.filter(p => p.hidden).length };
    drawTrial();
  }
  function drawTrial() {
    if (!trial) {
      $('trialChart').innerHTML = '';
      $('trialNote').className = 'note info';
      $('trialNote').textContent = 'ボタンを押すと、40人をくじ引きで2つのグループに分けます。かくれた特性（もともと勉強が得意かどうか）が、どのように分かれるか見てください。';
      return;
    }
    C.bar($('trialChart'), { W: 560, H: 250,
      labels: ['Aグループ 人数', 'Aのうち得意な人', 'Bグループ 人数', 'Bのうち得意な人'],
      values: [trial.g0, trial.h0, trial.g1, trial.h1],
      colors: ['#123a6b', '#8a5a00', '#123a6b', '#8a5a00'], unit: '人', rotate: true });
    const p0 = trial.g0 ? trial.h0 / trial.g0 * 100 : 0, p1 = trial.g1 ? trial.h1 / trial.g1 * 100 : 0;
    const n = $('trialNote');
    n.className = Math.abs(p0 - p1) < 20 ? 'note ok' : 'note warn';
    n.innerHTML = 'かくれた特性をもつ人の割合は A ' + p0.toFixed(0) + '％、B ' + p1.toFixed(0) + '％。' +
      (Math.abs(p0 - p1) < 20
        ? '<strong>くじ引きで分けただけなのに、両グループにほぼ均等に散らばりました。</strong>だから後で差が出れば、それは調べたい要因の効果だと考えられます。'
        : '今回はやや偏りました。<strong>人数が少ないと偏ることがあります。</strong>何度か押して、人数が多いほど安定することを確かめてください。');
  }

  function init() {
    document.querySelectorAll('[data-case]').forEach(b => b.addEventListener('click', () => showCase(+b.dataset.case)));
    $('strat').addEventListener('input', drawStrat);
    $('pNext').addEventListener('click', () => { pi++; renderP(); });
    $('pReset').addEventListener('click', startP);
    $('jOk').addEventListener('click', () => answerJ(true));
    $('jNg').addEventListener('click', () => answerJ(false));
    $('jNext').addEventListener('click', () => { ji++; renderJ(); });
    $('jReset').addEventListener('click', startJ);
    $('runTrial').addEventListener('click', runTrial);
    $('resetTrial').addEventListener('click', () => { trial = null; drawTrial(); });
    showCase(0); startP(); startJ(); drawTrial();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
