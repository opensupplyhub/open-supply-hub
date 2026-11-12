import React from 'react';
import { render } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import EmbedFieldValue from '../../components/EmbedFieldValue';

const renderField = (props, embed) =>
    render(
        <MuiThemeProvider theme={createMuiTheme({ embed })}>
            <EmbedFieldValue label="Initiatives" {...props} />
        </MuiThemeProvider>,
    );

describe('EmbedFieldValue', () => {
    it('renders nothing without a value', () => {
        const { container } = renderField({ value: '  ' });

        expect(container.textContent).toBe('');
    });

    it('renders text by default', () => {
        const { getByTestId } = renderField({ value: 'HERhealth' });

        expect(getByTestId('embed-field-text').textContent).toBe(
            'Initiatives: HERhealth',
        );
    });

    it('renders one tag per value', () => {
        const { getByTestId } = renderField({
            value: 'HERhealth|RISE',
            displayAs: 'tags',
        });
        const tags = getByTestId('embed-field-tags').querySelectorAll(
            'span + span',
        );

        expect([...tags].map(tag => tag.textContent)).toEqual([
            'HERhealth',
            'RISE',
        ]);
    });

    it('renders a blurb as text, not as HTML', () => {
        const { getByTestId } = renderField({
            value: '<b>Since 2019</b> we have worked together.',
            displayAs: 'blurb',
        });
        const blurb = getByTestId('embed-field-blurb');

        expect(blurb.textContent).toContain('<b>Since 2019</b>');
        expect(blurb.querySelector('b')).toBeNull();
    });

    it('renders with an embed accent color set', () => {
        const { getByTestId } = renderField(
            { value: 'HERhealth', displayAs: 'tags' },
            { accentColor: '#f2a900', headingFont: null, cornerRadius: null },
        );

        expect(getByTestId('embed-field-tags')).toBeTruthy();
    });
});
