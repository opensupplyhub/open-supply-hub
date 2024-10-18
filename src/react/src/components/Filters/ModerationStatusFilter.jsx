import React from 'react';
import { connect } from 'react-redux';
import { bool } from 'prop-types';
import StyledSelect from './StyledSelect';
import { MODERATION_STATUSES_OPTIONS } from '../../util/constants';

const MODERATION_STATUS = 'MODERATION_STATUS';

const ModerationStatusFilter = ({ isDisabled }) => {
    console.log('ModerationStatusFilter isDisabled >>>', isDisabled);

    return (
        <div className="form__field">
            <StyledSelect
                label="Moderation Status"
                name={MODERATION_STATUS}
                options={MODERATION_STATUSES_OPTIONS || []}
                // value={countries}
                // onChange={updateCountry}
                // disabled={fetching}
                isDisabled={isDisabled}
            />
        </div>
    );
};

ModerationStatusFilter.defaultProps = {
    isDisabled: false,
};

ModerationStatusFilter.propTypes = {
    isDisabled: bool,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ModerationStatusFilter);
