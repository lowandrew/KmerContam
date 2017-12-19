import shutil
import os
import sys
from Bio import SeqIO

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
from confindr.confindr import *


def test_present_dependency():
    assert dependency_check('ls') is True


def test_nonexistent_dependency():
    assert dependency_check('fake_dependency') is False


def test_r1_fastqs():
    assert find_paired_reads('tests/fake_fastqs/') == [['tests/fake_fastqs/test_R1.fastq.gz',
                                                        'tests/fake_fastqs/test_R2.fastq.gz']]


def test_1_fastqs():
    assert find_paired_reads('tests/fake_fastqs/', forward_id='_1',
                             reverse_id='_2') == [['tests/fake_fastqs/test_1.fastq.gz',
                                                   'tests/fake_fastqs/test_2.fastq.gz']]


def test_empty_fastqs():
    assert find_paired_reads('tests/fake_fastqs/', forward_id='_asdf', reverse_id='_fdsa') == []


def test_unpaired_fastq():
    assert 'tests/fake_fastqs/test_alone.fastq.gz' in find_unpaired_reads('tests/fake_fastqs')


# def test_mashsippr_run():
#    assert run_mashsippr('mashsippr', 'mashsippr/mashsippr_results', 'databases') is True
#    shutil.rmtree('mashsippr/O157')
#    shutil.rmtree('mashsippr/mashsippr_results')


def test_mashsippr_read():
    assert read_mashsippr_output('tests/mash.csv', 'O157') == 'Escherichia'


def test_mashsippr_read_fail():
    assert read_mashsippr_output('tests/mash.csv', 'NotInTheFile') == 'NA'


def test_genus_exclusion_positive():
    assert find_genusspecific_alleles('databases/profiles.txt', 'Escherichia') == ['BACT000060', 'BACT000065']


def test_genus_exclusion_negative():
    assert find_genusspecific_alleles('databases/profiles.txt', 'NotARealGenus') == []


def test_rmlst_bait():
    pair = ['tests/mashsippr/O157_R1.fastq.gz', 'tests/mashsippr/O157_R2.fastq.gz']
    actual_result = 'AAAAAAACAGCAAATCCGGTGGTCGTAACAACAATGGCCGTATCACCACTCGTCATATCGGTGGTGGCCA' \
                    'CAAGCAGGCTTACCGTATTGTTGACTTCAAACGCAACAAAGACGGTATCCCGGCAGTTGTTGAACGTCTT' \
                    'GAGTACGATCCGAACCGTTCCGCGAACATCGCGCTGGTTCTGTACAAAGACGGTGAACGCCGTTACATCC' \
                    'TGGCCCCTAAAGGCCTGAAAGCTGGCGACCAGATTCAGTC'
    extract_rmlst_genes(pair, 'tests/bait_fasta.fasta', 'asdf_R1.fasta', 'asdf_R2.fasta')
    thing = SeqIO.read('asdf_R1.fasta', 'fasta')
    assert str(thing.seq) == actual_result
    os.remove('asdf_R1.fasta')
    os.remove('asdf_R2.fasta')


def test_read_subsampling():
    subsample_reads('tests/mashsippr/O157_R1.fastq.gz', 'tests/mashsippr/O157_R2.fastq.gz', 2, 1000, 'asdf_R1.fasta', 'asdf_R2.fasta')
    thing = SeqIO.parse('asdf_R1.fasta', 'fasta')
    bases = 0
    for record in thing:
        bases += len(record.seq)
    assert 1000 <= bases <= 1250
    os.remove('asdf_R1.fasta')
    os.remove('asdf_R2.fasta')


def test_kmerization():
    pair = ['tests/mashsippr/O157_R1.fastq.gz', 'tests/mashsippr/O157_R2.fastq.gz']
    generate_kmers(pair[0], pair[1], 'counts.fasta', 31, 'tmp')
    expected_num_kmers = 23871
    thing = SeqIO.parse('counts.fasta', 'fasta')
    i = 0
    for item in thing:
        i += 1
    assert i == expected_num_kmers
    os.remove('counts.fasta')


def test_kmer_rename():
    rename_kmers('tests/kmers.fasta', 'counts.fasta', 2)
    with open('counts.fasta') as f:
        lines = f.readlines()
    assert lines == ['>3_1\n', 'GCTAGCTAGCTAGCTAGCATGCTACT\n', '>2_2\n', 'ATTCTAGCTACTAGCATGCAGTGGGG\n']
    os.remove('counts.fasta')


def test_bam_parsing():
    fasta_ids = parse_bamfile('tests/subsample_0.bam', 31)
    assert len(fasta_ids) == 32


def test_present_database():
    assert check_db_presence('tests/fake_database.fasta') is True


def test_nonexistent_database():
    assert check_db_presence('tests/not_a_database.fasta') is False


def test_blast_positive():
    assert present_in_db('CAAGCAGGCTTACCGTATTGTTGACTTCAAA', 'tests/bait_fasta.fasta', 31) is True


def test_blast_negative():
    assert present_in_db('CATGCTACGATCGAGTGGGGGGGGG', 'tests/bait_fasta.fasta', 31) is False
