import React from 'react';

const blockStyle = Object.freeze({
    margin: 0,
    display: 'block',
});

const renderUniqueListItems = (fieldValue, fieldName = '') => {
    if (!Array.isArray(fieldValue)) {
        return fieldValue;
    }

    const uniqueValues = [...new Set(fieldValue)];

    return uniqueValues.map(value =>
        fieldName === 'parent_company_os_id' ? (
            <a
                href={`/facilities/${value}`}
                key={value}
                style={blockStyle}
                target="_blank"
                rel="noopener noreferrer"
            >
                {value}
            </a>
        ) : (
            <span style={blockStyle} key={value}>
                {value}
            </span>
        ),
    );
};

export default renderUniqueListItems;
