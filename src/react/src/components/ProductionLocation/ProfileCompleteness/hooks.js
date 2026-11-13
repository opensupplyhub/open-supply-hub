import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import apiRequest from '../../../util/apiRequest';
import { makeGetProfileCompletenessURL } from '../../../util/util';

/*
Loads the profile completeness preview for a production location.

The endpoint answers 404 to everyone the show_profile_completeness flag is
not on for, so anything but a successful response means "show nothing".
Signed-out visitors can never see it, so no request is made for them.
*/
const useProfileCompleteness = (osId, { skip = false } = {}) => {
    const isSignedIn = useSelector(
        ({ auth }) => !!auth?.user?.user && !auth.user.user.isAnon,
    );
    const [profileCompleteness, setProfileCompleteness] = useState(null);

    useEffect(() => {
        setProfileCompleteness(null);

        if (!osId || !isSignedIn || skip) {
            return undefined;
        }

        let isCurrent = true;
        apiRequest
            .get(makeGetProfileCompletenessURL(osId))
            .then(({ data }) => {
                if (isCurrent) {
                    setProfileCompleteness(data);
                }
            })
            .catch(() => {});

        return () => {
            isCurrent = false;
        };
    }, [osId, isSignedIn, skip]);

    return profileCompleteness;
};

export default useProfileCompleteness;
