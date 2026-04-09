import React from 'react';
import { render, screen } from '@testing-library/react';
import DefaultProperty from '../../components/PartnerFields/TypeComponents/DefaultProperty/DefaultProperty';

const defaultProps = {
    propertyKey: 'status',
    value: { status: 'active' },
    schemaProperties: { status: { title: 'Status' } },
};

describe('DefaultProperty', () => {
    it('renders the string value from value object', () => {
        render(<DefaultProperty {...defaultProps} />);

        expect(screen.getByText('active')).toBeInTheDocument();
    });

    it('falls back to schema default when value is missing', () => {
        render(
            <DefaultProperty
                {...defaultProps}
                value={{}}
                schemaProperties={{
                    status: { title: 'Status', default: 'pending' },
                }}
            />,
        );

        expect(screen.getByText('pending')).toBeInTheDocument();
    });

    it('displays the title from schema', () => {
        render(<DefaultProperty {...defaultProps} />);

        expect(screen.getByText(/Status:/)).toBeInTheDocument();
    });
});
