import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import ProductionLocationDetailsDataSourcesInfo from '../../components/ProductionLocation/Heading/DataSourcesInfo/DataSourcesInfo';

const theme = createMuiTheme();

const CLAIMED_DEFINITION =
    /General information & operational details submitted by production location/;

const renderDataSourcesInfo = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <ProductionLocationDetailsDataSourcesInfo {...props} />
        </MuiThemeProvider>,
    );

describe('ProductionLocation DataSourcesInfo', () => {
    test('renders section title "Understanding Data Labels"', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByRole('heading', {
                level: 3,
                name: 'Understanding Data Labels',
            }),
        ).toBeInTheDocument();
    });

    test('renders all three data labels as buttons', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByRole('button', { name: 'Claimed' }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: 'Crowdsourced' }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: 'Spotlight Partners' }),
        ).toBeInTheDocument();
    });

    test('shows the list slide and hides the detail slide by default', () => {
        renderDataSourcesInfo();

        expect(screen.getByTestId('data-labels-list')).toHaveAttribute(
            'aria-hidden',
            'false',
        );
        expect(screen.getByTestId('data-labels-detail')).toHaveAttribute(
            'aria-hidden',
            'true',
        );
        expect(screen.queryByText(CLAIMED_DEFINITION)).not.toBeInTheDocument();
    });

    test('opening a data label reveals only that label definition', () => {
        renderDataSourcesInfo();

        fireEvent.click(screen.getByRole('button', { name: 'Claimed' }));

        expect(screen.getByText(CLAIMED_DEFINITION)).toBeInTheDocument();
        expect(
            screen.queryByText(/shared by supply chain stakeholders/),
        ).not.toBeInTheDocument();
        expect(screen.getByTestId('data-labels-detail')).toHaveAttribute(
            'aria-hidden',
            'false',
        );
        expect(screen.getByTestId('data-labels-list')).toHaveAttribute(
            'aria-hidden',
            'true',
        );
    });

    test('opening a data label keeps its Learn more link', () => {
        renderDataSourcesInfo();

        fireEvent.click(
            screen.getByRole('button', { name: 'Spotlight Partners' }),
        );

        expect(screen.getByRole('link', { name: /Learn more/ })).toHaveAttribute(
            'href',
            'https://info.opensupplyhub.org/spotlight',
        );
    });

    test('back control returns to the list slide', () => {
        renderDataSourcesInfo();

        fireEvent.click(screen.getByRole('button', { name: 'Crowdsourced' }));
        fireEvent.click(
            screen.getByRole('button', { name: 'Back to Data Labels' }),
        );

        expect(screen.getByTestId('data-labels-list')).toHaveAttribute(
            'aria-hidden',
            'false',
        );
        expect(screen.getByTestId('data-labels-detail')).toHaveAttribute(
            'aria-hidden',
            'true',
        );
    });

    test('moves focus with the panel so keyboard users follow it', () => {
        renderDataSourcesInfo();

        const crowdsourced = screen.getByRole('button', {
            name: 'Crowdsourced',
        });
        fireEvent.click(crowdsourced);

        const backButton = screen.getByTestId('data-label-back');
        expect(backButton).toHaveFocus();

        fireEvent.click(backButton);

        expect(crowdsourced).toHaveFocus();
    });

    test('takes the off-screen slide out of the tab order', () => {
        renderDataSourcesInfo();

        const claimed = screen.getByRole('button', { name: 'Claimed' });
        expect(claimed).toHaveAttribute('tabindex', '0');
        expect(screen.getByTestId('data-label-back')).toHaveAttribute(
            'tabindex',
            '-1',
        );

        fireEvent.click(claimed);

        expect(claimed).toHaveAttribute('tabindex', '-1');
        expect(screen.getByTestId('data-label-back')).toHaveAttribute(
            'tabindex',
            '0',
        );
    });

    test('names the detail panel after the label it describes', () => {
        renderDataSourcesInfo();

        fireEvent.click(screen.getByRole('button', { name: 'Claimed' }));

        expect(
            screen.getByRole('group', { name: 'Claimed data label' }),
        ).toBeInTheDocument();
    });

    test('points each label at the detail panel it expands', () => {
        renderDataSourcesInfo();

        const claimed = screen.getByRole('button', { name: 'Claimed' });
        const crowdsourced = screen.getByRole('button', {
            name: 'Crowdsourced',
        });
        const panelId = screen
            .getByTestId('data-labels-detail')
            .getAttribute('id');

        expect(claimed).toHaveAttribute('aria-controls', panelId);
        expect(claimed).toHaveAttribute('aria-expanded', 'false');

        fireEvent.click(claimed);

        expect(claimed).toHaveAttribute('aria-expanded', 'true');
        expect(crowdsourced).toHaveAttribute('aria-expanded', 'false');
    });

    test('renders info button for data sources tooltip', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByTestId('data-sources-info-tooltip'),
        ).toBeInTheDocument();
    });

    test('applies custom className when provided', () => {
        const { container } = renderDataSourcesInfo({
            className: 'custom-class',
        });

        expect(container.querySelector('.custom-class')).toBeInTheDocument();
    });
});
