import React from 'react';
import { connect } from 'react-redux';
import { bool, arrayOf, shape, string } from 'prop-types';
import StyledSelect from './StyledSelect';

const MATCH_STATUS = 'MATCH_STATUS';

const MatchStatusFilter = ({
    isDisabled,
    matchStatusesOptions,
    fetchingMatchStatuses,
}) => {
    console.log('MatchStatusFilter isDisabled >>>', isDisabled);
    console.log(
        'MatchStatusFilter matchStatusesOptions >>>',
        matchStatusesOptions,
    );
    console.log(
        'MatchStatusFilter fetchingMatchStatuses >>>',
        fetchingMatchStatuses,
    );

    return (
        <div className="form__field">
            <StyledSelect
                label="Match Status"
                name={MATCH_STATUS}
                options={matchStatusesOptions || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                // isDisabled={isDisabled}
            />
        </div>
    );
};

MatchStatusFilter.defaultProps = {
    isDisabled: false,
    matchStatusesOptions: null,
};

MatchStatusFilter.propTypes = {
    isDisabled: bool,
    matchStatusesOptions: arrayOf(
        shape({
            value: string.isRequired,
            label: string.isRequired,
        }),
    ),
};

const mapStateToProps = ({
    filterOptions: {
        matchStatuses: {
            data: matchStatusesOptions,
            fetching: fetchingMatchStatuses,
        },
    },
}) => ({
    matchStatusesOptions,
    fetchingMatchStatuses,
});

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(MatchStatusFilter);
