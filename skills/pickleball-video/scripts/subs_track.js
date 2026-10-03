// Render subtitles as one transparent video track (this ffmpeg build has no libass/drawtext, so text is drawn by Chromium).
// usage: NODE_PATH=motion/node_modules node subs_track.js cues.json subs.mov [fps=30000/1001]
// cues.json = [[start, end, "text"], ...] in seconds on the target timeline. Style matches the motion-broll clips (Geist).
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path'); const os=require('os'); const {execFileSync}=require('child_process');
(async()=>{
 const [cuesPath,out,fps='30000/1001']=process.argv.slice(2);
 const cues=JSON.parse(fs.readFileSync(cuesPath,'utf8'));
 const font=fs.readFileSync(path.join(__dirname,'../assets/Geist-Variable.woff2')).toString('base64');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'subs'));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080}});
 await p.setContent(`<html><head><style>@font-face{font-family:G;src:url(data:font/woff2;base64,${font}) format('woff2');font-weight:100 900}
  html,body{margin:0;background:transparent;width:1920px;height:1080px}
  #s{position:absolute;left:0;right:0;margin:0 auto;width:fit-content;max-width:1700px;bottom:46px;text-align:center;font-family:G;font-size:46px;font-weight:600;letter-spacing:-.01em;line-height:1.25;color:#fff;background:rgba(11,11,11,.72);padding:12px 28px;border-radius:18px}</style></head><body><div id="s"></div></body></html>`);
 await p.evaluate(()=>document.fonts.ready);
 await p.evaluate(()=>{document.getElementById('s').style.display='none'});
 await p.screenshot({path:`${dir}/blank.png`,omitBackground:true});
 await p.evaluate(()=>{document.getElementById('s').style.display=''});
 const list=[]; let t=0;
 for(let i=0;i<cues.length;i++){ const [a,z,txt]=cues[i];
   await p.evaluate(s=>{document.getElementById('s').textContent=s},txt);
   const f=`c${String(i).padStart(4,'0')}.png`; await p.screenshot({path:`${dir}/${f}`,omitBackground:true});
   if(a>t) list.push(['blank.png',a-t]); list.push([f,Math.max(0.05,z-Math.max(a,t))]); t=Math.max(t,z); }
 list.push(['blank.png',1],['blank.png',0]);
 fs.writeFileSync(`${dir}/list.txt`,list.map(([f,d])=>`file '${f}'`+(d?`\nduration ${d.toFixed(3)}`:'')).join('\n')+'\n');
 await b.close();
 execFileSync('ffmpeg',['-loglevel','error','-y','-f','concat','-safe','0','-i',`${dir}/list.txt`,'-vf',`fps=${fps},format=rgba`,'-c:v','qtrle',out],{stdio:'inherit'});
 fs.rmSync(dir,{recursive:true,force:true});
 console.log('wrote',out,'('+cues.length+' cues)');
})();
