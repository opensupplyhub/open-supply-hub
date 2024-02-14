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
});

