import React from 'react';
import { render } from '@testing-library/react';
import { createMuiTheme } from '@material-ui/core/styles';
import FieldWithTip from '../../components/InitialClaimFlow/Shared/FieldWithTip/FieldWithTip';
import styles from '../../components/InitialClaimFlow/Shared/FieldWithTip/styles';

describe('FieldWithTip component', () => {
    test('renders the heading, then the control, then the tip', () => {
        const { container } = render(
            <FieldWithTip
                heading={<h4>Heading</h4>}
                tip={<aside>Tip</aside>}
            >
                <input aria-label="Control" />
            </FieldWithTip>,
        );

        const order = Array.from(
            container.querySelectorAll('h4, input, aside'),
        ).map(element => element.tagName);

        expect(order).toEqual(['H4', 'INPUT', 'ASIDE']);
    });

    describe('layout', () => {
        const theme = createMuiTheme();
        const rules = styles(theme);
        const wide = theme.breakpoints.up('lg');

        test('puts the tip beside the control in an equal column on wide screens', () => {
            expect(rules.root[wide]).toEqual({
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 528px) minmax(0, 528px)',
                columnGap: '24px',
            });
            expect(rules.field[wide]).toEqual({ gridColumn: 1 });
            expect(rules.tip[wide]).toEqual({
                gridColumn: 2,
                gridRow: 2,
                alignSelf: 'start',
                margin: 0,
            });
        });

        test('keeps the tip in normal page flow', () => {
            expect(rules.root.display).toBeUndefined();
            expect(rules.tip.position).toBeUndefined();
            expect(rules.tip[wide].position).toBeUndefined();
        });
    });
});
