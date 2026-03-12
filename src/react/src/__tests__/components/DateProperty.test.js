import React from 'react';
import { render, screen } from '@testing-library/react';
import moment from 'moment';
import DateProperty from '../../components/PartnerFields/FormatComponents/DateProperty';

const defaultProps = {
    propertyKey: 'start_date',
    value: { start_date: '2024-06-15' },
    schemaProperties: { start_date: {} },
};

describe('DateProperty', () => {
    it('renders a formatted date from value', () => {
        render(<DateProperty {...defaultProps} />);

        const expected = moment('2024-06-15').format('LL');
        expect(screen.getByText(expected)).toBeInTheDocument();
    });

    it('falls back to schema default date when value is missing', () => {
        render(
            <DateProperty
                {...defaultProps}
                value={{}}
                schemaProperties={{
                    start_date: { default: '2024-01-15' },
                }}
            />,
        );

        const expected = moment('2024-01-15').format('LL');
        expect(screen.getByText(expected)).toBeInTheDocument();
    });

    it('displays the title from schema', () => {
        render(
            <DateProperty
                {...defaultProps}
                schemaProperties={{
                    start_date: { title: 'Start Date' },
                }}
            />,
        );

        expect(screen.getByText(/Start Date:/)).toBeInTheDocument();
    });
});
