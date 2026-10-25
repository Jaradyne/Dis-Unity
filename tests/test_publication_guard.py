"""Prevent excluded or temporary receipt copies from entering a release manifest."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('richmond_publication',ROOT/'reports/shelter-accountability/richmond-operations-20261024/verify_packet.py')
publication=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publication)


class PublicationGuardTests(unittest.TestCase):
    def test_rejects_excluded_content_under_a_new_name(self):
        manifest={'excluded':[{'excluded_repository_path':'receipts/private.json','sha256':'a'*64}],
                  'files_sha256':{'receipts/renamed.json':'a'*64}}
        with self.assertRaises(AssertionError):
            publication.validate_publication_paths(manifest)

    def test_rejects_temporary_receipt_even_with_different_bytes(self):
        manifest={'excluded':[], 'files_sha256':{'receipts/api/.0007.json.partial':'b'*64}}
        with self.assertRaises(AssertionError):
            publication.validate_publication_paths(manifest)
        manifest['files_sha256']={'receipts/api/0001.json':'c'*64,'.github/workflows/verify.yml':'d'*64}
        publication.validate_publication_paths(manifest)


if __name__=='__main__':unittest.main()
