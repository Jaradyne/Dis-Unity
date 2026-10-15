import copy
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continuity as shared
import cycle
import garden_runtime as garden
import safeguards as sg

ROOT = Path(__file__).resolve().parents[1]


class SafeguardTests(unittest.TestCase):
    def setUp(self):
        self.journal = shared.strict_json(ROOT/sg.JOURNAL)
        self.schema = shared.strict_json(ROOT/sg.SCHEMA)
        self.manifest = shared.strict_json(ROOT/sg.REFERENCES)
        self.state, self.resolved = sg.replay(ROOT)

    def case(self, sid='SG-CEM-INSPECTIONS'):
        return copy.deepcopy(self.state['safeguards'][sid])

    def validate(self, case):
        sg.validate(case, self.schema, self.resolved)

    def append(self, case, revision=None):
        j = copy.deepcopy(self.journal)
        sid = case['safeguard_id']
        j['entries'].append(sg.make_entry(case, sequence=len(j['entries'])+1,
            recorded_at=j['entries'][-1]['recorded_at'], actor='test reviewer',
            reason='Synthetic boundary test only; no empirical admission',
            expected_revision=self.state['revisions'][sid] if revision is None else revision,
            previous=j['entries'][-1]['entry_sha256']))
        return j

    def effect(self, case):
        """Synthetic outcome tests the contract; never added to the saved case."""
        item = copy.deepcopy(case['evidence'][0])
        item.update(evidence_id='SYNTHETIC-EFFECT', kind='effectiveness_observation',
                    claim='Synthetic verified remedy for a single named requirement',
                    period={'start':'2026-06-01','end':'2026-06-01','note':'Synthetic observation date'},
                    effect={'kind':'remedied','harm':'Synthetic unmet TB testing requirement',
                            'action':'Synthetic completed intake change','result':'Synthetic reinspection verified compliance',
                            'scope':'One test fixture; not a claim about real Camp conditions'})
        case['evidence'].append(item)
        case['effectiveness'] = {'status':'observed','claim':'Synthetic bounded remedy',
                                 'evidence_ids':['SYNTHETIC-EFFECT']}
        return case

    def test_three_demonstrations_keep_dimensions_separate(self):
        cases = self.state['safeguards']
        self.assertEqual(len(cases),3)
        self.assertTrue(all(c['formal']['status']=='documented' for c in cases.values()))
        self.assertTrue(all(c['effectiveness']['status']=='unknown' for c in cases.values()))
        self.assertEqual(cases['SG-CEM-INSPECTIONS']['failure']['status'],'documented')
        for sid in ('SG-ORA-CONSCIENCE','SG-JAG-INDEPENDENCE'):
            self.assertEqual(cases[sid]['failure']['status'],'unknown')
        self.assertEqual(cases['SG-JAG-INDEPENDENCE']['operational']['people']['status'],'partial')
        self.assertTrue(all(a['status']=='unknown' for a in cases['SG-ORA-CONSCIENCE']['operational'].values()))

    def test_formal_text_cannot_establish_operation_or_effectiveness(self):
        for component in ('people','procedures','authority'):
            for status in ('observed','partial','absent'):
                case=self.case('SG-ORA-CONSCIENCE')
                case['operational'][component].update(status=status,evidence_ids=['ORA-FORMAL'])
                with self.subTest(component=component,status=status), self.assertRaisesRegex(sg.Error,'policy alone'):
                    self.validate(case)
        case=self.case('SG-ORA-CONSCIENCE')
        case['effectiveness'].update(status='observed',evidence_ids=['ORA-FORMAL'])
        with self.assertRaisesRegex(sg.Error,'Observed effectiveness needs'):
            self.validate(case)

    def test_activity_response_rating_and_open_status_do_not_prove_effectiveness(self):
        for eid in ('CEM-INSPECTION','CEM-ACTIONS','CEM-DHS','CEM-OPEN-STATUS'):
            case=self.case()
            case['effectiveness'].update(status='observed',evidence_ids=[eid])
            with self.subTest(eid=eid), self.assertRaisesRegex(sg.Error,'Observed effectiveness needs'):
                self.validate(case)

    def test_unknown_and_open_status_cannot_establish_failure(self):
        for eid in ('CEM-OPEN-STATUS','CEM-POLICY','CEM-DHS'):
            case=self.case()
            case['failure'].update(status='documented',evidence_ids=[eid])
            with self.subTest(eid=eid), self.assertRaisesRegex(sg.Error,'Documented failure needs'):
                self.validate(case)
        case=self.case('SG-ORA-CONSCIENCE')
        case['failure']['status']='reported'
        with self.assertRaisesRegex(sg.Error,'Reported failure needs'):
            self.validate(case)

    def test_dated_scoped_effect_is_allowed_without_erasing_historical_failure(self):
        case=self.effect(self.case())
        self.validate(case)
        state,_=sg.replay(ROOT,journal=self.append(case))
        latest=state['safeguards'][case['safeguard_id']]
        self.assertEqual(latest['effectiveness']['status'],'observed')
        self.assertEqual(latest['failure']['status'],'documented')
        self.assertEqual(state['history'][:-1],self.state['history'])
        for missing in ('harm','action','result','scope'):
            bad=copy.deepcopy(case)
            del bad['evidence'][-1]['effect'][missing]
            with self.subTest(missing=missing), self.assertRaises(sg.Error):
                self.validate(bad)
        case['evidence'][-1]['period'].update(start=None,end=None)
        with self.assertRaisesRegex(sg.Error,'needs a dated period'):
            self.validate(case)

    def test_all_effect_kinds_are_scoped_and_no_other_class_carries_proven_effect(self):
        for kind in ('prevented','stopped','remedied'):
            case=self.effect(self.case())
            case['evidence'][-1]['effect']['kind']=kind
            self.validate(case)
        case['evidence'][-1]['kind']='formal_text'
        with self.assertRaisesRegex(sg.Error,'Only effectiveness'):
            self.validate(case)

    def test_real_open_status_revision_preserves_both_dates_and_findings(self):
        before=self.journal['entries'][1]['safeguard']
        after=self.journal['entries'][3]['safeguard']
        self.assertEqual(sg.dimensions(before),sg.dimensions(after))
        self.assertEqual(before['evidence_cutoff'],'2026-06-09')
        self.assertEqual(after['evidence_cutoff'],'2026-10-12')
        self.assertEqual(after['evidence'][:-1],before['evidence'])
        self.assertTrue(self.journal['entries'][1]['recorded_at'].startswith('2026-10-14'))
        self.assertEqual(after['evidence'][-1]['period']['start'],'2026-10-12')
        self.assertEqual(self.state['history'][3]['revision'],2)

    def test_journal_mutation_stale_writer_and_reordering_fail(self):
        j=copy.deepcopy(self.journal)
        j['entries'][0]['safeguard']['formal']['claim']='Changed history'
        with self.assertRaisesRegex(sg.Error,'Entry modified'):
            sg.replay(ROOT,journal=j)
        j=copy.deepcopy(self.journal)
        j['entries'][0],j['entries'][1]=j['entries'][1],j['entries'][0]
        with self.assertRaisesRegex(sg.Error,'sequence mismatch'):
            sg.replay(ROOT,journal=j)
        with self.assertRaisesRegex(sg.Error,'Stale safeguard revision'):
            sg.replay(ROOT,journal=self.append(self.case(),revision=0))

    def test_revision_preserves_old_evidence_contrary_assessments_and_scope(self):
        for mutation in ('evidence','contrary_evidence','scope','evidence_cutoff'):
            case=self.case()
            if mutation=='evidence': case['evidence'][0]['claim']='Silent replacement'
            elif mutation=='contrary_evidence': case['contrary_evidence'].pop()
            elif mutation=='scope': case['scope']='Different population/scope'
            else: case['evidence_cutoff']='2026-10-11'
            with self.subTest(mutation=mutation),self.assertRaises(sg.Error):
                sg.replay(ROOT,journal=self.append(case))
        case=self.case()
        case['failure']['status']='unknown'
        with self.assertRaisesRegex(sg.Error,'changed evidence'):
            sg.replay(ROOT,journal=self.append(case))

    def test_dates_preserve_precision_and_reject_definitely_future_observations(self):
        case=self.case()
        case['evidence'][1]['period'].update(start='2025-08-16',end='2025-08')
        self.validate(case)
        future=(date.fromisoformat(case['evidence_cutoff'])+timedelta(days=1)).isoformat()
        case['evidence'][1]['period'].update(start=future,end=future)
        with self.assertRaisesRegex(sg.Error,'after evidence cutoff'):
            self.validate(case)
        case['evidence'][1]['period'].update(start='2025-09-01',end='2025-08')
        with self.assertRaisesRegex(sg.Error,'Definitely reversed'):
            self.validate(case)

    def test_reference_drift_shadowing_wrong_kind_and_unknown_evidence_fail(self):
        for mutation in ('base','record','shadow','snapshot'):
            manifest=copy.deepcopy(self.manifest)
            if mutation=='base': manifest['base']['sha256']='0'*64
            elif mutation=='record': manifest['references']['S-J03']['sha256']='0'*64
            elif mutation=='shadow': manifest['references']['S-ORA']=manifest['references']['S-J03']
            else: manifest['snapshots']['S-CEM-STATUS']['sha256']='0'*64
            with self.subTest(mutation=mutation),self.assertRaises(sg.Error):
                sg.resolve(ROOT,manifest)
        case=self.case()
        case['evidence'][0]['citations'][0]['source_ref']='E-ORA'
        with self.assertRaisesRegex(sg.Error,'wrong-kind'):
            self.validate(case)
        case=self.case()
        case['formal']['evidence_ids']=['MISSING']
        with self.assertRaisesRegex(sg.Error,'Unknown evidence'):
            self.validate(case)

    def test_schema_identity_and_one_proposed_test_remain_bounded(self):
        case=self.case()
        case['protection_score']=100
        with self.assertRaisesRegex(sg.Error,'unexpected fields'):
            self.validate(case)
        for value in (2,True):
            case=self.case()
            case['next_test']['max_records']=value
            with self.subTest(value=value),self.assertRaises(sg.Error):
                self.validate(case)
        case=self.case()
        case['next_test']['status']='scheduled'
        with self.assertRaises(sg.Error):
            self.validate(case)
        with self.assertRaisesRegex(sg.Error,'Schema snapshot mismatch'):
            sg.replay(ROOT,schema={**self.schema,'title':'Changed'})

    def test_shared_snapshot_lineage_is_not_independent_corroboration(self):
        self.assertEqual(sg.lineage('S-CEM-STATUS',self.resolved),sg.lineage('S-GAO-CEM',self.resolved))
        self.assertEqual(self.resolved['S-CEM-STATUS']['record']['parent_source_id'],'C01')
        self.assertEqual(self.resolved['S-J01']['record']['source_family'],self.resolved['S-J03']['record']['source_family'])
        self.assertIn('pre-Dec2025',self.resolved['S-J01']['record']['limitations'])
        manifest=copy.deepcopy(self.manifest)
        manifest['snapshots']['S-CEM-STATUS']['parent_source_ref']='S-ORA'
        with self.assertRaisesRegex(sg.Error,'parent source identity mismatch'):
            sg.resolve(ROOT,manifest)

    def test_exact_outputs_garden_rest_and_original_continuity_are_preserved(self):
        self.assertEqual(sg.build(ROOT,check=True),5)
        self.assertEqual(shared.build(ROOT,check=True),5)
        self.assertEqual(sg.outputs(ROOT),sg.outputs(ROOT))
        for path in (ROOT/sg.OUTPUT/'garden').glob('*.json'):
            doc=shared.strict_json(path)
            with self.subTest(case=path.stem):
                self.assertEqual(garden.replay(doc),doc)
                commands=[e['command'] for e in doc['events']]
                self.assertEqual([c['node'] for c in commands],garden.NODES)
                self.assertEqual(set(doc['state']['branches']),{'B0'})
                self.assertEqual(doc['state']['branches']['B0']['status'],'resting')
                cross=next(c['output'] for c in commands if c['node']=='CROSS')
                self.assertEqual(cross['independent'],[])
                self.assertEqual(doc['initial']['packet']['budget']['model_calls'],0)

    def test_repository_escape_and_duplicate_json_fail(self):
        manifest=copy.deepcopy(self.manifest)
        manifest['base']['path']='../outside.json'
        with self.assertRaisesRegex(sg.Error,'escapes repository'):
            sg.resolve(ROOT,manifest)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'bad.json'
            path.write_text('{"a":1,"a":2}')
            with self.assertRaisesRegex(sg.Error,'Duplicate JSON'):
                shared.strict_json(path)


if __name__ == '__main__':
    unittest.main()
