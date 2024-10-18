import React from 'react';
import { connect } from 'react-redux';
import { bool } from 'prop-types';
import StyledSelect from './StyledSelect';
import { MATCH_STATUSES_OPTIONS } from '../../util/constants';

const MATCH_STATUS = 'MATCH_STATUS';

const MatchStatusFilter = ({ isDisabled }) => {
    console.log('MatchStatusFilter isDisabled >>>', isDisabled);

    return (
        <div className="form__field">
            <StyledSelect
                label="Match Status"
                name={MATCH_STATUS}
                options={MATCH_STATUSES_OPTIONS || []}
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
};

MatchStatusFilter.propTypes = {
    isDisabled: bool,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(mapStateToProps, mapDispatchToProps)(MatchStatusFilter);
