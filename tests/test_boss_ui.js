'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {HoldSession,digest,sha256,makeDelivery,normalizeBundle,chatNote,canonical}=require('../web/meaning-tower/boss.js');
const {validatePacket}=require('../web/meaning-tower/packet.js');
const packet=JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/meaning-tower/parallax-trucks-2026-09-25.json')));
const original=JSON.stringify(packet);
for(const text of ['', 'abc', '电动货车 🌊', 'x'.repeat(1200)]) assert.equal(sha256(text),crypto.createHash('sha256').update(text).digest('hex'));
const session=new HoldSession(packet), [first,second]=packet.rounds[0].pieces;
session.start(first.id,0,'pointer');assert.equal(session.tick(1800),null);
session.cancel();session.start(first.id,2000,'pointer');assert.equal(session.tick(2100),null,'releasing resets progress');
session.start(second.id,2100,'pointer');assert.equal(session.tick(3900),null,'changing pieces resets progress');
assert.equal(session.tick(4000).preserved_id,second.id);
assert.equal(session.tick(5000),null,'a completed hold cannot append twice');
assert.equal(session.start(first.id,6000,'keyboard'),false);
session.next();session.start(session.round.pieces[0].id,7000,'keyboard');session.tick(8900);
session.next();session.start(session.round.pieces[2].id,10000,'assist');session.tick(11900);
const result={schema_version:'meaning-tower-boss-result-1',packet_id:packet.packet_id,packet_sha256:digest(packet),
  play_id:'TEST-NODE-1',actor:{name:'Automated verifier, not Jared',runtime:'Node fixture'},completed_at:'2026-09-25T22:00:00Z',
  completion_status:'completed',choices:session.choices,power_decision:'pending_review',evidence_changed:false};
const delivery=makeDelivery(packet,result);
assert.deepEqual(delivery.applied_powers,[]);
assert.deepEqual(delivery.selection_before_powers,delivery.selection_after_powers);
assert.equal(delivery.evidence_changed,false);
assert.equal(delivery.canonical_admission,false);
packet.rounds.forEach((round,i)=>assert.equal(delivery.rounds[i].sunk.length+1,round.pieces.length));
assert.equal(JSON.stringify(packet),original,'play preserves the complete source packet');
validatePacket(packet,1,canonical);
// A changed content packet can be loaded without rebuilding the player.
const next=JSON.parse(original);next.packet_id='TEST-RELOADED';next.title='Another question 🌊';
validatePacket(next,1,canonical);
const nextResult={...result,packet_id:next.packet_id,packet_sha256:digest(next)};
const reopened=normalizeBundle({packet:next,result:nextResult,governor_input:{applied_powers:['FORGED'],evidence_changed:true}},1);
assert.deepEqual(reopened.governor_input.applied_powers,[],'receipt imports derive delivery again');
assert.equal(reopened.governor_input.evidence_changed,false);
assert.ok(chatNote(reopened).includes(second.text));
assert.ok(chatNote(reopened).includes('Other pieces, still possible:'));
assert.ok(chatNote(reopened).includes(next.source_ledger[0].url));
assert.throws(()=>normalizeBundle({packet:next,result},1),/exact encounter/,'changed text cannot reuse an old result');
for(const url of ['javascript:alert(1)','https://127.0.0.1/x','https://2130706433/x','https://u:p@example.org/x','https://a.local/x']){
  const invalid=JSON.parse(original);invalid.source_ledger[0].url=url;
  assert.throws(()=>validatePacket(invalid,1,canonical));
}
for(const change of [p=>p.epoch=2,p=>p.rounds[0].pieces[0].source_refs=['MISSING'],p=>p.rounds[0].pieces[0].score=1,
  p=>p.source_ledger[0].publication_date='2026-02-30',p=>p.power_candidate.canonical_status='approved']){
  const invalid=JSON.parse(original);change(invalid);assert.throws(()=>validatePacket(invalid,1,canonical));
}
if(process.argv.includes('--fixture')) process.stdout.write(JSON.stringify({packet,result,governor_input:delivery}));
else process.stdout.write('Hold integrity, reloadable content, imported receipt derivation, source links, packet binding and Chat handoff passed.\n');
