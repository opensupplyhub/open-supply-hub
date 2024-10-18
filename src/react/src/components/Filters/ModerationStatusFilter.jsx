import React from 'react';
import { connect } from 'react-redux';
import { bool, string } from 'prop-types';
import StyledSelect from './StyledSelect';
import { MODERATION_STATUSES_OPTIONS } from '../../util/constants';

const MODERATION_STATUS = 'MODERATION_STATUS';

const ModerationStatusFilter = ({ isDisabled, className }) => {
    console.log('ModerationStatusFilter isDisabled >>>', isDisabled);

    return (
        <div className={className}>
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
    className: 'form__field',
};

ModerationStatusFilter.propTypes = {
    isDisabled: bool,
    className: string,
};

const mapStateToProps = () => {};

const mapDispatchToProps = () => {};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ModerationStatusFilter);
