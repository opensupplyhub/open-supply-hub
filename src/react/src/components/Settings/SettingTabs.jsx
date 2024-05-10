import React, { PureComponent } from 'react';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import PropTypes from 'prop-types';

class SettingTabs extends PureComponent {
    render() {
        const { value, onChange, tabs } = this.props;

        return (
            <Tabs
                data-testid="settings-tabs"
                value={value}
                onChange={onChange}
                centered
                classes={{
                    root: 'settings-tabs',
                    indicator: 'settings-tabs-indicator',
                }}
            >
                {tabs.map(tab => (
                    <Tab
                        label={tab}
                        key={tab}
                        classes={{
                            label: 'settings-tabs-label',
                        }}
                    />
                ))}
            </Tabs>
        );
    }
}

SettingTabs.propTypes = {
    value: PropTypes.number.isRequired,
    onChange: PropTypes.func.isRequired,
    tabs: PropTypes.array.isRequired, // eslint-disable-line react/forbid-prop-types
};

export default SettingTabs;
