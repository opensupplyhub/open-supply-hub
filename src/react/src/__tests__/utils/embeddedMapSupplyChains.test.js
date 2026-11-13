import {
    findEmbedSupplyChain,
    getChainDepths,
    getChainGroups,
    getEmbedSupplyChains,
    getSafeProductUrl,
} from '../../util/embeddedMap';
import FiltersReducer from '../../reducers/FiltersReducer';
import { resetAllFilters, selectEmbedSupplyChain } from '../../actions/filters';

const node = (osId, name, tier) => ({
    os_id: osId,
    name,
    address: '1 Main Street',
    country_name: 'Vietnam',
    lat: 1,
    lng: 2,
    stage: '',
    tier,
});

describe('embedded map supply chains', () => {
    const chain = {
        id: 7,
        name: 'Jacket',
        color: '#c0392b',
        nodes: [
            node('F', 'Factory', '1'),
            node('M1', 'Mill One', '2'),
            node('M2', 'Mill Two', '2'),
            node('S', 'Spinner', '3'),
        ],
        links: [
            ['M1', 'F'],
            ['M2', 'F'],
            ['S', 'M1'],
        ],
    };

    describe('getEmbedSupplyChains', () => {
        it('returns the published chains on an embedded map', () => {
            const config = { supply_chains: [chain, { ...chain, nodes: [] }] };

            expect(getEmbedSupplyChains(true, config)).toEqual([chain]);
        });

        it('returns none outside an embed or without any', () => {
            expect(getEmbedSupplyChains(false, { supply_chains: [chain] })).toEqual(
                [],
            );
            expect(getEmbedSupplyChains(true, {})).toEqual([]);
            expect(getEmbedSupplyChains(true, null)).toEqual([]);
        });

        it('finds a chain by id, whatever type the id is', () => {
            expect(findEmbedSupplyChain([chain], '7')).toBe(chain);
            expect(findEmbedSupplyChain([chain], 8)).toBeNull();
            expect(findEmbedSupplyChain([chain], null)).toBeNull();
        });
    });

    describe('getChainGroups', () => {
        it('groups by tier, upstream first, when every location has one', () => {
            const groups = getChainGroups(chain);

            expect(groups.map(g => g.label)).toEqual([
                'Tier 3',
                'Tier 2',
                'Tier 1',
            ]);
            expect(groups[1].nodes.map(n => n.name)).toEqual([
                'Mill One',
                'Mill Two',
            ]);
        });

        it('says what each location supplies', () => {
            const [tier3, tier2, tier1] = getChainGroups(chain);

            expect(tier3.nodes[0].supplies).toEqual(['Mill One']);
            expect(tier2.nodes[1].supplies).toEqual(['Factory']);
            expect(tier1.nodes[0].supplies).toEqual([]);
        });

        it('groups by position in the chain without tiers', () => {
            const untiered = {
                ...chain,
                nodes: chain.nodes.map(n => ({ ...n, tier: null })),
            };
            const groups = getChainGroups(untiered);

            expect(groups.map(g => g.label)).toEqual([
                'Step 1',
                'Step 2',
                'Step 3',
            ]);
            expect(groups[0].nodes.map(n => n.name)).toEqual(['Spinner']);
            expect(groups[2].nodes.map(n => n.name)).toEqual(['Factory']);
        });

        it('measures depth from the end of the chain', () => {
            expect(getChainDepths(chain)).toEqual({ F: 1, M1: 2, M2: 2, S: 3 });
        });
    });

    describe('getSafeProductUrl', () => {
        it('only allows web addresses', () => {
            expect(getSafeProductUrl(' https://example.com/jacket ')).toBe(
                'https://example.com/jacket',
            );
            expect(getSafeProductUrl(['javascript', 'alert(1)'].join(':'))).toBe('');
            expect(getSafeProductUrl('')).toBe('');
            expect(getSafeProductUrl(undefined)).toBe('');
        });
    });

    describe('reducer', () => {
        const initial = FiltersReducer(undefined, { type: '@@INIT' });

        it('follows and stops following a chain', () => {
            expect(initial.embedSupplyChainId).toBeNull();

            const following = FiltersReducer(initial, selectEmbedSupplyChain(7));
            expect(following.embedSupplyChainId).toBe(7);
            expect(
                FiltersReducer(following, selectEmbedSupplyChain(null))
                    .embedSupplyChainId,
            ).toBeNull();
        });

        it('stops following a chain when the filters are reset', () => {
            const following = FiltersReducer(initial, selectEmbedSupplyChain(7));

            expect(
                FiltersReducer(following, resetAllFilters(true))
                    .embedSupplyChainId,
            ).toBeNull();
        });
    });
});
