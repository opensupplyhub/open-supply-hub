/* eslint-env jest */
import {
    pendingClaimApiToFormData,
    buildPendingClaimPatchPayload,
} from '../../components/PendingClaimEdit/utils';

const APPAREL_ENTRY = Object.freeze({
    section: 'C - Manufacturing',
    division: '14 - Manufacture of wearing apparel',
    group: '141 - Manufacture of wearing apparel, except fur apparel',
    class: '1410 - Manufacture of wearing apparel, except fur apparel',
});

describe('pending claim edit ISIC mapping', () => {
    it('loads stored ISIC entries as picker options', () => {
        const formData = pendingClaimApiToFormData({
            your_name: 'Name',
            isic_4: [APPAREL_ENTRY],
            isic_5: null,
        });

        expect(formData.isic4).toEqual([
            {
                value: 'class:1410',
                label: 'Manufacture of wearing apparel, except fur apparel',
            },
        ]);
        expect(formData.isic5).toEqual([]);
    });

    it('loads a claim without ISIC fields as empty pickers', () => {
        const formData = pendingClaimApiToFormData({ your_name: 'Name' });

        expect(formData.isic4).toEqual([]);
        expect(formData.isic5).toEqual([]);
    });

    it('sends ISIC options as codes, not as option objects or titles', () => {
        const payload = buildPendingClaimPatchPayload({
            yourName: 'Name',
            isic4: [
                {
                    value: 'class:1410',
                    label: 'Manufacture of wearing apparel, except fur apparel',
                },
            ],
            isic5: [{ value: 'group:631', label: 'Computing infrastructure' }],
        });

        expect(payload.isic_4).toEqual(['class:1410']);
        expect(payload.isic_5).toEqual(['group:631']);
    });

    it('sends an empty list when every ISIC value was removed', () => {
        const payload = buildPendingClaimPatchPayload({
            yourName: 'Name',
            isic4: [],
            isic5: [],
        });

        expect(payload.isic_4).toEqual([]);
        expect(payload.isic_5).toEqual([]);
    });

    it('sends back unchanged the values it loaded', () => {
        const formData = pendingClaimApiToFormData({
            your_name: 'Name',
            isic_4: [APPAREL_ENTRY],
            isic_5: [],
        });

        const payload = buildPendingClaimPatchPayload(formData);

        expect(payload.isic_4).toEqual(['class:1410']);
        expect(payload.isic_5).toEqual([]);
    });
});
