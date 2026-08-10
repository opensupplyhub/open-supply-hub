import fs from 'fs';
import path from 'path';

import {
    getFacilityProcessingSearchIndex,
    getFacilityProcessingVisibleRows,
} from '../../data/facilityProcessingSearchIndex';
import { getIsic4SearchIndex } from '../../data/isic4SearchIndex';

const TAXONOMY_SOURCE_FILES = [
    '../../data/facilityProcessingTaxonomy.js',
    '../../data/isicRev4Taxonomy.js',
    '../../data/facilityProcessingSearchIndex.js',
    '../../data/isic4SearchIndex.js',
    '../../data/taxonomySearchIndex.js',
];

describe('taxonomy search index', () => {
    test('builds the facility processing search index once per module load', () => {
        const first = getFacilityProcessingSearchIndex();
        const second = getFacilityProcessingSearchIndex();

        expect(first).toBe(second);
        expect(first.groups.length).toBeGreaterThan(0);
    });

    test('builds the ISIC search index once per module load', () => {
        const first = getIsic4SearchIndex();
        const second = getIsic4SearchIndex();

        expect(first).toBe(second);
        expect(first.flatNodes.length).toBeGreaterThan(0);
    });

    test('filtering "material" returns parent facility types and nested processing matches', () => {
        const { groups } = getFacilityProcessingSearchIndex();
        const { rows } = getFacilityProcessingVisibleRows(groups, 'material');

        const parentLabels = rows
            .filter(row => row.depth === 0)
            .map(row => row.node.label);
        const childLabels = rows
            .filter(row => row.depth === 1)
            .map(row => row.node.label);

        expect(parentLabels).toContain('Raw Material Processing or Production');
        expect(parentLabels).toContain('Textile or Material Production');
        expect(childLabels).toEqual(
            expect.arrayContaining([
                'Material Creation',
                'Material Production',
                'Textile or Material Production',
            ]),
        );
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
