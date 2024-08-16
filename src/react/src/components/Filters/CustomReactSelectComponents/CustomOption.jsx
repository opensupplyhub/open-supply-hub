import React from 'react';
import { components } from 'react-select';

const CustomOption = props => {
    const { data, selectProps } = props;
    const { expandedGroups } = selectProps;
    const isVisible = expandedGroups.some(group => data.groupLabel === group);

    return isVisible ? <components.Option {...props} /> : null;
};

export default CustomOption;
