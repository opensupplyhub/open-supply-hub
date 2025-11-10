import React from 'react';
import { render, screen } from '@testing-library/react';
import FacilityDetailsDetail from './../../components/FacilityDetailsDetail';

describe('FacilityDetailsDetail', () => {
    const facilityLat = '33.7862099'
    const facilityLng = '119.2787399'
    test('renders primary text correctly without latitude and longitude', () => {
        const primary = `${facilityLat}, ${facilityLng}`;
        render(
            <FacilityDetailsDetail primary={primary} />
        );
        expect(screen.getByText(primary)).toBeInTheDocument();

        const latitudeText = screen.queryByText('Latitude');
        expect(latitudeText).not.toBeInTheDocument();
        const longitudeText = screen.queryByText('Longitude');
        expect(longitudeText).not.toBeInTheDocument();
    });

    test('renders location labeled component correctly with latitude before longitude', () => {
        const locationLabeled = (
            <>
                {`Latitude: ${facilityLat}`}
                <br />
                {`Longitude: ${facilityLng}`}
            </>
        );
        const { container } = render(
            <FacilityDetailsDetail locationLabeled={locationLabeled} />
        );
    
        const latitudeRegex = new RegExp(`Latitude: ${facilityLat}`);
        const longitudeRegex = new RegExp(`Longitude: ${facilityLng}`);
    
        const latitudeElements = screen.getAllByText(latitudeRegex);
        const longitudeElements = screen.getAllByText(longitudeRegex);
    
        expect(latitudeElements.length).toBeGreaterThan(0);
        expect(longitudeElements.length).toBeGreaterThan(0);
    
        // Check if the latitude text appears before the longitude text
        const allText = container.textContent;
        const latitudeIndex = allText.indexOf(`Latitude: ${facilityLat}`);
        const longitudeIndex = allText.indexOf(`Longitude: ${facilityLng}`);
    
        expect(latitudeIndex).toBeLessThan(longitudeIndex);
    });

    test('renders with sourceBy HTML content', () => {
        const props = {
            primary: 'Test Primary',
            sourceBy: '<strong>Climate TRACE</strong> API',
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                sourceText: 'sourceText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        expect(screen.getByText('Test Primary')).toBeInTheDocument();

        const sourceElement = container.querySelector('.sourceText');
        expect(sourceElement).toBeInTheDocument();
        expect(sourceElement.innerHTML).toBe('<strong>Climate TRACE</strong> API');
    });

    test('renders sourceBy with link HTML', () => {
        const props = {
            primary: 'Test Primary',
            sourceBy: 'Data from <a href="https://example.com">Climate TRACE</a>',
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                sourceText: 'sourceText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        const sourceElement = container.querySelector('.sourceText');
        expect(sourceElement).toBeInTheDocument();
        expect(sourceElement.innerHTML).toContain('<a href="https://example.com">');
        expect(sourceElement.innerHTML).toContain('Climate TRACE');
    });

    test('does not render sourceBy when null', () => {
        const props = {
            primary: 'Test Primary',
            sourceBy: null,
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                sourceText: 'sourceText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        expect(screen.getByText('Test Primary')).toBeInTheDocument();

        const sourceElement = container.querySelector('.sourceText');
        expect(sourceElement).not.toBeInTheDocument();
    });

    test('does not render sourceBy when empty string', () => {
        const props = {
            primary: 'Test Primary',
            sourceBy: '',
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                sourceText: 'sourceText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        const sourceElement = container.querySelector('.sourceText');
        expect(sourceElement).not.toBeInTheDocument();
    });

    test('renders unit text inline with primary value', () => {
        const props = {
            primary: '100',
            unit: 'kg',
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        const primaryElement = container.querySelector('.primaryText');
        expect(primaryElement).toBeInTheDocument();
        expect(primaryElement.textContent).toBe('100kg');

        const unitElement = container.querySelector('.unitText');
        expect(unitElement).toBeInTheDocument();
        expect(unitElement.textContent).toBe('kg');
    });

    test('does not render unit text when unit is null', () => {
        const props = {
            primary: 'Test Primary',
            unit: null,
            classes: {
                detailsContainer: 'detailsContainer',
                primaryText: 'primaryText',
                unitText: 'unitText',
            },
        };

        const { container } = render(<FacilityDetailsDetail {...props} />);

        expect(container.querySelector('.unitText')).not.toBeInTheDocument();
    });
});

