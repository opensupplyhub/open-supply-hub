import React from 'react';
import StyledSelect from './StyledSelect';

const RECORD_TYPE = 'RECORD_TYPE';
const RecordTypeFilter = props => {
    console.log('RecordTypeFilter props >>>', props);
    const recordTypes = [
        {
            label: 'Claim',
            value: 'Claim',
        },
        {
            label: 'Single',
            value: 'Single',
        },
        {
            label: 'API',
            value: 'API',
        },
    ];

    return (
        <div className="form__field">
            <StyledSelect
                label="Record Type"
                name={RECORD_TYPE}
                options={recordTypes || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                // isDisabled={isDisabled}
            />
        </div>
    );
};

export default RecordTypeFilter;
