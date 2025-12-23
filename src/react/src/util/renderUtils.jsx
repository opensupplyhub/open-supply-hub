import React from 'react';
import Divider from '@material-ui/core/Divider';

export const ISIC_DIVIDER = '__ISIC_DIVIDER__';

const blockStyle = Object.freeze({
    margin: 0,
    display: 'block',
});

const dividerStyle = Object.freeze({
    margin: '10px 0',
});

const renderUniqueListItems = (
    fieldValue,
    fieldName = '',
    { preserveOrder = false } = {},
) => {
    if (!Array.isArray(fieldValue)) {
        return fieldValue;
    }

    if (fieldValue.length > 0 && React.isValidElement(fieldValue[0])) {
        return fieldValue;
    }

    const shouldPreserveOrder = preserveOrder || fieldName === 'isic_4';

    const values = shouldPreserveOrder ? fieldValue : [...new Set(fieldValue)];

    const valueCounts = new Map();

    return values.map(value => {
        const count = (valueCounts.get(value) || 0) + 1;
        valueCounts.set(value, count);
        const key = `${fieldName}-${value}-${count}`;

        if (fieldName === 'isic_4' && value === ISIC_DIVIDER) {
            return <Divider key={key} style={dividerStyle} />;
        }

        if (fieldName === 'parent_company_os_id') {
            return (
                <a
                    href={`/facilities/${value}`}
                    key={key}
                    style={blockStyle}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    {value}
                </a>
            );
        }

        return (
            <span style={blockStyle} key={key}>
                {value}
            </span>
        );
    });
};

export default renderUniqueListItems;
