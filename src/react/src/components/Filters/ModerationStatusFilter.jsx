import React from 'react';
import StyledSelect from './StyledSelect';

const MODERATION_STATUS = 'MODERATION_STATUS';
const moderationStatuses = [
    {
        label: 'Pending',
        value: 'Pending',
    },
    {
        label: 'Approved',
        value: 'Approved',
    },
    {
        label: 'Rejected',
        value: 'Rejected',
    },
    {
        label: 'Revoked',
        value: 'Revoked',
    },
];
const ModerationStatusFilter = props => {
    console.log('ModerationStatusFilter props >>>', props);

    return (
        <div className="form__field">
            <StyledSelect
                label="Moderation Status"
                name={MODERATION_STATUS}
                options={moderationStatuses || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                // isDisabled={isDisabled}
            />
        </div>
    );
};

export default ModerationStatusFilter;
