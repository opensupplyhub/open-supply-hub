import React from 'react';
import { bool } from 'prop-types';

import COLOURS from '../../../util/COLOURS';

const noteStyle = Object.freeze({
    display: 'block',
    fontSize: '14px',
    color: COLOURS.DARK_SLATE_GREY,
});

/*
 * The claimant's choice of whether a claimed value (company phone or
 * website) is shown on the production location profile (OSDEV-2680),
 * as a secondary line under that value in the moderator claim views.
 */
const ProfileVisibilityNote = ({ isPubliclyVisible }) => (
    <span style={noteStyle}>
        {isPubliclyVisible ? 'Shown on profile' : 'Not shown on profile'}
    </span>
);

ProfileVisibilityNote.propTypes = {
    isPubliclyVisible: bool,
};

ProfileVisibilityNote.defaultProps = {
    isPubliclyVisible: false,
};

export default ProfileVisibilityNote;
