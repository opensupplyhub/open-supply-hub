import React from 'react';

const blockStyle = Object.freeze({
    margin: 0,
    display: 'block',
});

const renderUniqueListItems = (
    fieldValue,
    fieldName = '',
    { preserveOrder = false } = {},
) => {
    if (!Array.isArray(fieldValue)) {
        return fieldValue;
    }

    const values = preserveOrder ? fieldValue : [...new Set(fieldValue)];

    return values.map(value =>
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
