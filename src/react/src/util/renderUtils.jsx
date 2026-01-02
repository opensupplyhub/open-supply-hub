import React from 'react';
import Divider from '@material-ui/core/Divider';

/**
 * Sentinel token inserted into ISIC value arrays to trigger divider rendering.
 * Assumes ISIC data never contains this exact value; double-underscores reduce
 * collision risk.
 */
export const CONTRIBUTION_DATA_DIVIDER = '__CONTRIBUTION_DATA_DIVIDER__';

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

    let keySeq = 0;

    return values.map(value => {
        keySeq += 1;
        const key = `${fieldName}-${keySeq}`;

        if (fieldName === 'isic_4' && value === CONTRIBUTION_DATA_DIVIDER) {
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
