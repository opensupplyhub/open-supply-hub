import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import UserEvent from "user-event";
import SettingTabs from '../../components/Settings/SettingTabs';

import {
    PROFILE_TAB,
    EMBED_TAB,
    API_TAB,
} from '../../components/Settings/constants';

test('SettingsTabs component', () => {
    const handleTabChange = (event, tab) => {
        // Check index of clicked tab
        expect(tab).toBe(2);
    };
    const tabs = [PROFILE_TAB, EMBED_TAB, API_TAB];

    render (
            <Router>
            <SettingTabs
                value={0}
                onChange={handleTabChange}
                tabs={tabs}
            />
            </Router>
    );

    // Check component presence on the page
    const settingsTabsElem = screen.getByTestId('settings-tabs');
    expect(settingsTabsElem).toBeInTheDocument();

    // Click on 'Token' tab
    const itemClickable = screen.getByText(API_TAB);
    UserEvent.click(itemClickable);
})
