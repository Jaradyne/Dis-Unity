/* Local import checks matching scripts/meaning_boss.py. Content is data, never code. */
(function () {
  'use strict';
  const MAX_PACKET_BYTES = 98304, MAX_FILE_BYTES = 300000;
  const requireValue = (ok, message) => { if (!ok) throw new Error(message); };
  const record = (value, required, optional=[]) => {
    requireValue(value && typeof value==='object' && !Array.isArray(value), 'Expected a named record.');
    requireValue(required.every(k=>Object.hasOwn(value,k)) && Object.keys(value).every(k=>required.includes(k)||optional.includes(k)), 'Record has missing or unexpected fields.');
  };
  const words = (value, max=1600) => requireValue(typeof value==='string' && value.trim() && [...value].length<=max, 'Expected nonempty text within the packet limit.');
  const list = (value, min=0, max=12) => requireValue(Array.isArray(value) && value.length>=min && value.length<=max, 'List has too few or too many items.');
  const texts = (value, min=0) => { list(value,min);value.forEach(v=>words(v)); };
  const identifier = value => requireValue(typeof value==='string' && /^[A-Za-z][A-Za-z0-9_.-]{0,95}$/.test(value), 'Use stable named IDs.');
  function instant(value) {
    words(value,40);
    requireValue(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value) && Number.isFinite(Date.parse(value)), 'Use an ISO timestamp with its timezone.');
    day(value.slice(0,10));
  }
  function day(value) {
    if(value===null)return;
    requireValue(typeof value==='string' && /^\d{4}-\d{2}-\d{2}$/.test(value), 'Use an ISO date or null.');
    const date=new Date(value+'T00:00:00Z');
    requireValue(Number.isFinite(date.getTime()) && date.toISOString().slice(0,10)===value, 'Invalid calendar day.');
  }
  function publicURL(value) {
    words(value,2048);
    const url=new URL(value);
    requireValue(url.protocol==='https:' && url.hostname.includes('.') && !url.username && !url.password && !url.port && !/\s|\\/.test(value) && !/\.(localhost|local|internal)$/.test(url.hostname) && !/^[\d.]+$/.test(url.hostname) && !url.hostname.includes(':'), 'Sources need public named HTTPS URLs without credentials.');
  }
  function actor(value, model=false) {
    record(value,model?['name','runtime','model']:['name','runtime']);
    Object.values(value).forEach(v=>words(v,160));
  }
  function validatePacket(packet, epoch, canonical) {
    requireValue(new TextEncoder().encode(canonical(packet)).length<=MAX_PACKET_BYTES, 'Packet is larger than 96 KiB.');
    record(packet,['schema_version','packet_id','boss_id','packet_status','question_id','epoch','title','created_at','actor','source_ledger','comparison','cross','rounds'],['power_candidate']);
    requireValue(packet.schema_version==='meaning-tower-boss-packet-1' && packet.boss_id==='THE-UNRESOLVED' && packet.packet_status==='evidence_backed', 'Load a Translation/Parallax Tide-Shepherd packet.');
    requireValue(packet.question_id==='Q-MEANING-TRANSLATION-BOSS' && Number.isSafeInteger(packet.epoch) && packet.epoch===epoch, 'Packet needs the Translation Boss Question and the epoch included in this player.');
    const seen=new Set(), sourceIDs=new Set(), urls=new Set();
    const unique=id=>{identifier(id);requireValue(!seen.has(id),'Packet IDs must be unique.');seen.add(id);};
    const refs=(value,min=0)=>{list(value,min,3);requireValue(value.every(id=>sourceIDs.has(id))&&new Set(value).size===value.length,'Use unique references to sources in this packet.');};
    unique(packet.packet_id);words(packet.title,240);instant(packet.created_at);actor(packet.actor,true);
    list(packet.source_ledger,2,3);
    packet.source_ledger.forEach(s=>{
      record(s,['source_id','url','title','language','publication_date','observation_date','retrieved_at','access_limitations']);
      unique(s.source_id);sourceIDs.add(s.source_id);publicURL(s.url);
      requireValue(!urls.has(s.url),'Repeated URLs are not separate sources.');urls.add(s.url);
      words(s.title,400);words(s.language,80);day(s.publication_date);day(s.observation_date);instant(s.retrieved_at);texts(s.access_limitations);
      requireValue((s.publication_date!==null&&s.observation_date!==null)||s.access_limitations.length,'Explain unknown source dates in access limitations.');
    });
    record(packet.comparison,['kind','summary','ordinary_explanations','limitations']);
    requireValue(packet.comparison.kind==='official_notice_and_summary','This player supports a matched official notice and summary.');
    words(packet.comparison.summary);texts(packet.comparison.ordinary_explanations,1);texts(packet.comparison.limitations,1);
    record(packet.cross,['inherited','independent','bridge']);refs(packet.cross.inherited,1);refs(packet.cross.independent);texts(packet.cross.bridge);
    list(packet.rounds,1,4);
    packet.rounds.forEach(r=>{
      record(r,['id','kind','title','prompt','context','originals','pieces']);unique(r.id);
      requireValue(['control','residual','question'].includes(r.kind),'Unknown round kind.');words(r.title,240);words(r.prompt);words(r.context);
      list(r.originals,1,3);refs(r.originals.map(o=>o.source_id),1);
      r.originals.forEach(o=>{record(o,['source_id','text','english_pivot']);words(o.text);words(o.english_pivot);});
      list(r.pieces,2,4);
      r.pieces.forEach(p=>{
        record(p,['id','text','note','evidence_status','source_refs']);unique(p.id);words(p.text,400);words(p.note);
        requireValue(['source_statement','inference','question','unknown'].includes(p.evidence_status),'Unknown evidence label.');refs(p.source_refs,p.evidence_status==='source_statement'?1:0);
      });
    });
    requireValue(packet.rounds.some(r=>r.kind==='control')&&packet.rounds.filter(r=>r.kind==='residual').length<=3,'Keep an ordinary control and at most three residuals.');
    if(packet.power_candidate!=null){
      const p=packet.power_candidate;record(p,['id','text','canonical_status']);unique(p.id);words(p.text);
      requireValue(p.id==='PECULIARITY_SENSE'&&p.canonical_status==='proposed','Only the existing proposed power is supported.');
    }
    return packet;
  }
  function validateResult(packet,result,digest,canonical) {
    requireValue(new TextEncoder().encode(canonical(result)).length<=8192,'Play result is too large.');
    record(result,['schema_version','packet_id','packet_sha256','play_id','actor','completed_at','completion_status','choices','power_decision','evidence_changed']);
    requireValue(result.schema_version==='meaning-tower-boss-result-1'&&result.packet_id===packet.packet_id&&result.packet_sha256===digest(packet),'Play does not match the exact encounter text.');
    identifier(result.play_id);actor(result.actor);instant(result.completed_at);
    requireValue(result.completion_status==='completed'&&result.power_decision==='pending_review'&&result.evidence_changed===false,'Completed play must preserve evidence and leave powers for review.');
    list(result.choices,packet.rounds.length,packet.rounds.length);
    result.choices.forEach((c,i)=>{
      record(c,['round_id','preserved_id','held_ms','input_method']);const r=packet.rounds[i];
      requireValue(c.round_id===r.id&&r.pieces.some(p=>p.id===c.preserved_id),'Each round needs its own valid choice in order.');
      requireValue(Number.isSafeInteger(c.held_ms)&&c.held_ms>=1900&&c.held_ms<=600000&&['pointer','keyboard','assist'].includes(c.input_method),'Invalid hold record.');
    });
    return result;
  }
  const api={validatePacket,validateResult,MAX_FILE_BYTES};
  if(typeof module!=='undefined')module.exports=api;
  else globalThis.TowerPacket=api;
})();
