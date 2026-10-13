"""Reproduce approved S2 Panels A/D; never write to the publication workbook.

Run after scripts 02, 04 and 05. Existing result CSVs are read-only inputs.
Verification is against full-precision numeric XLSX cells, not displayed rounding.
"""
from common import *
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = BASE.parents[2]
S2 = ROOT / 'supplementary/Supplementary_Table_S2.xlsx'
S2_SHA256 = 'd61eda7730afec629b9fc8d41d51c5b39831bc515dbb498f9aaa06d79eb00dbb'
LABELS = ['MATTR', 'Lexical density', 'Average syllables per word',
          'Lexical sophistication', 'MDD', 'MHD', 'Average line length',
          'Line repetition rate']
RTOL, ATOL = 1e-10, 1e-13

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def read_s2():
    require(hashlib.sha256(S2.read_bytes()).hexdigest() == S2_SHA256,
            'Approved S2 checksum mismatch')
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(S2) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(si.itertext()) for si in
                       ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si', ns)]
        cells = {}
        for c in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:c', ns):
            require(c.find('s:f', ns) is None, 'Unexpected formula in approved S2')
            v = c.find('s:v', ns)
            inline = c.find('s:is', ns)
            if c.get('t') == 's':
                value = strings[int(v.text)]
            elif c.get('t') == 'inlineStr':
                value = ''.join(inline.itertext())
            elif c.get('t') == 'str':
                value = v.text
            elif v is not None:
                value = float(v.text)
            else:
                continue
            cells[c.attrib['r']] = value
    return cells

def main():
    cells = read_s2()
    df = load()  # verifies the public frozen v1.1 dataset and integrity manifest
    N, G = len(df), df.primary_artist.nunique()
    require((N, G) == (561, 231), 'Unexpected sample or artist-cluster count')
    checks = []
    def compare(cell, actual, pvalue=False):
        approved = float(cells[cell])
        tolerance = 0. if pvalue else ATOL
        require(np.isclose(actual, approved, rtol=RTOL, atol=tolerance),
                f'S2 mismatch at {cell}: {actual!r} vs {approved!r}')
        checks.append(dict(cell=cell, reproduced=float(actual), approved=approved,
                           absolute_difference=abs(actual-approved),
                           rtol=RTOL, atol=tolerance, passed=True))

    anova = pd.read_csv(RESULTS/'anova_omnibus.csv', float_precision='round_trip').set_index('feature')
    panel_a = []
    for row, outcome, label in zip(range(8, 16), MEASURES, LABELS):
        require(cells[f'A{row}'] == label, 'Unexpected Panel A row label')
        fit = smf.ols(f'{outcome} ~ C(genre)', data=df).fit(
            cov_type='cluster', cov_kwds={'groups': df.primary_artist,
            'use_correction': True, 'df_correction': True}, use_t=True)
        names = list(fit.params.index)
        R = np.eye(len(names))[[i for i, term in enumerate(names) if term.startswith('C(genre)')]]
        test = fit.f_test(R)
        require((test.df_num, test.df_denom) == (6, 230), 'Unexpected CR1 test df')
        compare(f'B{row}', anova.loc[outcome, 'F'])
        compare(f'C{row}', anova.loc[outcome, 'p'], True)
        compare(f'D{row}', float(test.fvalue))
        compare(f'E{row}', float(test.pvalue), True)
        panel_a.append(dict(outcome=outcome, model='M0', formula=f'{outcome} ~ C(genre)',
            N=N, clusters=G, clustering_variable='primary_artist', covariance='CR1',
            finite_cluster_covariance_multiplier=G/(G-1)*(N-1)/(N-len(names)),
            genre_F=float(test.fvalue), genre_df_num=6, genre_df_denom=230,
            genre_p=float(test.pvalue), significant_alpha_05=float(test.pvalue)<.05,
            s2_F_cell=f'D{row}', s2_p_cell=f'E{row}'))

    panel_d = []
    others = [g for g in GENRES if g != 'rap']
    for estimator, prefix, lower, upper, pcolumn, expected_df in [
            ('HC3', 'hc3', 'D', 'E', 'F', 553),
            ('CR1', 'cluster', 'G', 'H', 'I', 230)]:
        contrasts = pd.read_csv(RESULTS/f'{prefix}_rap_contrasts.csv', float_precision='round_trip')
        models = pd.read_csv(RESULTS/f'{prefix}_models.csv', float_precision='round_trip')
        for outcome in ['MDD', 'MHD']:
            model = models[(models.outcome == outcome) & (models.model == 'M1')]
            require(len(model) == 1, 'Expected one M1 model record')
            dof = float(model.iloc[0].genre_df_denom)
            require(dof == expected_df, 'Unexpected M1 inference df')
            source = contrasts[(contrasts.outcome == outcome) & (contrasts.model == 'M1')]
            require(len(source) == 6 and set(source.contrast) == {'rap - '+g for g in others},
                    'Expected exactly six Rap contrasts per family')
            critical = stats.t.ppf(1-.05/(2*6), dof)
            for i, genre in enumerate(others):
                row = 41 + (6 if outcome == 'MHD' else 0) + i
                require(cells[f'A{row}'] == outcome and
                        cells[f'B{row}'] == 'Rap − '+{'r&b':'R&B'}.get(genre, genre.title()),
                        'Unexpected Panel D row label')
                s = source[source.contrast == 'rap - '+genre].iloc[0]
                estimate, se = float(s.estimate), float(s.SE)
                lo, hi = estimate-critical*se, estimate+critical*se
                compare(f'C{row}', estimate)
                compare(f'{lower}{row}', lo)
                compare(f'{upper}{row}', hi)
                compare(f'{pcolumn}{row}', float(s.p_bonferroni_six), True)
                excludes_zero = lo > 0 or hi < 0
                require(excludes_zero == (s.p_bonferroni_six < .05),
                        'Simultaneous CI decision differs from Bonferroni p')
                panel_d.append(dict(outcome=outcome, model='M1', estimator=estimator,
                    contrast=s.contrast, estimate=estimate, SE=se, inference_df=dof,
                    alpha=.05, family_size=6, critical_t=critical,
                    simultaneous_ci95_lower=lo, simultaneous_ci95_upper=hi,
                    p_bonferroni_six=float(s.p_bonferroni_six), excludes_zero=excludes_zero,
                    contrast_source=f'{prefix}_rap_contrasts.csv', df_source=f'{prefix}_models.csv',
                    s2_lower_cell=f'{lower}{row}', s2_upper_cell=f'{upper}{row}'))
    # Write only new supplementary outputs, after every comparison has passed.
    save('s2_panel_a_artist_clustered.csv', panel_a)
    save('s2_panel_d_simultaneous_intervals.csv', panel_d)
    report = dict(status='PASS', N=N, clusters=G,
                  dataset_sha256=frozen_dataset.EXPECTED_SHA256,
                  s2_sha256=S2_SHA256, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  panel_a_models=8, panel_d_intervals=24, numerical_cell_checks=len(checks),
                  checks=checks, existing_outputs_read_only=True)
    (RESULTS/'s2_panels_verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: S2 Panel A (8 CR1 models) and Panel D (24 simultaneous intervals)')

if __name__ == '__main__':
    main()
