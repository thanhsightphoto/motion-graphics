// Instagram cover: a video frame with the clip's card style on top. Square 1080x1080 by default; for a Reels cover use
// "width":1080,"height":1920 (the profile grid shows only the middle 3:4, so cardTop/rulesBottom default to ~250 there).
// usage: NODE_PATH=motion/node_modules node cover.js cover.json
// cover.json: {"frame":"inputs/cover_frame.png","out":"out/cover_instagram_1080.png","chip":"Pickleball · Dink drill",
//              "title":"The twoey dink","subtitle":"Read the spin before you lift",
//              "rules":[{"tag":"No spin","text":"Slightly closed · forward"},{"tag":"Heavy slice","text":"Open · straight up","accent":true}],
//              "titleSize":100, "width":1080, "height":1080, "cardTop":40, "rulesBottom":48}
// "layout":"stack" (tall covers): title card, then the frame in a rounded box (zoomed out: a wide crop showing both players),
// then the rules. "bg": an image to fill the whole canvas behind them, blurred and dimmed (e.g. a full-height 9:16 crop
// of the same moment) so a tall cover reads as 9:16, not a square on grey. Without "layout" the frame fills the background.
// Bleed layout: the frame should already be cropped to the canvas aspect; keep faces below the card. Stack layout: see
// SKILL.md step 6 (the default for Reels covers).
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{
 const cfgPath=process.argv[2]; const C=JSON.parse(fs.readFileSync(cfgPath,'utf8')); const base=path.dirname(path.resolve(cfgPath));
 const rel=f=>path.isAbsolute(f)?f:path.join(base,f);
 const b64=f=>fs.readFileSync(f).toString('base64');
 const geist=b64(path.join(__dirname,'../assets/Geist-Variable.woff2')), img=b64(rel(C.frame)), bgimg=C.bg?b64(rel(C.bg)):null;
 const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
 const W=C.width||1080, H=C.height||1080, tall=H/W>1.5;
 const cardTop=C.cardTop??(tall?260:40), rulesBottom=C.rulesBottom??(tall?270:48), stack=C.layout==='stack';
 const rules=(C.rules||[]).map(r=>`<div class="r"><span class="tag" style="${r.accent?'background:#FF5A1F;color:#fff':'background:#F1EFEB'}">${esc(r.tag)}</span>${esc(r.text)}</div>`).join('');
 const html=`<html><head><style>@font-face{font-family:G;src:url(data:font/woff2;base64,${geist}) format('woff2');font-weight:100 900}
 body{margin:0;width:${W}px;height:${H}px;position:relative;overflow:hidden;font-family:G;-webkit-font-smoothing:antialiased;color:#0B0B0B}
 .ph{position:absolute;inset:0;background:url(data:image/png;base64,${img}) center/cover}
 body.stack{background:#E9E7E2;display:flex;flex-direction:column;align-items:stretch;padding:${cardTop}px 44px 0;box-sizing:border-box;gap:40px}
 body.stack .card,body.stack .rules{position:static;width:auto}
 body.stack .ph{position:relative;inset:auto;aspect-ratio:${C.photoAspect||'1.27'};border-radius:40px;box-shadow:0 1px 2px rgba(20,18,14,.08),0 18px 40px -12px rgba(20,18,14,.3)}
 body.stack .rules{padding-left:4px}
 .bgf{position:absolute;inset:-60px;background:url(data:image/png;base64,${bgimg||img}) center/cover;filter:blur(36px) brightness(.72) saturate(1.1);z-index:-1}
 body.stack{position:relative;overflow:hidden}
 .card{position:absolute;left:44px;top:${cardTop}px;width:${W-88}px;box-sizing:border-box;padding:32px 44px 36px;background:#fff;border-radius:44px;box-shadow:0 1px 2px rgba(20,18,14,.08),0 18px 40px -12px rgba(20,18,14,.35)}
 .chip{display:inline-block;font-size:28px;font-weight:500;border-radius:999px;padding:8px 20px;background:#F1EFEB}
 h1{margin:14px 0 0;font-size:${C.titleSize||100}px;line-height:1;font-weight:650;letter-spacing:-.04em}
 .sub{margin-top:12px;font-size:36px;font-weight:500;color:#8A8782}
 .rules{position:absolute;left:48px;bottom:${rulesBottom}px;display:flex;flex-direction:column;gap:14px}
 .r{display:flex;align-items:center;gap:18px;background:#fff;border-radius:999px;padding:12px 30px 12px 12px;font-size:32px;font-weight:600;letter-spacing:-.01em;width:max-content;box-shadow:0 12px 30px -10px rgba(20,18,14,.35)}
 .tag{border-radius:999px;padding:10px 22px;font-size:26px;font-weight:600}
 </style></head><body class="${stack?'stack':''}">${stack?(bgimg?'<div class="bgf"></div>':''):'<div class="ph"></div>'}
 <div class="card">${C.chip?`<span class="chip">${esc(C.chip)}</span>`:''}<h1>${esc(C.title)}</h1>${C.subtitle?`<div class="sub">${esc(C.subtitle)}</div>`:''}</div>
 ${stack?'<div class="ph"></div>':''}<div class="rules">${rules}</div></body></html>`;
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:W,height:H}});
 await p.setContent(html); await p.evaluate(()=>document.fonts.ready);
 const cardBottom=await p.evaluate(()=>document.querySelector('.card').getBoundingClientRect().bottom);
 const rulesBottomY=await p.evaluate(()=>document.querySelector('.rules').getBoundingClientRect().bottom).catch(()=>0);
 await p.screenshot({path:rel(C.out)}); await b.close();
 console.log(`wrote ${rel(C.out)} (title card bottom at y=${Math.round(cardBottom)}; keep faces below it${stack?`; rules end at y=${Math.round(rulesBottomY)}, keep under ${Math.round(H/2+W*2/3)} for the 3:4 grid crop`:''})`);
})();
