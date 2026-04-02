import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import ProductionLocationDetailsDataSourcesInfo from '../../components/ProductionLocation/Heading/DataSourcesInfo/DataSourcesInfo';

jest.mock('../../components/Contribute/DialogTooltip', () => {
    function MockDialogTooltip({ childComponent }) {
        return <>{childComponent}</>;
    }
    return MockDialogTooltip;
});

const theme = createMuiTheme();

const renderDataSourcesInfo = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <ProductionLocationDetailsDataSourcesInfo {...props} />
        </MuiThemeProvider>,
    );

describe('ProductionLocation DataSourcesInfo', () => {
    test('renders without crashing', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByRole('heading', { name: 'Data Sources' }),
        ).toBeInTheDocument();
    });

    test('renders section title "Understanding Data Sources"', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByRole('heading', { level: 3, name: 'Data Sources' }),
        ).toBeInTheDocument();
    });

    test('shows expand-more icon when subsection info is collapsed', () => {
        renderDataSourcesInfo();

        expect(
            screen.getByTestId('data-sources-expand-more'),
        ).toBeInTheDocument();
        expect(
            screen.queryByTestId('data-sources-expand-less'),
        ).not.toBeInTheDocument();
    });

    test('shows expand-less icon when subsection info is expanded', () => {
        renderDataSourcesInfo();

        fireEvent.click(screen.getByTestId('data-sources-expand-more'));

        expect(
            screen.getByTestId('data-sources-expand-less'),
        ).toBeInTheDocument();
        expect(
            screen.queryByTestId('data-sources-expand-more'),
        ).not.toBeInTheDocument();
    });

    test('renders all three data source items', () => {
        renderDataSourcesInfo();

        expect(screen.getByText('Claimed')).toBeInTheDocument();
        expect(screen.getByText('Crowdsourced')).toBeInTheDocument();
        expect(screen.getByText('Partner Data')).toBeInTheDocument();
    });

    test('expand control shows subsection text when opened', () => {
        renderDataSourcesInfo();

        expect(
            screen.queryByText(/General information & operational details submitted by production location/),
        ).not.toBeInTheDocument();

        fireEvent.click(screen.getByTestId('data-sources-expand-more'));

        expect(
            screen.getByText(/General information & operational details submitted by production location/),
        ).toBeInTheDocument();
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

        const wrapper = container.querySelector('.custom-class');
        expect(wrapper).toBeInTheDocument();
    });
});
