import React from 'react';
import StyledSelect from './StyledSelect';

const MATCH_STATUS = 'MATCH_STATUS';

const MatchStatusFilter = props => {
    console.log('MatchStatusFilter props >>>', props);
    const statuses = [
        {
            label: 'Matched',
            value: 'Matched',
        },
        {
            label: 'New Location',
            value: 'New Location',
        },
        {
            label: 'Potential Match',
            value: 'Potential Match',
        },
    ];

    return (
        <div className="form__field">
            <StyledSelect
                label="Match Status"
                name={MATCH_STATUS}
                options={statuses || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                // isDisabled={isDisabled}
            />
        </div>
    );
};

export default MatchStatusFilter;
