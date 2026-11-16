import {
    SUPPLY_CHAIN_TUTORIAL_STEPS,
    hasSeenSupplyChainTutorial,
    markSupplyChainTutorialSeen,
    getEmbedSectionDescription,
    getEmbedSettingsTourSteps,
    hasSeenEmbedSettingsTour,
    markEmbedSettingsTourSeen,
} from '../../util/embeddedMap';

describe('the tour of the Embed settings', () => {
    const standardSections = [
        { id: 'style', label: 'Style' },
        { id: 'fields', label: 'Fields' },
        { id: 'code', label: 'Size and embed code' },
    ];
    const deluxeSections = [
        { id: 'style', label: 'Style' },
        { id: 'fields', label: 'Fields' },
        { id: 'spotlight', label: 'Spotlight' },
        { id: 'chains', label: 'Supply chains' },
        { id: 'code', label: 'Size and embed code' },
    ];

    it('welcomes, covers each section the contributor has, then the preview', () => {
        expect(
            getEmbedSettingsTourSteps(deluxeSections, true).map(s => s.id),
        ).toEqual([
            'welcome',
            'style',
            'fields',
            'spotlight',
            'chains',
            'code',
            'preview',
        ]);
        expect(
            getEmbedSettingsTourSteps(standardSections, false).map(s => s.id),
        ).toEqual(['welcome', 'style', 'fields', 'code', 'preview']);
    });

    it('opens the section each step is about', () => {
        const steps = getEmbedSettingsTourSteps(deluxeSections, true);

        expect(steps.find(s => s.id === 'chains')).toMatchObject({
            section: 'chains',
            title: 'Supply chains',
        });
        expect(steps[0].section).toBeNull();
        expect(steps[steps.length - 1].section).toBeNull();
    });

    it('says something at every step', () => {
        [
            ...getEmbedSettingsTourSteps(deluxeSections, true),
            ...getEmbedSettingsTourSteps(standardSections, false),
        ].forEach(step => {
            expect(step.title).toBeTruthy();
            expect(step.body).toBeTruthy();
        });
    });

    it('describes a section by what the contributor can do there', () => {
        expect(getEmbedSectionDescription('fields', true)).toMatch(
            /explain what your fields and values mean/,
        );
        expect(getEmbedSectionDescription('fields', false)).not.toMatch(
            /explain/,
        );
        expect(getEmbedSectionDescription('code', true)).toBe(
            getEmbedSectionDescription('code', false),
        );
        expect(getEmbedSectionDescription('unknown', true)).toBe('');
    });

    describe('remembering it was shown', () => {
        const makeStorage = () => {
            const values = {};
            return {
                getItem: key => (key in values ? values[key] : null),
                setItem: (key, value) => {
                    values[key] = value;
                },
            };
        };

        it('is not seen until it is closed', () => {
            const storage = makeStorage();

            expect(hasSeenEmbedSettingsTour(storage)).toBe(false);
            markEmbedSettingsTourSeen(storage);
            expect(hasSeenEmbedSettingsTour(storage)).toBe(true);
        });

        it('copes with browser storage that cannot be used', () => {
            const blocked = {
                getItem: () => {
                    throw new Error('blocked');
                },
                setItem: () => {
                    throw new Error('blocked');
                },
            };

            expect(hasSeenEmbedSettingsTour(blocked)).toBe(false);
            expect(() => markEmbedSettingsTourSeen(blocked)).not.toThrow();
        });
    });

describe('the tutorial on building a supply chain', () => {
    it('follows the order a chain is built in', () => {
        expect(SUPPLY_CHAIN_TUTORIAL_STEPS.map(step => step.id)).toEqual([
            'name',
            'first',
            'link',
            'branch',
            'fix',
            'describe',
            'schematic',
            'publish',
        ]);
    });

    it('points each step at a part of the builder', () => {
        const parts = [
            'name',
            'map',
            'undo',
            'locations',
            'schematic',
            'publish',
        ];
        SUPPLY_CHAIN_TUTORIAL_STEPS.forEach(step => {
            expect(parts).toContain(step.target);
            expect(step.title).toBeTruthy();
            expect(step.body).toBeTruthy();
        });
    });

    it('is remembered apart from the tour of the settings', () => {
        const values = {};
        const storage = {
            getItem: key => (key in values ? values[key] : null),
            setItem: (key, value) => {
                values[key] = value;
            },
        };

        markSupplyChainTutorialSeen(storage);

        expect(hasSeenSupplyChainTutorial(storage)).toBe(true);
        expect(hasSeenEmbedSettingsTour(storage)).toBe(false);
    });
});
});
