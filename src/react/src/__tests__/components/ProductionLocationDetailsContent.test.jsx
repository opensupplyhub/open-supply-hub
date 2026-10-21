import React from 'react';
import { MemoryRouter } from 'react-router-dom';

import ProductionLocationDetailsContent from '../../components/ProductionLocation/ProductionLocationDetailsContent/ProductionLocationDetailsContent';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsMap/ProductionLocationDetailsMap',
    () => () => <div data-testid="details-map" />,
);
jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields',
    () => () => <div data-testid="general-fields">General Information</div>,
);
jest.mock(
    '../../components/ProductionLocation/ClaimSection/ClaimDataContainer/ClaimDataContainer',
    () => () => null,
);
jest.mock(
    '../../components/ProductionLocation/PartnerSection/PartnerDataContainer/PartnerDataContainer',
    () => () => null,
);

/*
The OS ID and the data labels legend have to line up with the General
Information / map row below them (OSDEV-3239). They do that by sharing that
row's Grid columns rather than by matching numbers that happen to look close,
so compare the two rows instead of asserting a width.
*/
/*
JSS appends a counter to every generated class, so match on the rule name
(`MuiGrid-grid-lg-7-123`) rather than on an exact class.
*/
const ruleNames = element =>
    [...element.classList].map(name => name.replace(/-\d+$/, ''));

/*
The `lg` columns are what put the two panels side by side and decide where they
line up; the identity row also declares `xs={12}` so it is explicitly full
width below `md`, which the row below leaves to the flex default.
*/
const lgColumn = element =>
    ruleNames(element).find(name => /^MuiGrid-grid-lg-/.test(name));

const gridItemFor = node => {
    let current = node;
    while (current && !ruleNames(current).includes('MuiGrid-item')) {
        current = current.parentElement;
    }
    return current;
};

describe('ProductionLocationDetailsContent identity row', () => {
    const data = {
        properties: {
            os_id: 'CN2023146Q0ZV4R',
            claim_info: null,
        },
    };

    const renderContent = () =>
        renderWithProviders(
            <MemoryRouter>
                <ProductionLocationDetailsContent data={data} />
            </MemoryRouter>,
        );

    test('puts the OS ID and the data labels legend in one row', () => {
        const { getByTestId } = renderContent();

        const osIdItem = gridItemFor(getByTestId('os-id'));
        const labelsItem = gridItemFor(
            getByTestId('understanding-data-sources-section'),
        );

        expect(osIdItem).not.toBeNull();
        expect(labelsItem).not.toBeNull();
        expect(osIdItem.parentElement).toBe(labelsItem.parentElement);
        expect(ruleNames(osIdItem.parentElement)).toContain(
            'MuiGrid-container',
        );
    });

    test('gives the identity row the same columns as the row below it', () => {
        const { getByTestId } = renderContent();

        const osIdItem = gridItemFor(getByTestId('os-id'));
        const labelsItem = gridItemFor(
            getByTestId('understanding-data-sources-section'),
        );
        const generalFieldsItem = gridItemFor(getByTestId('general-fields'));
        const mapItem = gridItemFor(getByTestId('details-map'));

        expect(lgColumn(osIdItem)).toBe(lgColumn(generalFieldsItem));
        expect(lgColumn(labelsItem)).toBe(lgColumn(mapItem));
        expect(ruleNames(osIdItem)).toContain('MuiGrid-grid-xs-12');
        expect(ruleNames(labelsItem)).toContain('MuiGrid-grid-xs-12');
    });
});
