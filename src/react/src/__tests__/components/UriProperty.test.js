import React from 'react';
import { render, screen } from '@testing-library/react';
import UriProperty from '../../components/PartnerFields/FormatComponents/UriProperty';

const defaultProps = {
    propertyKey: 'link',
    value: { link: 'https://example.com/resource' },
    schemaProperties: {},
};

describe('UriProperty', () => {
    it('renders a link with the property value as href and text', () => {
        render(<UriProperty {...defaultProps} />);

        const link = screen.getByRole('link', {
            name: 'https://example.com/resource',
        });
        expect(link).toHaveAttribute('href', 'https://example.com/resource');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('returns null when property value is missing and no default', () => {
        const { container } = render(
            <UriProperty {...defaultProps} value={{}} schemaProperties={{}} />,
        );

        expect(container).toBeEmptyDOMElement();
    });

    it('falls back to schema default when value is missing', () => {
        render(
            <UriProperty
                {...defaultProps}
                value={{}}
                schemaProperties={{
                    link: { default: 'https://default-uri.com' },
                }}
            />,
        );

        const link = screen.getByRole('link', {
            name: 'https://default-uri.com',
        });
        expect(link).toHaveAttribute('href', 'https://default-uri.com');
    });

    it('displays the title from schema before the link', () => {
        render(
            <UriProperty
                {...defaultProps}
                schemaProperties={{ link: { title: 'Resource Link' } }}
            />,
        );

        expect(screen.getByText(/Resource Link:/)).toBeInTheDocument();
        expect(screen.getByRole('link')).toHaveAttribute(
            'href',
            'https://example.com/resource',
        );
    });
});
