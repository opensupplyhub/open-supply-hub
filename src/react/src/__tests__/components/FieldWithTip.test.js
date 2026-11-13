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
        // The app's breakpoints (see App.jsx).
        const theme = createMuiTheme({
            breakpoints: {
                values: { xs: 0, sm: 700, md: 900, lg: 1280, xl: 1920 },
            },
        });
        const rules = styles(theme);
        const wide = theme.breakpoints.up('lg');

        test('the wide rule starts exactly where the old full-width rule ended', () => {
            // The wrappers this replaces were full width under
            // down('md') and capped at 528px above it.
            expect(theme.breakpoints.down('md')).toBe(
                '@media (max-width:1279.95px)',
            );
            expect(wide).toBe('@media (min-width:1280px)');
        });

        test('below lg the field and the tip are full width with no cap', () => {
            const { [wide]: wideRoot, ...narrowRoot } = rules.root;
            const { [wide]: wideField, ...narrowField } = rules.field;
            const { [wide]: wideTip, ...narrowTip } = rules.tip;

            expect(wideRoot).toBeDefined();
            expect(wideField).toBeDefined();
            expect(wideTip).toBeDefined();
            expect(narrowRoot).toEqual({ width: '100%', position: 'relative' });
            expect(narrowField).toEqual({});
            expect(narrowTip).toEqual({ margin: '8px 0 12px 0' });
        });

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
