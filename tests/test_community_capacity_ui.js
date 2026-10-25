'use strict';
// Structural loading and an explicitly simulated play; never a play by Jared.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {validatePacket}=require('../web/meaning-tower/packet.js');
const {canonical,digest,HoldSession,makeDelivery}=require('../web/meaning-tower/boss.js');
const packet=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../examples/meaning-tower/richmond-community-capacity-20261024.json')));
validatePacket(packet,1,canonical);
const before=canonical(packet),session=new HoldSession(packet);
packet.rounds.forEach((round,i)=>{session.start(round.pieces[0].id,i*3000,'keyboard');session.tick(i*3000+1900);if(i+1<packet.rounds.length)session.next();});
const delivery=makeDelivery(packet,{schema_version:'meaning-tower-boss-result-1',packet_id:packet.packet_id,
  packet_sha256:digest(packet),play_id:'SIM-RICHMOND-TEST',actor:{name:'Automated test, not a person',runtime:'Node fixture'},
  completed_at:'2026-10-24T19:00:00Z',completion_status:'completed',choices:session.choices,power_decision:'pending_review',evidence_changed:false});
assert.deepEqual(delivery.applied_powers,[]);assert.equal(delivery.canonical_admission,false);
assert.equal(delivery.evidence_changed,false);assert.equal(canonical(packet),before);
assert.equal(delivery.rounds.length,3);
for(const round of delivery.rounds)assert.equal(round.sunk.length,2);
process.stdout.write('PASS: Richmond packet loads; simulated choices retain all pieces; no powers or evidence change\n');
