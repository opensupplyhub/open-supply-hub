import React from 'react';
import { Link } from 'react-router-dom';

const blockStyle = Object.freeze({
    margin: 0,
    display: 'block',
});

const formatIfListAndRemoveDuplicates = (value, fieldName = '') => {
    if (!Array.isArray(value)) {
        return value;
    }

    const uniqueValues = [...new Set(value)];

    return uniqueValues.map(v =>
        fieldName === 'parent_company_os_id' ? (
            <Link
                to={`/facilities/${v}`}
                key={v}
                style={blockStyle}
                target="_blank"
                rel="noopener noreferrer"
            >
                {v}
            </Link>
        ) : (
            <span style={blockStyle} key={v}>
                {v}
            </span>
        ),
    );
};

export default formatIfListAndRemoveDuplicates;
