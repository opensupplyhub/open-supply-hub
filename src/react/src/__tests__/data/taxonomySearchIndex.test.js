import fs from 'fs';
import path from 'path';

import { getIsic4SearchIndex } from '../../data/isic4SearchIndex';

const TAXONOMY_SOURCE_FILES = [
    '../../data/isic4SearchIndex.js',
    '../../data/taxonomySearchIndex.js',
];

const SAMPLE_ISIC_TAXONOMY = Object.freeze({
    sections: [
        {
            code: 'A',
            label: 'Agriculture, forestry and fishing',
            displayLabel: 'A - Agriculture, forestry and fishing',
            kind: 'section',
            divisions: [
                {
                    code: '01',
                    label: 'Crop and animal production',
                    displayLabel: '01 - Crop and animal production',
                    kind: 'division',
                    groups: [
                        {
                            code: '011',
                            label: 'Growing of non-perennial crops',
                            displayLabel: '011 - Growing of non-perennial crops',
                            kind: 'group',
                            classes: [
                                {
                                    code: '0111',
                                    label: 'Growing of cereals',
                                    displayLabel: '0111 - Growing of cereals',
                                    kind: 'class',
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ],
});

describe('taxonomy search index', () => {
    test('builds the ISIC search index once per module load', () => {
        const first = getIsic4SearchIndex(SAMPLE_ISIC_TAXONOMY, 'test');
        const second = getIsic4SearchIndex(SAMPLE_ISIC_TAXONOMY, 'test');

        expect(first).toBe(second);
        expect(first.flatNodes.length).toBeGreaterThan(0);
    });

    test('taxonomy modules do not import spreadsheet parsers at build time', () => {
        const forbiddenPatterns = [
            /\bfrom\s+['"]xlsx['"]/,
            /\brequire\s*\(\s*['"]xlsx['"]\s*\)/,
            /\bfrom\s+['"][^'"]*\.ods['"]/,
            /\bfrom\s+['"][^'"]*\.xlsx['"]/,
        ];

        TAXONOMY_SOURCE_FILES.forEach(relativePath => {
            const absolutePath = path.resolve(__dirname, relativePath);
            const source = fs.readFileSync(absolutePath, 'utf8');

            forbiddenPatterns.forEach(pattern => {
                expect(source).not.toMatch(pattern);
            });
        });
    });
});
