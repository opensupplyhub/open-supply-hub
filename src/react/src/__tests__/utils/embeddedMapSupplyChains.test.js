import {
    addChainLink,
    addChainLocation,
    chainHasChanges,
    chainLinksLoop,
    chainStructureKey,
    restoreChainStructure,
    getSchematicLayout,
    moveChain,
    clickChainLocation,
    reverseChainLink,
    formatChainForAPI,
    getChainErrorMessages,
    getPossibleCustomers,
    makeEmptyChain,
    removeChainLink,
    removeChainLocation,
    setChainLocationStage,
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

        it('falls back to position when the tiers disagree with the links', () => {
            // The spinner is marked tier 1 but supplies a tier 2 mill.
            const muddled = {
                ...chain,
                nodes: chain.nodes.map(n =>
                    n.os_id === 'S' ? { ...n, tier: '1' } : n,
                ),
            };

            expect(getChainGroups(muddled).map(g => g.label)).toEqual([
                'Step 1',
                'Step 2',
                'Step 3',
            ]);
        });

        it('measures depth from the end of the chain', () => {
            expect(getChainDepths(chain)).toEqual({ F: 1, M1: 2, M2: 2, S: 3 });
        });
    });

    describe('getSchematicLayout', () => {
        const layout = getSchematicLayout(chain);
        const boxOf = osId => layout.boxes.find(b => b.osId === osId);

        it('puts the start of the chain on the left under its heading', () => {
            expect(layout.headers.map(h => h.label)).toEqual([
                'Tier 3',
                'Tier 2',
                'Tier 1',
            ]);
            expect(boxOf('S').x).toBeLessThan(boxOf('M1').x);
            expect(boxOf('M1').x).toBe(boxOf('M2').x);
            expect(boxOf('M1').x).toBeLessThan(boxOf('F').x);
            expect(boxOf('S').x).toBe(layout.headers[0].x);
        });

        it('stacks a column and centres the shorter ones beside it', () => {
            expect(boxOf('M1').y).toBeLessThan(boxOf('M2').y);
            expect(boxOf('F').y).toBe((boxOf('M1').y + boxOf('M2').y) / 2);
        });

        it('draws one line per link and labels each location', () => {
            expect(layout.edges.map(e => e.key)).toEqual([
                'M1-F',
                'M2-F',
                'S-M1',
            ]);
            expect(boxOf('F')).toMatchObject({
                name: 'Factory',
                sub: 'Vietnam',
            });
        });

        it('orders a column by where its customers sit', () => {
            // Two factories; the mill listed first supplies the second one.
            const crossed = {
                ...chain,
                nodes: [
                    node('F1', 'Factory One', '1'),
                    node('F2', 'Factory Two', '1'),
                    node('MA', 'Mill A', '2'),
                    node('MB', 'Mill B', '2'),
                ],
                links: [
                    ['MA', 'F2'],
                    ['MB', 'F1'],
                ],
            };
            const {boxes} = getSchematicLayout(crossed);
            const y = osId => boxes.find(b => b.osId === osId).y;

            expect(y('MB')).toBeLessThan(y('MA'));
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

    describe('building a chain', () => {
        const build = () => {
            let draft = makeEmptyChain();
            draft = addChainLocation(draft, { osId: 'F', name: 'Factory' });
            draft = addChainLocation(draft, { osId: 'M', name: 'Mill' });
            draft = addChainLocation(draft, { osId: 'S', name: 'Spinner' });
            draft = addChainLink(draft, 'M', 'F');
            return addChainLink(draft, 'S', 'M');
        };

        it('adds each location once', () => {
            const draft = addChainLocation(build(), {
                osId: 'F',
                name: 'Factory',
            });

            expect(draft.nodes.map(n => n.os_id)).toEqual(['F', 'M', 'S']);
        });

        it('adds each link once and removes it', () => {
            const draft = addChainLink(build(), 'M', 'F');

            expect(draft.links).toEqual([
                ['M', 'F'],
                ['S', 'M'],
            ]);
            expect(removeChainLink(draft, 'M', 'F').links).toEqual([
                ['S', 'M'],
            ]);
        });

        it('removes a location along with its links', () => {
            const draft = removeChainLocation(build(), 'M');

            expect(draft.nodes.map(n => n.os_id)).toEqual(['F', 'S']);
            expect(draft.links).toEqual([]);
        });

        it('sets what happens at a location', () => {
            const draft = setChainLocationStage(build(), 'M', 'Weaving');

            expect(draft.nodes[1].stage).toBe('Weaving');
            expect(draft.nodes[0].stage).toBe('');
        });

        it('spots links that loop', () => {
            expect(chainLinksLoop(build().links)).toBe(false);
            expect(chainLinksLoop([...build().links, ['F', 'S']])).toBe(true);
            expect(
                chainLinksLoop([
                    ['A', 'C'],
                    ['B', 'C'],
                    ['A', 'B'],
                ]),
            ).toBe(false);
        });

        it('only offers links that are new and would not loop', () => {
            const draft = build();
            const offered = osId =>
                getPossibleCustomers(draft, osId).map(n => n.os_id);

            // The spinner already supplies the mill; it could also supply
            // the factory directly.
            expect(offered('S')).toEqual(['F']);
            // The factory is the end of the chain: supplying either of the
            // others would loop.
            expect(offered('F')).toEqual([]);
        });

        it('reverses a link unless that would loop', () => {
            expect(reverseChainLink(build(), 'S', 'M').links).toEqual([
                ['M', 'F'],
                ['M', 'S'],
            ]);

            const direct = addChainLink(build(), 'S', 'F');
            // S -> M -> F already: F -> S would loop.
            expect(reverseChainLink(direct, 'S', 'F')).toBe(direct);
        });

        describe('clicking facilities', () => {
            const factory = { osId: 'F', name: 'Factory' };
            const mill = { osId: 'M', name: 'Mill' };
            const spinner = { osId: 'S', name: 'Spinner' };

            it('adds and selects the first facility clicked', () => {
                const result = clickChainLocation(
                    makeEmptyChain(),
                    null,
                    factory,
                );

                expect(result.chain.nodes.map(n => n.os_id)).toEqual(['F']);
                expect(result.selectedId).toBe('F');
            });

            it('links the next facility clicked as a supplier and moves on to it', () => {
                let result = clickChainLocation(makeEmptyChain(), null, factory);
                result = clickChainLocation(result.chain, 'F', mill);
                result = clickChainLocation(result.chain, 'M', spinner);

                expect(result.chain.links).toEqual([
                    ['M', 'F'],
                    ['S', 'M'],
                ]);
                expect(result.selectedId).toBe('S');
            });

            it('links the same way whatever tiers the facilities have', () => {
                // Built from the mill towards the factory: the factory is
                // clicked second, so it is the supplier, as the click says.
                let result = clickChainLocation(makeEmptyChain(), null, mill);
                result = clickChainLocation(result.chain, 'M', factory);

                expect(result.chain.links).toEqual([['F', 'M']]);
            });

            it('deselects the selected location when it is clicked again', () => {
                const result = clickChainLocation(build(), 'M', mill);

                expect(result.selectedId).toBeNull();
                expect(result.chain).toEqual(build());
            });

            it('only selects a location already linked to the selected one', () => {
                const result = clickChainLocation(build(), 'M', factory);

                expect(result.selectedId).toBe('F');
                expect(result.chain.links).toEqual(build().links);
            });

            it('refuses a link that would loop, and does not reverse it', () => {
                // S -> M -> F. With the spinner selected, the factory is
                // clicked: "factory supplies spinner" would loop.
                const before = build();
                const result = clickChainLocation(before, 'S', factory);

                expect(result.chain).toBe(before);
                expect(result.selectedId).toBe('S');
                expect(result.message).toMatch(/Factory cannot supply/);
            });

            it('refuses a facility once the chain is full', () => {
                const full = {
                    ...makeEmptyChain(),
                    nodes: Array.from({ length: 60 }, (_, i) => ({
                        os_id: `N${i}`,
                        name: `N${i}`,
                        stage: '',
                    })),
                };
                const result = clickChainLocation(full, 'N0', factory);

                expect(result.chain).toBe(full);
                expect(result.message).toMatch(/at most 60/);
            });
        });

        it('knows when a chain has unsaved changes', () => {
            const opened = build();

            expect(chainHasChanges({ ...opened }, opened)).toBe(false);
            expect(
                chainHasChanges({ ...opened, name: 'Jacket' }, opened),
            ).toBe(true);
            expect(
                chainHasChanges(removeChainLink(opened, 'S', 'M'), opened),
            ).toBe(true);
        });

        it('undoes a change to the structure and keeps text typed since', () => {
            const before = build();
            const step = { nodes: before.nodes, links: before.links };
            // A location is removed, then another is described.
            let after = removeChainLocation(before, 'S');
            after = setChainLocationStage(after, 'M', 'Weaving');
            after = { ...after, name: 'Jacket' };

            const undone = restoreChainStructure(after, step);

            expect(chainStructureKey(undone)).toBe(chainStructureKey(before));
            expect(chainStructureKey(after)).not.toBe(
                chainStructureKey(before),
            );
            expect(undone.nodes[1].stage).toBe('Weaving');
            expect(undone.name).toBe('Jacket');
        });

        it('does not count typing as a change to the structure', () => {
            const before = build();

            expect(
                chainStructureKey(setChainLocationStage(before, 'M', 'Weaving')),
            ).toBe(chainStructureKey(before));
        });

        it('moves a chain up or down the list', () => {
            const chains = [{ id: 1 }, { id: 2 }, { id: 3 }];
            const ids = list => list.map(c => c.id);

            expect(ids(moveChain(chains, 3, -1))).toEqual([1, 3, 2]);
            expect(ids(moveChain(chains, 1, 1))).toEqual([2, 1, 3]);
            expect(moveChain(chains, 1, -1)).toBe(chains);
            expect(moveChain(chains, 3, 1)).toBe(chains);
        });

        it('sends the API the chain without display names', () => {
            const draft = {
                ...setChainLocationStage(build(), 'F', 'Sewing'),
                name: ' Jacket ',
            };

            expect(formatChainForAPI(draft)).toEqual({
                name: 'Jacket',
                description: '',
                product_url: '',
                color: '#c0392b',
                is_published: false,
                nodes: [
                    { os_id: 'F', stage: 'Sewing' },
                    { os_id: 'M', stage: '' },
                    { os_id: 'S', stage: '' },
                ],
                links: [
                    ['M', 'F'],
                    ['S', 'M'],
                ],
            });
        });

        it('collects every message from an API error', () => {
            expect(
                getChainErrorMessages({
                    non_field_errors: ['The links cannot loop.'],
                    product_url: ['Enter a web address.'],
                }),
            ).toEqual(['The links cannot loop.', 'Enter a web address.']);
            expect(getChainErrorMessages(undefined)).toEqual([
                'The supply chain could not be saved.',
            ]);
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
