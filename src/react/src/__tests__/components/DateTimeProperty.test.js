import React from 'react';
import { render, screen } from '@testing-library/react';
import moment from 'moment';
import DateTimeProperty from '../../components/PartnerFields/FormatComponents/DateTimeProperty';

const defaultProps = {
    propertyKey: 'created_at',
    value: { created_at: '2024-06-15T14:30:00Z' },
    schemaProperties: { created_at: {} },
};

describe('DateTimeProperty', () => {
    it('renders a formatted date-time from value', () => {
        render(<DateTimeProperty {...defaultProps} />);

        const expected = moment('2024-06-15T14:30:00Z').format('LLL');
        expect(screen.getByText(expected)).toBeInTheDocument();
    });

    it('falls back to schema default datetime when value is missing', () => {
        render(
            <DateTimeProperty
                {...defaultProps}
                value={{}}
                schemaProperties={{
                    created_at: { default: '2024-01-15T09:00:00Z' },
                }}
            />,
        );

        const expected = moment('2024-01-15T09:00:00Z').format('LLL');
        expect(screen.getByText(expected)).toBeInTheDocument();
    });

    it('displays the title from schema', () => {
        render(
            <DateTimeProperty
                {...defaultProps}
                schemaProperties={{
                    created_at: { title: 'Created At' },
                }}
            />,
        );

        expect(screen.getByText(/Created At:/)).toBeInTheDocument();
    });
});
