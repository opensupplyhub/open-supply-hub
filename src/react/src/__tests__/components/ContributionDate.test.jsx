import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import ContributionDate from '../../components/ProductionLocation/Shared/ContributionDate/ContributionDate';

const theme = createMuiTheme();

const renderContributionDate = (date = '2024-06-15T12:00:00Z') =>
    render(
        <MuiThemeProvider theme={theme}>
            <ContributionDate date={date} />
        </MuiThemeProvider>,
    );

describe('ContributionDate', () => {
    test('renders with data-testid', () => {
        renderContributionDate();

        expect(screen.getByTestId('contribution-date')).toBeInTheDocument();
    });

    test('renders schedule icon inside date container', () => {
        renderContributionDate();

        const dateElement = screen.getByTestId('contribution-date');
        expect(dateElement.querySelector('svg')).toBeInTheDocument();
    });

    test('accepts Date instances', () => {
        renderContributionDate(new Date('2024-01-01T00:00:00Z'));

        expect(screen.getByTestId('contribution-date')).toBeInTheDocument();
    });
});
