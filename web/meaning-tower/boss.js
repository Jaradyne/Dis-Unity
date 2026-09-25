/* Local attention play. No network requests, inference, scoring, or evidence writes. */
(function () {
  'use strict';
  const HOLD_MS = 1900;
  const clone = value => JSON.parse(JSON.stringify(value));
  function canonical(value) {
    function sorted(v) {
      if (Array.isArray(v)) return v.map(sorted);
      if (v && typeof v === 'object') return Object.fromEntries(Object.keys(v).sort().map(k => [k, sorted(v[k])]));
      return v;
    }
    return JSON.stringify(sorted(value), null, 2) + '\n';
  }
  // Synchronous SHA-256 keeps the exported receipt usable in a downloaded file, too.
  function sha256(text) {
    const bytes = new TextEncoder().encode(text), n = bytes.length;
    const padded = new Uint8Array(Math.ceil((n + 9) / 64) * 64);
    padded.set(bytes); padded[n] = 128;
    const view = new DataView(padded.buffer);
    view.setUint32(padded.length - 8, Math.floor(n / 536870912));
    view.setUint32(padded.length - 4, (n * 8) >>> 0);
    const h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const k = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const r = (x, a) => (x >>> a) | (x << (32 - a)), w = new Uint32Array(64);
    for (let offset = 0; offset < padded.length; offset += 64) {
      for (let i = 0; i < 16; i++) w[i] = view.getUint32(offset + i * 4);
      for (let i = 16; i < 64; i++) {
        const a = w[i-15], b = w[i-2];
        w[i] = w[i-16] + (r(a,7)^r(a,18)^(a>>>3)) + w[i-7] + (r(b,17)^r(b,19)^(b>>>10));
      }
      let [a,b,c,d,e,f,g,j] = h;
      for (let i = 0; i < 64; i++) {
        const t = (j+(r(e,6)^r(e,11)^r(e,25))+((e&f)^(~e&g))+k[i]+w[i]) | 0;
        const u = ((r(a,2)^r(a,13)^r(a,22))+((a&b)^(a&c)^(b&c))) | 0;
        j=g;g=f;f=e;e=(d+t)|0;d=c;c=b;b=a;a=(t+u)|0;
      }
      [a,b,c,d,e,f,g,j].forEach((v,i) => { h[i] = (h[i]+v) >>> 0; });
    }
    return h.map(v => v.toString(16).padStart(8,'0')).join('');
  }
  const digest = value => sha256(canonical(value));

  class HoldSession {
    constructor(packet) { this.packet=packet; this.index=0; this.choices=[]; this.active=null; }
    get round() { return this.packet.rounds[this.index]; }
    get resolved() { return this.choices.length > this.index; }
    start(id, time, method) {
      this.cancel();
      if (this.resolved || !this.round.pieces.some(p => p.id === id)) return false;
      this.active={id, time, method}; return true;
    }
    cancel() { this.active=null; }
    progress(time) { return this.active ? Math.max(0, Math.min(HOLD_MS, time-this.active.time)) : 0; }
    tick(time) {
      if (!this.active || this.resolved || this.progress(time) < HOLD_MS) return null;
      const choice={round_id:this.round.id, preserved_id:this.active.id, held_ms:HOLD_MS, input_method:this.active.method};
      this.choices.push(choice); this.cancel(); return choice;
    }
    next() { if (!this.resolved || this.index+1 >= this.packet.rounds.length) return false; this.index++;return true; }
  }

  function makeDelivery(packet, result) {
    const resultHash=digest(result);
    return {schema_version:'governor-boss-input-1',kind:'governor_boss_input',delivery_id:'BOSS-'+resultHash.slice(0,24),
      packet_id:packet.packet_id,packet_sha256:digest(packet),play_id:result.play_id,result_sha256:resultHash,
      question_id:packet.question_id,epoch:packet.epoch,actor:clone(result.actor),completed_at:result.completed_at,
      input_origin:'client_report',human_identity_verified:false,
      validation_scope:'Structure, packet binding and choices; source truth and human identity are not verified by this validator.',
      route:{from:'PYGENT:PARALLAX-0001',to:'INIT:RETURN-0010',status:'resolved',automatic_execution:false},
      event_order:['attention_selection','power_application','governor_delivery'],applied_powers:[],power_status:'no_canonical_powers',
      power_candidate:clone(packet.power_candidate || null),selection_before_powers:clone(result.choices),selection_after_powers:clone(result.choices),
      rounds:packet.rounds.map((round,i) => ({round_id:round.id,kind:round.kind,title:round.title,prompt:round.prompt,context:round.context,
        originals:clone(round.originals),preserved:clone(round.pieces.find(p=>p.id===result.choices[i].preserved_id)),
        sunk:round.pieces.filter(p=>p.id!==result.choices[i].preserved_id).map(p=>({...clone(p),attention_status:'not_selected_not_false'}))})),
      source_ledger:clone(packet.source_ledger),comparison:clone(packet.comparison),cross:clone(packet.cross),
      evidence_changed:false,canonical_admission:false,
      evidence_treatment:'Preserved means selected for attention. Sunk means unselected, never false. Every original evidence status remains unchanged.'};
  }
  const api={HoldSession, makeDelivery, canonical, digest, sha256, HOLD_MS};
  if (typeof module !== 'undefined') module.exports=api;
  if (typeof document === 'undefined') return;

  const $=id=>document.getElementById(id);
  function element(tag, text, className) {
    const el=document.createElement(tag); if (text!==undefined) el.textContent=text; if(className) el.className=className; return el;
  }
  function fail(error) { $('fatalError').hidden=false; $('fatalError').textContent='The encounter could not be prepared: '+error.message; }
  try { boot(); } catch(error) { fail(error); }

  function boot() {
    const data=JSON.parse($('tower-data').textContent), packet=data.packet;
    if (digest(packet)!==data.packet_sha256 || data.approved_powers.length) throw new Error('Packet binding or proposed-power boundary does not match this build.');
    let session=new HoldSession(packet), bundle=null, delivered=false, memoryQueue=[];
    let storageReadable=true;
    const storageKey='meaning-tower-governor-inbox-v1';
    try { const saved=JSON.parse(localStorage.getItem(storageKey)||'[]'); if(!Array.isArray(saved)) throw new Error('Invalid inbox'); memoryQueue=saved; }
    catch (_) { storageReadable=false; }
    const media=window.matchMedia('(prefers-reduced-motion: reduce)');
    $('motionOff').checked=media.matches;
    function motion() { document.body.classList.toggle('still-waters',$('motionOff').checked); }
    motion(); $('motionOff').onchange=motion;
    $('assistMode').onchange=()=>{cancel();$('assistExplanation').hidden=!$('assistMode').checked;};
    $('seriesTitle').textContent=data.series.title;
    $('seriesNote').textContent='Governor curates · Jared can rearrange';
    data.series.slots.forEach((slot,i)=>{
      const li=element('li',undefined,slot.packet_id===packet.packet_id?'active':'');
      li.append(element('span',String(i+1).padStart(2,'0'),'slot-number'),element('span',slot.title,'slot-title'));
      $('seriesSlots').append(li);
    });
    $('packetMark').textContent=packet.packet_id;
    $('comparisonSummary').textContent=packet.comparison.summary;
    for (const [id,items] of [['ordinaryExplanations',packet.comparison.ordinary_explanations],['comparisonLimitations',packet.comparison.limitations]]) {
      items.forEach(text=>$ (id).append(element('li',text)));
    }
    packet.source_ledger.forEach(source=>{
      const row=element('div',undefined,'source-row'), link=element('a',source.title);
      link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';row.append(link);
      const dl=element('dl');
      for (const [label,value] of [['Language',source.language],['Published',source.publication_date||'Unknown'],['Observed event',source.observation_date||'No single measured event'],['Retrieved',source.retrieved_at]]) dl.append(element('dt',label),element('dd',value));
      row.append(dl,element('p',source.url));source.access_limitations.forEach(text=>row.append(element('p',text)));$('sources').append(row);
    });
    function inboxStatus() {
      $('inboxStatus').textContent=memoryQueue.length?memoryQueue.length+' completed encounter(s) kept in this browser. Nothing is sent to GitHub or an AI.':'Your completed encounter will appear here. Nothing is sent to GitHub or an AI.';
      $('restoreButton').hidden=!memoryQueue.length;
    }
    function cancel() {
      session.cancel(); document.querySelectorAll('.piece.holding').forEach(b=>b.classList.remove('holding'));
      if(!session.resolved) {$('holdFill').style.width='0%';$('holdTrack').setAttribute('aria-valuenow','0');$('holdStatus').textContent='Choose a piece to steady.';}
    }
    function begin(id, method) {
      cancel();if(!session.start(id,performance.now(),method))return;
      document.querySelectorAll('.piece').forEach(b=>b.classList.toggle('holding',b.dataset.id===id));
      $('holdStatus').textContent='Steady… keep this one piece with you.';
    }
    function renderRound() {
      const round=session.round;
      $('tamarianLine').textContent='Jared at the whirlpool, his hands steady.';
      $('tamarianGloss').textContent='A piece held for attention. The others remain possible.';
      $('roundLabel').textContent='WHIRLPOOL '+(session.index+1)+' / '+packet.rounds.length;
      $('roundKind').textContent=round.kind==='control'?'ordinary control':round.kind;
      $('roundTitle').textContent=round.title;$('roundPrompt').textContent=round.prompt;$('roundContext').textContent=round.context;
      $('roundResolution').hidden=true;$('nextButton').hidden=true;$('pieces').replaceChildren();$('originals').replaceChildren();$('chapterDots').replaceChildren();
      $('pieces').dataset.count=round.pieces.length;
      packet.rounds.forEach((_,i)=>$('chapterDots').append(element('span',undefined,'chapter-dot '+(i<session.index?'complete':i===session.index?'current':''))));
      round.originals.forEach(original=>{
        const source=packet.source_ledger.find(s=>s.source_id===original.source_id), card=element('div',undefined,'original');
        const heading=element('div',undefined,'original-heading'), link=element('a',source.language+' · '+source.publication_date);
        link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
        const quote=element('blockquote',original.text);quote.lang=source.language;
        card.append(heading,quote,element('p','Work’s English pivot · explanatory, not authoritative','pivot-label'),element('p',original.english_pivot,'pivot'));
        $('originals').append(card);
      });
      round.pieces.forEach((piece,i)=>{
        const b=element('button',undefined,'piece');b.dataset.id=piece.id;b.type='button';
        b.setAttribute('aria-label','Hold steady: '+piece.text);b.append(element('span','FLOTSAM '+(i+1)+' · '+piece.evidence_status.replace('_',' '),'piece-index'),element('span',piece.text,'piece-name'),element('span',piece.note,'piece-note'));
        b.onpointerdown=e=>{if(e.button!==0||$('assistMode').checked||session.resolved)return;e.preventDefault();b.setPointerCapture(e.pointerId);begin(piece.id,'pointer');};
        const release=()=>{if(session.active?.id===piece.id && session.active.method==='pointer')cancel();};
        b.onpointerup=release;b.onpointercancel=release;b.onlostpointercapture=release;
        b.onkeydown=e=>{if(['Space','Enter'].includes(e.code)&&!$('assistMode').checked){e.preventDefault();if(!e.repeat)begin(piece.id,'keyboard');}};
        b.onkeyup=e=>{if(['Space','Enter'].includes(e.code)&&!$('assistMode').checked){e.preventDefault();if(session.active?.method==='keyboard')cancel();}};
        b.onblur=()=>{if(session.active?.id===piece.id)cancel();};
        b.onclick=()=>{if($('assistMode').checked)begin(piece.id,'assist');};
        $('pieces').append(b);
      });
      $('seaState').textContent='THE WATER IS LISTENING';cancel();
    }
    function resolved(choice) {
      document.querySelectorAll('.piece').forEach(b=>{b.classList.remove('holding');b.classList.add(b.dataset.id===choice.preserved_id?'preserved':'sunk');b.disabled=true;});
      $('holdFill').style.width='100%';$('holdTrack').setAttribute('aria-valuenow',String(HOLD_MS));$('holdStatus').textContent='One piece preserved. The others remain possible.';
      $('seaState').textContent='THE WHIRLPOOL RESTS';$('roundResolution').hidden=false;
      const kept=session.round.pieces.find(p=>p.id===choice.preserved_id);
      $('resolutionText').textContent='You kept “'+kept.text+'”. Every other piece keeps its original evidence status.';
      if(session.index+1<packet.rounds.length) $('nextButton').hidden=false; else complete();
    }
    function complete() {
      if(delivered)return;delivered=true;
      const id=typeof crypto.randomUUID==='function'?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
      const result={schema_version:'meaning-tower-boss-result-1',packet_id:packet.packet_id,packet_sha256:data.packet_sha256,
        play_id:'PLAY-'+id,actor:{name:'Jared (self-reported player)',runtime:'Meaning Tower browser'},completed_at:new Date().toISOString(),
        completion_status:'completed',choices:clone(session.choices),power_decision:'pending_review',evidence_changed:false};
      bundle={packet:clone(packet),result,governor_input:makeDelivery(packet,result)};
      memoryQueue.push(bundle);
      let saved=false;
      try { if(storageReadable){localStorage.setItem(storageKey,JSON.stringify(memoryQueue));saved=true;} } catch (_) { /* The complete export remains available. */ }
      window.dispatchEvent(new CustomEvent('meaning-tower:governor-input',{detail:clone(bundle.governor_input)}));
      showReceipt(bundle,saved?'Saved in this browser. Download a copy to carry it into a Work Governor review.':'Browser storage is unavailable or full. This receipt is in memory; download or copy it before closing.');
      inboxStatus();
    }
    function showReceipt(saved, storageText) {
      bundle=saved;$('resultPanel').hidden=false;
      $('receiptExplanation').textContent='Your choices are now a Governor input here, with every unselected piece alongside them. No AI has been called. To give Work the encounter, download it and attach the JSON in chat.';
      $('storageStatus').textContent=storageText;$('receiptChoices').replaceChildren();
      saved.governor_input.rounds.forEach(round=>{
        const row=element('div',undefined,'receipt-choice'), p=element('p');p.append(element('strong',round.preserved.text),element('small',' · '+round.preserved.evidence_status.replace('_',' ')));
        const details=element('details'), list=element('ul');details.append(element('summary','Also carried: '+round.sunk.length+' unselected pieces, not false'));
        round.sunk.forEach(piece=>list.append(element('li',piece.text+' · '+piece.evidence_status.replace('_',' '))));details.append(list);row.append(p,details);$('receiptChoices').append(row);
      });
      $('powerNotice').textContent='No power applied. Peculiarity Sense remains a proposal for review after your play.';
      $('bundleText').value=JSON.stringify(saved,null,2);$('exportStatus').textContent='';
      $('tamarianLine').textContent='Jared at the whirlpool, his hands steady.';
      $('tamarianGloss').textContent='Your choices have arrived. Their evidence has not changed.';
    }
    $('nextButton').onclick=()=>{if(session.next())renderRound();};
    $('restartButton').onclick=()=>{cancel();session=new HoldSession(packet);delivered=false;bundle=null;$('resultPanel').hidden=true;renderRound();};
    $('restoreButton').onclick=()=>{cancel();const last=memoryQueue[memoryQueue.length-1];if(last?.governor_input?.rounds)showReceipt(last,'Restored from this browser’s inbox; no new delivery was created.');};
    $('downloadButton').onclick=()=>{
      if(!bundle)return;const blob=new Blob([JSON.stringify(bundle,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=element('a');
      a.href=url;a.download=bundle.result.play_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('exportStatus').textContent='Encounter ready to save.';
    };
    $('copyButton').onclick=async()=>{
      try {await navigator.clipboard.writeText($('bundleText').value);$('exportStatus').textContent='Copied.';}
      catch (_){$('bundleText').parentElement.open=true;$('bundleText').focus();$('bundleText').select();$('exportStatus').textContent='Select and copy the JSON below.';}
    };
    window.addEventListener('blur',cancel);document.addEventListener('visibilitychange',()=>{if(document.hidden)cancel();});
    renderRound();inboxStatus();

    const ctx=$('sea').getContext('2d');ctx.imageSmoothingEnabled=false;
    const px=(x,y,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(Math.round(x),Math.round(y),w,h);};
    function draw(time,progress) {
      px(0,0,640,420,'#052531');
      for(let row=0;row<10;row++)for(let x=-30;x<680;x+=40)px(x,135+row*28+Math.sin(time*1.3+x*.03+row)*4,24,5,row%2?'#0a4250':'#0b5260');
      const calm=session.resolved?1:progress/HOLD_MS;
      for(let ring=0;ring<7;ring++) {ctx.beginPath();const start=time*(1.8+ring*.08)*(ring%2?1:-1);ctx.strokeStyle=ring%2?'#2a9cab':'#78ded4';ctx.globalAlpha=.14+.05*ring;ctx.lineWidth=3;ctx.ellipse(320,276,26+ring*15,13+ring*7.5,0,start,start+Math.PI*(1.15+calm*.5));ctx.stroke();}
      ctx.globalAlpha=1;
      // The original staged Tide-Shepherd's pixel silhouette, drawn larger for readable play.
      const bx=320,by=105+Math.round(Math.sin(time*1.7)*2);
      px(bx-46,by-40,92,5,'#0b8390');px(bx-34,by-47,12,11,'#65e2d1');px(bx-6,by-54,12,18,'#eaca87');px(bx+22,by-47,12,11,'#65e2d1');
      px(bx-34,by-20,68,16,'#147a86');px(bx-26,by-4,52,34,'#1794a0');px(bx-18,by+30,36,14,'#0d6674');
      px(bx-18,by-32,36,25,'#63d7cf');px(bx-13,by-24,6,5,'#06252d');px(bx+7,by-24,6,5,'#06252d');px(bx-5,by-13,10,4,'#0d5c67');
      for(let i=0;i<7;i++){const x=bx-24+i*8,sway=Math.sin(time*2+i*.8)*5;px(x,by-7,6,29+(i%2)*7,'#36b7ad');px(x+sway,by+18+(i%2)*7,6,17,'#78e5d8');}
      px(bx-48,by-10,14,34,'#13818d');px(bx+34,by-10,14,34,'#13818d');px(bx-58,by+12,12,10,'#5cd5cb');px(bx+46,by+12,12,10,'#5cd5cb');
      px(bx+61,by-40,4,78,'#b9efe4');px(bx+53,by-42,4,19,'#b9efe4');px(bx+69,by-42,4,19,'#b9efe4');px(bx+53,by-43,20,4,'#b9efe4');
      for(let i=0;i<5;i++)for(let s=0;s<5;s++)px(bx-34+i*17+Math.sin(time*2.2+s*.8+i)*7,by+42+s*8,9,7,i%2?'#0f7c88':'#1598a0');
      for(let i=0;i<session.round.pieces.length;i++){if(session.resolved&&session.choices[session.index].preserved_id!==session.round.pieces[i].id)continue;const angle=i*2*Math.PI/session.round.pieces.length+time*.25*(1-calm);const x=320+Math.cos(angle)*125,y=276+Math.sin(angle)*54;
        px(x-15,y-5,30,10,session.resolved&&session.choices[session.index].preserved_id===session.round.pieces[i].id?'#b4dac5':'#bea978');px(x-10,y-2,21,2,'#806e4d');}
    }
    function frame(now) {
      if(!document.hidden) {
        const progress=session.progress(now),choice=session.tick(now);
        if(choice)resolved(choice);
        else if(session.active){$('holdFill').style.width=(progress/HOLD_MS*100)+'%';$('holdTrack').setAttribute('aria-valuenow',String(Math.floor(progress)));}
        draw($('motionOff').checked?0:now/1000,progress);
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
})();
