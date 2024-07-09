import React from 'react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimFacilityAdditionalData from '../../components/ClaimFacilityAdditionalData';

describe('ClaimFacilityAdditionalData', () => {
    it('renders without crashing', () => {
        renderWithProviders(
            <ClaimFacilityAdditionalData 
                sectors = {["Apparel", "Footwear", "Home Furnishings"]}
                numberOfWorkers = {0}
                updateNumberOfWorkers = {() => {}}
                localLanguageName = ""
                updateLocalLanguageName = {() => {}}
                sectorOptions = {['Apparel', 'Footwear', 'Home Furnishings']}
                fetchSectors = {() => {}}
                fetching = {false}
            />
        )
    });
});


