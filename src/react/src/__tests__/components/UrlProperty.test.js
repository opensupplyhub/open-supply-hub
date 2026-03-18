import React from 'react';
import { render, screen } from '@testing-library/react';
import UrlProperty from '../../components/PartnerFields/FormatComponents/UrlProperty';

const defaultProps = {
    propertyKey: 'website',
    value: { website: 'https://example.com' },
    schemaProperties: {},
};

describe('UrlProperty', () => {
    it('renders a link with the property value as href and text', () => {
        render(<UrlProperty {...defaultProps} />);

        const link = screen.getByRole('link', {
            name: 'https://example.com',
        });
        expect(link).toHaveAttribute('href', 'https://example.com');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('returns null when property value is missing', () => {
        const { container } = render(
            <UrlProperty
                {...defaultProps}
                value={{ website: undefined }}
            />,
        );

        expect(container).toBeEmptyDOMElement();
    });

    it('displays the title from schema before the link', () => {
        render(
            <UrlProperty
                {...defaultProps}
                schemaProperties={{ website: { title: 'Website' } }}
            />,
        );

        expect(screen.getByText(/Website:/)).toBeInTheDocument();
        expect(screen.getByRole('link')).toHaveAttribute(
            'href',
            'https://example.com',
        );
    });

    it('uses _text property as link text when defined in schema', () => {
        render(
            <UrlProperty
                {...defaultProps}
                value={{
                    website: 'https://example.com',
                    website_text: 'Visit Site',
                }}
                schemaProperties={{
                    website: {},
                    website_text: { type: 'string' },
                }}
            />,
        );

        const link = screen.getByRole('link', { name: 'Visit Site' });
        expect(link).toHaveAttribute('href', 'https://example.com');
    });

    it('falls back to schema default when value is missing', () => {
        render(
            <UrlProperty
                {...defaultProps}
                value={{}}
                schemaProperties={{
                    website: { default: 'https://default.com' },
                }}
            />,
        );

        const link = screen.getByRole('link', {
            name: 'https://default.com',
        });
        expect(link).toHaveAttribute('href', 'https://default.com');
    });

    it('uses schemaProperty.text as link text when defined', () => {
        render(
            <UrlProperty
                {...defaultProps}
                schemaProperties={{
                    website: { text: 'Custom Link Text' },
                }}
            />,
        );

        const link = screen.getByRole('link', { name: 'Custom Link Text' });
        expect(link).toHaveAttribute('href', 'https://example.com');
    });
});
